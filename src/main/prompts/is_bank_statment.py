from langchain_core.prompts import PromptTemplate

IS_PROMPT_STATEMENT_PROMPT = PromptTemplate.from_template("""
    Analyze this document text and determine if it is a business bank statement.
    
    Your response must follow this exact format:
    - First line: Either "YES" or "NO" (indicating if it is a bank statement)
    - Second line: A brief explanation of your determination
    
    If it is a bank statement, explain what evidence led to this conclusion.
    If it is NOT a bank statement, explain what type of document it appears to be instead.
    
    Document text: {text}
    """) 