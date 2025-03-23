#!/usr/bin/env python3
"""
Bank Statement Checker

This script checks if this document has the potential to be a bank statement
by validating essential components of a bank statement.
"""

from src.main.llms import get_openai_client
from src.main.prompts.is_bank_statment import (
    IS_PROMPT_STATEMENT_PROMPT,
    BANK_INFO_CHECK_PROMPT,
    STATEMENT_PERIOD_CHECK_PROMPT,
    CUSTOMER_INFO_CHECK_PROMPT
)
from src.main.models.is_bank_statement import IsBankStatement
import sys
from pathlib import Path

# Add the src directory to the Python path
# Go up to the root directory
src_path = str(Path(__file__).resolve().parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


# Import utility functions


def __check_bank_info(first_page_md: str) -> IsBankStatement:
    """
    Check if the document contains bank information.

    Args:
        first_page_md: Markdown text of the first page

    Returns:
        Dict with results of bank info check
    """
    return get_openai_client().beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": str(
                BANK_INFO_CHECK_PROMPT.invoke({"text": first_page_md}))},
        ],
        response_format=IsBankStatement,
    ).choices[0].message.parsed


def __check_statement_period(first_page_md: str) -> IsBankStatement:
    """
    Check if the document contains statement period information.

    Args:
        first_page_md: Markdown text of the first page

    Returns:
        Dict with results of statement period check
    """
    return get_openai_client().beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": str(
                STATEMENT_PERIOD_CHECK_PROMPT.invoke({"text": first_page_md}))},
        ],
        response_format=IsBankStatement,
    ).choices[0].message.parsed


def __check_customer_info(first_page_md: str) -> IsBankStatement:
    """
    Check if the document contains customer information.

    Args:
        first_page_md: Markdown text of the first page

    Returns:
        Dict with results of customer info check
    """
    return get_openai_client().beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": str(
                CUSTOMER_INFO_CHECK_PROMPT.invoke({"text": first_page_md}))},
        ],
        response_format=IsBankStatement,
    ).choices[0].message.parsed


def check_is_business_bank_statement(first_page_md: str) -> IsBankStatement:
    """
    Determine if the document is a bank statement by checking essential components.

    Args:
        first_page_md: Markdown text of the first page

    Returns:
        IsBankStatement: Result of bank statement validation
    """
    # Check for essential components of a bank statement
    bank_info = __check_bank_info(first_page_md)

    if not bank_info.is_bank_statement:
        return IsBankStatement(
            is_bank_statement=False,
            reason=f"No bank information found. {bank_info.reason}"
        )

    period_info = __check_statement_period(first_page_md)

    if not period_info.is_bank_statement:
        return IsBankStatement(
            is_bank_statement=False,
            reason=f"No statement period information found. {period_info.reason}"
        )

    customer_info = __check_customer_info(first_page_md)

    if not customer_info.is_bank_statement:
        return IsBankStatement(
            is_bank_statement=False,
            reason=f"No customer information found. {customer_info.reason}"
        )

    # If all essential components are present, make final determination
    return get_openai_client().beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": str(
                IS_PROMPT_STATEMENT_PROMPT.invoke({"text": first_page_md}))},
        ],
        response_format=IsBankStatement,
    ).choices[0].message.parsed
