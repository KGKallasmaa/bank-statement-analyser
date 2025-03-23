#!/usr/bin/env python3
"""
MVP Bank Statement Analyzer

This script analyzes PDF bank statements to:
1. Verify if the document is a bank statement
2. Extract business name and address
3. The net change in account balance according to the transactions and whether or not this reconciles with the balances present on the document
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = str(Path(__file__).resolve().parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from main.models.business_info import BusinessInfo
from main.models.balance_analysis import BalanceAnalysis, PageTransactions, Transaction
from main.models.is_bank_statement import IsBankStatement
from main.prompts.business_info import BUSINESS_INFO_PROMPT
from main.prompts.is_bank_statment import IS_PROMPT_STATEMENT_PROMPT
from main.prompts.balance_analysis import BALANCE_ANALYSIS_PROMPT
from main.prompts.transaction_extraction import TRANSACTION_EXTRACTION_PROMPT
from dotenv import load_dotenv
import os
from typing import List

# Import utility functions
from main.llms import get_openai_client
from main.utils import get_pdf_metadata, convert_to_markdown, sum_moneys, extract_pdf_pages_as_markdown, get_first_page_as_markdown





def analyze_bank_statement(pdf_path:str):
    """
    Analyze a PDF to determine if it's a bank statement and extract key information.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        dict: Analysis results
    """
    # Convert first page of PDF to markdown for initial checks
    first_page_md = get_first_page_as_markdown(str(pdf_path))
    print(f"Successfully converted first page to markdown text ({len(first_page_md)} characters)")
    
    # Step 1: Determine if it's a bank statement (using only first page)
    is_statement_response = get_openai_client().beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "user", "content": str(IS_PROMPT_STATEMENT_PROMPT.invoke({"text": first_page_md}))},
            ],
            response_format=IsBankStatement,
        ).choices[0].message.parsed    
    # If not a bank statement, return early with analysis
    if not is_statement_response.is_bank_statement:
        return {
            "is_bank_statement": False,
            "reason": is_statement_response.reason
        }
    

    # Step 2: Extract business name and address
    business_info_response = get_openai_client().beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "user", "content": str(BUSINESS_INFO_PROMPT.invoke({"text": first_page_md}))},
            ],
            response_format=BusinessInfo,
        ).choices[0].message.parsed

    if len(business_info_response.name.strip()) == 0 and len(business_info_response.address.strip()) == 0:
        return {
            "is_bank_statement": False,
            "reason": "No business name or address found"
        }
    
    # Step 3: Extract starting and ending balances
    balance_info_response = get_openai_client().beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "user", "content": str(BALANCE_ANALYSIS_PROMPT.invoke({"text": first_page_md}))},
            ],
            response_format=BalanceAnalysis,
        ).choices[0].message.parsed
    
    # Step 4: Extract transactions page by page
    pages_md = extract_pdf_pages_as_markdown(pdf_path)
    all_transactions = []
    
    for i, page_md in enumerate(pages_md):
        print(f"Extracting transactions from page {i+1}/{len(pages_md)}...")
        page_transactions = get_openai_client().beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "user", "content": str(TRANSACTION_EXTRACTION_PROMPT.invoke({"text": page_md}))},
            ],
            response_format=PageTransactions,
        ).choices[0].message.parsed
        all_transactions.extend(page_transactions.transactions)
    
    # Calculate totals
    for t in all_transactions:
        print(t)
        print(t.money)
    deposits = [t for t in all_transactions if t.money.amount > 0]
    withdrawals = [t for t in all_transactions if t.money.amount < 0]
    
    total_deposits = sum_moneys([t.money for t in deposits])
    total_withdrawals = sum_moneys([t.money for t in withdrawals])
    
    # Calculate net change from transactions
    net_change = sum_moneys([t.money for t in all_transactions])
    
    # Calculate expected closing balance
    expected_closing = balance_info_response.opening_balance.amount + (net_change[0].amount if net_change else 0)
    
    # Check if balances reconcile
    difference = round(abs(expected_closing - balance_info_response.closing_balance.amount),3)
    reconciles = difference < 0.01
    
    # Return complete analysis
    return {
        "is_bank_statement": True,
        "business_info": {
            "name": business_info_response.name,
            "address": business_info_response.address
        },
        "balance_analysis": {
            "opening_balance": f"{balance_info_response.opening_balance.amount} {balance_info_response.opening_balance.currency} ({balance_info_response.opening_date})",
            "closing_balance": f"{balance_info_response.closing_balance.amount} {balance_info_response.closing_balance.currency} ({balance_info_response.closing_date})",
            "total_deposits": f"{total_deposits[0].amount if total_deposits else 0} {balance_info_response.opening_balance.currency}",
            "total_withdrawals": f"{total_withdrawals[0].amount if total_withdrawals else 0} {balance_info_response.opening_balance.currency}",
            "net_change": f"{net_change[0].amount if net_change else 0} {balance_info_response.opening_balance.currency}",
            "expected_closing_balance": f"{expected_closing} {balance_info_response.opening_balance.currency}",
            "reconciles": "YES" if reconciles else "NO",
            "discrepancy_reason": f'"Calculated balance doesn\'t match reported closing balance. Difference: {difference}"' if not reconciles else None,
            "transactions_count": len(all_transactions)
        },
        "transactions": [t.dict() for t in all_transactions]
    }


def main():
    load_dotenv()
    
    # Verify OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python mvp.py <pdf_file_path>")
        sys.exit(1)
    
    # Get PDF file path and verify it exists
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: File '{pdf_path}' does not exist")
        sys.exit(1)

    # Get and display PDF metadata
    print("\nPDF Metadata:")
    metadata = get_pdf_metadata(pdf_path)
    for key, value in metadata.items():
        print(f"{key}: {value}")
    
    # Analyze the bank statement
    print("\nAnalyzing document...")
    results = analyze_bank_statement(pdf_path)
    
    # Display results
    print("\n=== ANALYSIS RESULTS ===")
    
    if results["is_bank_statement"]:
        print("✅ Document is a bank statement")
        
        print("\nBusiness Information:")
        print(f"Name: {results['business_info']['name']}")
        print(f"Address: {results['business_info']['address']}")
        
        print("\nBalance Analysis:")
        if isinstance(results["balance_analysis"], str):
            # For image-based analysis that returns a string
            print(results["balance_analysis"])
        else:
            # For structured analysis
            balance = results["balance_analysis"]
            print(f"OPENING BALANCE: {balance['opening_balance']}")
            print(f"CLOSING BALANCE: {balance['closing_balance']}")
            print(f"TOTAL DEPOSITS: {balance['total_deposits']}")
            print(f"TOTAL WITHDRAWALS: {balance['total_withdrawals']}")
            print(f"NET CHANGE: {balance['net_change']}")
            print(f"EXPECTED CLOSING BALANCE: {balance['expected_closing_balance']}")
            print(f"RECONCILES: {balance['reconciles']}")
            if balance.get('discrepancy_reason'):
                print(f"DISCREPANCY REASON: {balance['discrepancy_reason']}")
        
        # Display transaction summary
        if "transactions" in results and results["transactions"]:
            print(f"\nTransactions: {len(results['transactions'])} found")
            print("Sample transactions:")
            # Show first 5 transactions as a sample
            for i, tx in enumerate(results["transactions"][:5]):
                print(f"{i+1}. {tx}")
            if len(results["transactions"]) > 5:
                print(f"... and {len(results['transactions']) - 5} more transactions")
    else:
        print("❌ Document is NOT a bank statement")
        print(f"Reason: {results.get('reason', 'Unknown')}")
        if results.get("document_type"):
            print("\nDocument Analysis:")
            print(results["document_type"])
    
if __name__ == "__main__":
    main()
