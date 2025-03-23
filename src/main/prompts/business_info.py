"""
Prompts for extracting business information from bank statements.
"""

from langchain_core.prompts import PromptTemplate

BUSINESS_INFO_PROMPT = PromptTemplate.from_template(
    """You are an expert at extracting business information from bank statements.

Given the text from a bank statement, extract the BUSINESS NAME and ADDRESS of the account holder.
DO NOT extract the bank's name or the bank's address.

The business name is the name of the company or individual that owns the account.
It is typically found near the top of the statement, often labeled as "Account Holder", "Customer", "Business Name", or similar.

The address is the mailing address of the business or individual account holder, not the bank's address.
It is typically found near the business name.

IMPORTANT:
- Extract ONLY the business/account holder name, not the bank name
- Extract ONLY the business/account holder address, not the bank address
- If you cannot find a clear business name or address, return empty strings
- Do not make up or guess information that is not clearly present

Bank Statement Text:
{text}

Respond with a JSON object with the following structure:
{{
  "name": "The business name (not the bank name)",
  "address": "The business address (not the bank address)"
}}
"""
)
