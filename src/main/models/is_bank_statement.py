from pydantic import BaseModel, Field
from typing import Optional

class IsBankStatement(BaseModel):
    """Model for determining if a document is a bank statement"""
    is_bank_statement: bool = Field(description="Whether the document is a bank statement")
    reason: Optional[str] = Field(None, description="Reason for the determination")