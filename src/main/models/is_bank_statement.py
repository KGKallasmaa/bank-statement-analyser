from pydantic import BaseModel, Field
from typing import Optional


class IsBankStatement(BaseModel):
    """Model for determining if a document is a bank statement"""
    is_bank_statement: bool = Field(
        description="Whether the document is a bank statement")
    reason: str = Field(
        description="Reason for the determination")


class BankIdentification(BaseModel):
    """Model for identifying bank information."""
    bank_name: Optional[str] = Field(None, description="Name of the bank")
    has_bank_logo: bool = Field(description="Whether a bank logo is present")
    confidence: float = Field(
        description="Confidence score (0.0-1.0) for the bank identification")
    notes: Optional[str] = Field(
        None, description="Additional notes about the bank identification")


class CustomerIdentification(BaseModel):
    """Model for identifying customer information."""
    business_name: Optional[str] = Field(
        None, description="Name of the business")
    is_business_account: bool = Field(
        description="Whether this appears to be a business account")
    account_number: Optional[str] = Field(
        None, description="Account number (if visible)")
    confidence: float = Field(
        description="Confidence score (0.0-1.0) for the customer identification")
    notes: Optional[str] = Field(
        None, description="Additional notes about the customer identification")


class StatementValidation(BaseModel):
    """Model for validating the type of bank statement."""
    is_business_statement: bool = Field(
        description="Whether this is a business bank statement")
    is_personal_statement: bool = Field(
        description="Whether this is a personal bank statement")
    confidence: float = Field(
        description="Confidence score (0.0-1.0) for the determination")
    reason: str = Field(description="Reasoning for the determination")
