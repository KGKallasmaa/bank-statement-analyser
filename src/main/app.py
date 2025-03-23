#!/usr/bin/env python3
"""
MVP Bank Statement Analyzer

This script analyzes PDF bank statements to:
1. Verify if the document is a bank statement
2. Extract business name and address
3. The net change in account balance according to the transactions and whether or not this reconciles with the balances present on the document
"""
from pathlib import Path
import sys

# Debug: Print the current Python path
print("Python sys.path:")
for p in sys.path:
    print(f"  - {p}")

# Add the root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional
from src.main.models.balance_analysis import BalanceAnalysis, Transaction
from src.main.prompts.balance_analysis import BALANCE_ANALYSIS_PROMPT
from dotenv import load_dotenv
from src.main.transaction_extraction import extract_transactions
from src.main.balance_reconciliation import reconcile_balances
from src.main.llms import get_openai_client
from src.main.utils import get_pdf_metadata, get_first_page_as_markdown
from src.main.is_bank_statement import check_is_business_bank_statement
from src.main.business_info import check_business_info
from src.main.integrity import check_document_integrity
from src.main.models.business_info import BusinessInfo
from pathlib import Path
import os
from pydantic import BaseModel


class AnalysisResult(BaseModel):
    is_bank_statement: Optional[bool] = None
    is_valid_business_info: Optional[bool] = None
    is_valid_balance_analysis: Optional[bool] = None
    reason: Optional[str] = None
    business_info: Optional[BusinessInfo] = None
    balance_analysis: Optional[BalanceAnalysis] = None
    transactions: Optional[List[Transaction]] = None

    def is_valid(self) -> bool:
        return self.is_bank_statement and self.is_valid_business_info and self.is_valid_balance_analysis


# Constants
MAX_FILE_SIZE_MB = 50  # Maximum PDF file size in MB
# Maximum number of transactions (2000/month * 12 months * 10 years)
MAX_TRANSACTIONS = 24000


def _validate_pdf_file(pdf_path: str) -> bool:
    """
    Validate that the file exists, is a PDF, and is not too large.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        bool: True if valid, False otherwise
    """
    path = Path(pdf_path)

    # Check if file exists
    if not path.exists():
        print(f"Error: File '{path}' does not exist")
        return False

    # Check if file is a PDF
    if path.suffix.lower() != '.pdf':
        print(f"Error: File '{path}' is not a PDF file")
        return False

    # Check file size
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        print(
            f"Error: File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({MAX_FILE_SIZE_MB} MB)")
        return False

    return True


def analyze_bank_statement(pdf_path: str) -> AnalysisResult:
    """
    Analyze a PDF to determine if it's a bank statement and extract key information.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        dict: Analysis results
    """
    # Convert first page of PDF to markdown for initial checks
    first_page_md = get_first_page_as_markdown(str(pdf_path))
    print(
        f"Successfully converted first page to markdown text ({len(first_page_md)} characters)")

    # Step 1: Determine if it's a bank statement (using only first page)
    statement_check = check_is_business_bank_statement(first_page_md)
    if not statement_check.is_bank_statement:
        return AnalysisResult(
            is_bank_statement=False,
            reason=statement_check.reason
        )

    # Step 2: Extract and validate business name and address
    business_info = check_business_info(first_page_md)

    if not business_info.is_valid:
        return AnalysisResult(
            is_valid_business_info=False,
            reason=f"Invalid business information: {business_info.name_validation_message or business_info.address_validation_message}"
        )

    # Step 3: Extract starting and ending balances
    balance_info_response = get_openai_client().beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": str(
                BALANCE_ANALYSIS_PROMPT.invoke({"text": first_page_md}))},
        ],
        response_format=BalanceAnalysis,
    ).choices[0].message.parsed

    # Step 4: Extract transactions page by page
    try:
        all_transactions = extract_transactions(pdf_path)
    except ValueError as e:
        return AnalysisResult(
            is_bank_statement=False,
            reason=str(e)
        )
    # Use the balance reconciliation module to calculate totals and check if
    # balances reconcile
    balance_analysis = reconcile_balances(
        balance_info_response, all_transactions)

    if not balance_analysis.is_valid():
        return AnalysisResult(
            is_valid_balance_analysis=False,
            reason=balance_analysis.discrepancy_reason
        )

    # Return complete analysis
    return AnalysisResult(
        is_bank_statement=True,
        is_valid_business_info=True,
        is_valid_balance_analysis=True,
        business_info=BusinessInfo(
            name=business_info.name,
            address=business_info.address,
        ),
        balance_analysis=BalanceAnalysis(
            opening_balance=balance_info_response.opening_balance,
            opening_date=balance_info_response.opening_date,
            closing_balance=balance_info_response.closing_balance,
            closing_date=balance_info_response.closing_date,
        ),
        transactions=all_transactions
    )


def display_results(results: Dict[str, Any]) -> None:
    """
    Display the analysis results in a formatted way.

    Args:
        results: Analysis results dictionary
    """
    print("\n=== ANALYSIS RESULTS ===")
    if results.is_valid():
        print("✅ Document is a bank statement")
        print("\nBusiness Information:")
        print(f"{results.business_info}")
        print("\nBalance Analysis:")
        print(f"{results.balance_analysis}")
        print("\nTransactions:")
        print(f"{len(results.transactions)} transactions found")
        print("\nExample transactions:")
        for tx in results.transactions[:5]:
            print(f"{tx}")
    else:
        if results.is_bank_statement == False:
            print("❌ Document is not a bank statement")
            print(f"Reason: {results.reason}")
        if results.is_valid_business_info == False:
            print("❌ Business information is invalid")
            print(f"Reason: {results.reason}")
        if results.is_valid_balance_analysis == False:
            print("❌ Balance analysis is invalid")
            print(f"Reason: {results.reason}")


def main():
    """
    Main function to parse arguments and run the analysis.
    """
    load_dotenv()

    # Verify OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        sys.exit(1)

    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python mvp.py <pdf_file_path>")
        sys.exit(1)

    # Get PDF file path and validate it
    pdf_path = sys.argv[1]
    if not _validate_pdf_file(pdf_path):
        sys.exit(1)

    # Get and display PDF metadata
    print("\nPDF Metadata:")
    metadata = get_pdf_metadata(pdf_path)
    for key, value in metadata.items():
        print(f"{key}: {value}")

    print("Checking document integrity...")
    is_valid, integrity_message = check_document_integrity(pdf_path)
    if not is_valid and 5>6:
        print(f"Document integrity check failed: {integrity_message}")
        sys.exit(1)

    # Analyze the bank statement
    print("\nAnalyzing document...")
    results = analyze_bank_statement(pdf_path)

    # Display results
    display_results(results)


if __name__ == "__main__":
    main()
