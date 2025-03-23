from langchain_core.prompts import ChatPromptTemplate

BALANCE_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a financial document analyzer specialized in extracting balance information from bank statements.

Your task is to extract the opening and closing balances from the provided bank statement.

Extract:
1. Opening balance - the starting balance for the statement period
2. Opening date - the date of the opening balance
3. Closing balance - the ending balance for the statement period
4. Closing date - the date of the closing balance

Return the information as a BalanceAnalysis object.
            """,
        ),
        ("human", "{text}"),
    ]
)
