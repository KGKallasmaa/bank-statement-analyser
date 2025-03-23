from langchain_core.prompts import ChatPromptTemplate

BANK_INFO_CHECK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in analyzing financial documents. Your task is to check if the provided document contains bank information.

Look for:
- Bank name
- Bank logo mention
- Bank contact information
- Branch details

Respond with a JSON object containing:
1. "has_bank_info": boolean (true if bank information is present, false otherwise)
2. "bank_name": string (name of the bank if found, null otherwise)
3. "reason": string (brief explanation of your determination)""",
        ),
        (
            "user",
            """Here is the text from a document. Check if it contains bank information.

{text}""",
        ),
    ]
)

STATEMENT_PERIOD_CHECK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in analyzing financial documents. Your task is to check if the provided document contains statement period information.

Look for:
- Statement period start date
- Statement period end date
- Any mention of "statement period" or similar terms

Respond with a JSON object containing:
1. "has_statement_period": boolean (true if statement period information is present, false otherwise)
2. "period_start": string (start date if found, null otherwise)
3. "period_end": string (end date if found, null otherwise)
4. "reason": string (brief explanation of your determination)""",
        ),
        (
            "user",
            """Here is the text from a document. Check if it contains statement period information.

{text}""",
        ),
    ]
)

CUSTOMER_INFO_CHECK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in analyzing financial documents. Your task is to check if the provided document contains customer information.

Look for:
- Account holder name (individual or business)
- Account number (full or partial)
- Customer address
- Any other customer identifiers

Respond with a JSON object containing:
1. "has_customer_info": boolean (true if customer information is present, false otherwise)
2. "customer_name": string (name of the customer if found, null otherwise)
3. "account_number": string (account number if found, null otherwise)
4. "reason": string (brief explanation of your determination)""",
        ),
        (
            "user",
            """Here is the text from a document. Check if it contains customer information.

{text}""",
        ),
    ]
)

IS_PROMPT_STATEMENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in analyzing financial documents. Your task is to determine if the provided document is a bank statement or not.

Look for key indicators such as:
- Account information
- Transaction history
- Beginning and ending balances
- Bank name or logo
- Statement period dates

Your response should be clear and direct:
1. Determine if this is a bank statement (yes or no)
2. Provide a brief reason for your determination

If it is NOT a bank statement, explain what type of document it appears to be instead.""",
        ),
        (
            "user",
            """Here is the text from a document. Determine if it is a bank statement or not, with a brief reason.

{text}""",
        ),
    ]
)

BANK_IDENTIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in analyzing financial documents. Your task is to identify bank information from the provided document.

Look for:
- Bank name
- Bank logo or branding elements
- Bank contact information
- Branch details

Provide a confidence score for your identification.""",
        ),
        (
            "user",
            """Here is the text from a document. Identify the bank information.

{text}""",
        ),
    ]
)

CUSTOMER_IDENTIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in analyzing financial documents. Your task is to identify customer information from the provided document.

Look for:
- Business name
- Account holder name
- Account number (partial is fine)
- Indicators that this is a business account (e.g., "Business Checking")
- Any other customer identifiers

Determine if this appears to be a business account rather than a personal account.""",
        ),
        (
            "user",
            """Here is the text from a document. Identify the customer information.

{text}""",
        ),
    ]
)

STATEMENT_TYPE_VALIDATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in analyzing financial documents. Your task is to determine if the provided document is a business bank statement or a personal bank statement.

Look for indicators such as:
- Account type (Business Checking, Commercial Account, etc.)
- Business name as the account holder
- Business-specific transaction types
- Business account features or fees
- Any explicit mentions of "business account" or similar terms

Provide a clear determination with your reasoning and confidence level.""",
        ),
        (
            "user",
            """Here is the text from a document. Determine if it is a business bank statement or a personal bank statement.

{text}""",
        ),
    ]
)
