"""
Transaction extraction module for bank statement analysis.

This module contains functions to extract transactions from bank statement pages.
"""

from typing import List
from src.main.utils import extract_pdf_pages
from src.main.llms import get_openai_client
from src.main.prompts.transaction_extraction import TRANSACTION_EXTRACTION_PROMPT
from src.main.models.balance_analysis import PageTransactions, Transaction

# Maximum number of transactions (2000/month * 12 months * 10 years)
MAX_TRANSACTIONS = 24000


def extract_transactions(pdf_path: str) -> List[Transaction]:
    """
    Extract transactions from bank statement pages.

    Args:
        pages_md: List of markdown text for each page of the bank statement

    Returns:
        List of Transaction objects
    """
    all_transactions: List[Transaction] = []
    currency = None

    i = 1
    for page in extract_pdf_pages(pdf_path):
        print(f"Extracting transactions from page {i}...")
        print(page)
        i += 1
        page_transactions = get_openai_client().beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": str(
                    TRANSACTION_EXTRACTION_PROMPT.invoke({"text": page}))},
            ],
            response_format=PageTransactions,
        ).choices[0].message.parsed
        new_transactions = page_transactions.transactions
        if currency is None:
            currency = new_transactions[0].money.currency
        else:
            for tx in new_transactions:
                if tx.money.currency != currency:
                    raise ValueError(
                        f"Transactions have different currencies: {currency} and {tx.money.currency}")
        all_transactions.extend(new_transactions)
        # Check if we've exceeded the maximum number of transactions
        if len(all_transactions) > MAX_TRANSACTIONS:
            print(
                f"Warning: Number of transactions exceeds maximum limit ({MAX_TRANSACTIONS})")
            return all_transactions[:MAX_TRANSACTIONS]

    return all_transactions
