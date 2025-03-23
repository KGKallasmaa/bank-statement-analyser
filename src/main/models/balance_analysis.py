from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Money(BaseModel):
    amount: float = Field(description="Amount of money")
    currency: str = Field(description="Currency of the money")

class Transaction(BaseModel):
    date: str
    description: str
    money: Money
    reference: Optional[str] = None


class PageTransactions(BaseModel):
    transactions: List[Transaction]

class BalanceAnalysis(BaseModel):
    """Model for bank statement balance analysis"""
    opening_balance: Money = Field(description="Opening balance amount")
    opening_date: str = Field(description="Date of the opening balance")
    closing_balance: Money = Field(description="Closing balance amount")
    closing_date: str = Field(description="Date of the closing balance")
