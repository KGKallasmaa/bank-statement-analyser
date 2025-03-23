from langchain_core.prompts import PromptTemplate

BUSINESS_INFO_PROMPT = PromptTemplate.from_template("""
   Extract the following information from this bank statement in JSON format:
    1. Business name
    2. Business address
    
    Format your response as:
    BUSINESS NAME: [extracted name]
    BUSINESS ADDRESS: [extracted address]
                                                    
    Document text:{text}
    """) 