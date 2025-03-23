from typing import Tuple, List
import re

from openai import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from main.utils import extract_pdf_pages
from src.main.llms import get_openai_client


class DocumentIntegrityResult(BaseModel):
    is_valid: bool
    confidence: int
    issues_detected: List[str]
    explanation: str


def check_document_integrity(pdf_path: str) -> Tuple[bool, str]:
    """
    Check the integrity of the document by verifying the number of pages and the
    presence of the first page, as well as running additional integrity checks.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Tuple of (is_valid, integrity_message)
    """
    # Run detailed integrity checks on each page
    i = 0
    for page_content in extract_pdf_pages(pdf_path):
        if i > 1000:
            return False, "Document is too long"
        is_valid, message = check_page_integrity(page_content, i)
        if not is_valid:
            return False, f"Page {i + 1} integrity issue: {message}"
        i += 1
    if i == 0:
        return False, "Document is empty"
    return True, "Document integrity check passed"


def check_page_integrity(
        page_content: str, page_number: int) -> Tuple[bool, str]:
    """
    Perform integrity checks on a single page.

    Args:
        page_content: Markdown text of the page
        page_number: Page number for reference

    Returns:
        Tuple of (is_valid, integrity_message)
    """
    # Check 1: Programmatic checks for obvious template placeholders
    if contains_template_placeholders(page_content):
        return False, "Contains template placeholders"

    # Check 2: Check for suspiciously empty content
    if is_suspiciously_empty(page_content):
        return False, "Page appears to be suspiciously empty"

    # Check 3: Use LangChain and OpenAI to analyze the page for integrity
    # issues
    ai_valid, ai_message = analyze_page_with_langchain(
        page_content, page_number)
    if not ai_valid:
        return False, ai_message

    return True, "Page integrity check passed"


def contains_template_placeholders(text: str) -> bool:
    """Check if the text contains obvious template placeholders."""
    placeholder_patterns = [
        r'\[.*?\]',                      # [Text in brackets]
        r'\{\{.*?\}\}',                  # {{Text in double curly braces}}
        r'<.*?>',                        # <Text in angle brackets>
        r'___+',                         # Underscores (3 or more)
        r'XXXX+',                        # X's (4 or more)
        r'\bN/A\b',                      # N/A
        r'\bTBD\b',                      # TBD
        r'\bPLACEHOLDER\b',              # PLACEHOLDER
        r'\bINSERT .* HERE\b'            # INSERT ... HERE
    ]

    for pattern in placeholder_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def is_suspiciously_empty(text: str) -> bool:
    """Check if the page has suspiciously little content."""
    # Remove whitespace and check content length
    cleaned_text = re.sub(r'\s+', '', text)
    return len(cleaned_text) < 50  # Arbitrary threshold


# Define the LangChain prompt template for document integrity analysis
DOCUMENT_INTEGRITY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert in document forensics and integrity verification. Your task is to analyze a bank statement page for signs of tampering, forgery, or other integrity issues.

Look for:
- Signs the text has been visibly modified or tampered with
- Indications of hidden or overlaid text
- Template placeholders or dummy data
- Inconsistencies in formatting or data
- Unusual patterns that suggest forgery

Respond with a JSON object containing:
1. "is_valid": boolean (true if the page appears legitimate, false if issues detected)
2. "confidence": number (0-100 indicating your confidence in the assessment)
3. "issues_detected": array of strings (list of specific issues found, empty if none)
4. "explanation": string (brief explanation of your determination)""",
        ),
        (
            "user",
            """Here is the text from page {page_number} of a bank statement document. Analyze it for integrity issues.

{text}""",
        ),
    ]
)


def analyze_page_with_langchain(
        page_content: str, page_number: int) -> Tuple[bool, str]:
    """
    Use LangChain and OpenAI to analyze the page for integrity issues.

    Args:
        page_content: Markdown text of the page
        page_number: Page number for reference

    Returns:
        Tuple of (is_valid, integrity_message)
    """
    response = get_openai_client().beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "user", "content": str(DOCUMENT_INTEGRITY_PROMPT.invoke(
                {"text": page_content, "page_number": page_number}))},
        ],
        response_format=DocumentIntegrityResult,
    ).choices[0].message.parsed
    if not response.is_valid:
        return False, f"AI detected issues ({response.confidence}% confidence): {response.issues_detected}. {response.explanation}"
    return True, f"AI verification passed ({response.confidence}% confidence)"
