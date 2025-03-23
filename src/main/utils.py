from decimal import Decimal
from typing import Dict, Generator, List
from src.main.models.balance_analysis import Money
from PyPDF2 import PdfReader


def get_pdf_metadata(pdf_path):
    """Extract metadata from a PDF file."""
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    return {
        "Pages": len(reader.pages),
        "Title": metadata.get("/Title", "Not available") if metadata is not None else "Not available",
        "Author": metadata.get("/Author", "Not available") if metadata is not None else "Not available",
        "Creator": metadata.get("/Creator", "Not available") if metadata is not None else "Not available",
        "Producer": metadata.get("/Producer", "Not available") if metadata is not None else "Not available",
        "Creation Date": metadata.get("/CreationDate", "Not available") if metadata is not None else "Not available",
        "Modification Date": metadata.get("/ModDate", "Not available") if metadata is not None else "Not available"
    }


def sum_moneys(moneys: List[Money]) -> List[Money]:
    currency_total: Dict[str, Decimal] = {}
    for money in moneys:
        currency = money.currency.upper()
        current_total = currency_total.get(currency, Decimal(0))
        currency_total[currency] = current_total + Decimal(money.amount)
    return [Money(amount=float(amount), currency=currency)
            for currency, amount in currency_total.items()]


def extract_pdf_pages(pdf_path: str) -> Generator[str, None, None]:
    """Extract each page of a PDF as separate markdown texts."""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        yield page.extract_text()


def get_first_page_as_markdown(pdf_path: str) -> str:
    """Extract only the first page of a PDF as markdown text."""
    reader = PdfReader(pdf_path)
    if len(reader.pages) == 0:
        return ""
    return reader.pages[0].extract_text()
