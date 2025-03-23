#!/usr/bin/env python3
"""
Business Information Extraction and Validation

This module handles extracting and validating business information from bank statements.
"""

from src.main.llms import get_openai_client
from src.main.models.business_info import Address, BusinessInfo
from src.main.prompts.business_info import BUSINESS_INFO_PROMPT
import sys
from pathlib import Path
from typing import Optional, Tuple
import re
from pydantic import BaseModel

# Add the src directory to the Python path
src_path = str(Path(__file__).resolve().parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)



def validate_business_name(name: str) -> Tuple[bool, str]:
    """
    Validate that a business name is reasonable.

    Args:
        name: The business name to validate

    Returns:
        Tuple of (is_valid, reason_if_invalid)
    """
    # Check if name is empty or just whitespace
    if not name or name.strip() == "":
        return False, "Business name is empty"

    # Check if name is too short
    if len(name.strip()) < 2:
        return False, "Business name is too short"

    # Check if name is too long (most business names aren't longer than 100
    # chars)
    if len(name.strip()) > 100:
        return False, "Business name is unreasonably long"

    # Check for nonsensical patterns (like all numbers or special characters)
    if re.match(r'^[\d\W_]+$', name.strip()):
        return False, "Business name contains only numbers or special characters"

    # Check for common bank names that might have been extracted incorrectly
    common_banks = [
        "bank of america", "chase", "wells fargo", "citibank", "capital one",
        "jpmorgan", "us bank", "pnc bank", "td bank", "bank", "credit union",
        "first national", "regions bank", "suntrust", "bbt", "fifth third",
        "citizens bank", "key bank", "huntington", "santander", "ally bank"
    ]

    if any(bank.lower() in name.lower() for bank in common_banks):
        return False, "Extracted name appears to be a bank name, not a business name"

    return True, ""


def validate_address(address: Address) -> Tuple[bool, str]:
    """
    Validate that an address is reasonable.

    Args:
        address: The address to validate

    Returns:
        Tuple of (is_valid, reason_if_invalid)
    """
    address_str = str(address)
    # Check if address is empty or just whitespace
    if not address_str or address_str == "":
        return False, "Address is empty"

    # Check if address is too short
    if len(address_str) < 5:
        return False, "Address is too short"

    # Check if address is too long
    if len(address_str) > 200:
        return False, "Address is unreasonably long"

    # Check for some address-like patterns (numbers, street names, etc.)
    has_number = bool(re.search(r'\d', address_str))

    # More comprehensive list of address terms
    address_terms = [
        'street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr',
        'lane', 'ln', 'blvd', 'boulevard', 'way', 'court', 'ct', 'circle', 'cir',
        'terrace', 'ter', 'place', 'pl', 'highway', 'hwy', 'parkway', 'pkwy',
        'suite', 'ste', 'unit', 'apt', 'apartment', 'floor', 'fl'
    ]

    has_common_terms = any(term in address_str.lower()
                           for term in address_terms)

    # Check for state abbreviations or names
    states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
        'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
        'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
        'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
        'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
        'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
        'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
        'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
        'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
        'West Virginia', 'Wisconsin', 'Wyoming'
    ]

    has_state = any(
        f" {state.lower()} " in f" {address_str.lower()} " for state in states)

    # Check for ZIP code pattern
    has_zip = bool(re.search(r'\b\d{5}(?:-\d{4})?\b', address_str))

    # Check for common bank address indicators
    bank_address_indicators = [
        "branch location", "atm location", "bank address", "branch address",
        "bank headquarters", "corporate headquarters", "main office"
    ]

    is_bank_address = any(indicator.lower() in address_str.lower()
                          for indicator in bank_address_indicators)

    if is_bank_address:
        return False, "Address appears to be a bank address, not a business address"

    # Address should have a number and either common terms, state, or ZIP
    if not has_number:
        return False, "Address doesn't contain any numbers"

    if not (has_common_terms or has_state or has_zip):
        return False, "Address doesn't appear to contain standard address elements"

    return True, ""


def format_address(address: Address) -> Address:
    """
    Format an address to title case and standardize formatting.

    Args:
        address: The address to format

    Returns:
        Formatted address
    """
    address.city = address.city.title()
    address.state = address.state.upper()
    address.zip = address.zip.upper()
    address.country = address.country.upper()
    address.street = address.street.title()
    return address


def extract_zip_code(address: str) -> str:
    """
    Extract and validate ZIP code from an address.

    Args:
        address: The address to extract ZIP code from

    Returns:
        ZIP code if found, empty string otherwise
    """
    # Look for 5-digit ZIP code
    zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b', address)
    if zip_match:
        return zip_match.group(0)
    return ""


class BusinessInfoResult(BaseModel):
    """
    Pydantic model to represent validated business information.
    """
    name: Optional[str] = None
    name_valid: Optional[bool] = None
    name_validation_message: Optional[str] = None
    address: Optional[Address] = None
    address_valid: Optional[bool] = None
    address_validation_message: Optional[str] = None
    zip_code: Optional[str] = None

    def is_valid(self) -> bool:
        return self.name_valid and self.address_valid

    def __repr__(self) -> str:
        return (
            f"BusinessInfoResult(name='{self.name}', name_valid={self.name_valid}, "
            f"address='{self.address}', address_valid={self.address_valid}, "
            f"zip_code='{self.zip_code}', is_valid={self.is_valid})"
        )


def check_business_info(text: str) -> BusinessInfoResult:
    """
    Extract and validate business information from text.

    Args:
        text: The text to extract business information from

    Returns:
        BusinessInfoResult object with business information and validation results
    """
    # Extract business info using LLM
    business_info_response: BusinessInfo = get_openai_client().beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": str(
                BUSINESS_INFO_PROMPT.invoke({"text": text}))},
        ],
        response_format=BusinessInfo,
    ).choices[0].message.parsed

    # Validate business name
    name_valid, name_reason = validate_business_name(
        business_info_response.name)

    # Validate address
    address_valid, address_reason = validate_address(
        business_info_response.address)

    # Format address if valid
    formatted_address = format_address(
        business_info_response.address) if address_valid else business_info_response.address

    return BusinessInfoResult(
        name=business_info_response.name.strip(),
        name_valid=name_valid,
        name_validation_message=name_reason if name_valid is False else None,
        address=formatted_address,
        address_valid=address_valid,
        address_validation_message=address_reason if address_valid is False else None,
        zip_code=formatted_address.zip if formatted_address else None,
    )
