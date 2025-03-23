from langchain_core.prompts import ChatPromptTemplate

TRANSACTION_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a financial document analyzer specialized in extracting transaction data from bank statements.
            
Your task is to extract all transactions from the provided bank statement page.

For each transaction, extract:
1. Date - in YYYY-MM-DD format
2. Description - the transaction description or payee
3. Amount - the transaction amount (positive for deposits, negative for withdrawals)
4. Currency - the currency code (USD, EUR, etc.)

Return the transactions as a list of Transaction objects.
            """,
        ),
        ("human", "{text}"),
    ]
) 