from typing import List, Optional
from dotenv import load_dotenv
from main.models.balance_analysis import Money
from PyPDF2 import PdfWriter
from pathlib import Path
import os
from openai import OpenAI
import base64
from io import BytesIO
from PyPDF2 import PdfReader
from markitdown import MarkItDown

def encode_image(image):
    """Convert a PIL Image to base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_completion(prompt, images=[], model="gpt-4o"):
    """Make a request to OpenAI's API with optional image input."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
        
    client = OpenAI()
    
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    
    # Add images to the message if provided
    for img in images:
        base64_image = encode_image(img)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error making OpenAI API request: {e}")
        return None

def get_pdf_metadata(pdf_path):
    """Extract metadata from a PDF file."""
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    return   {
        "Pages": len(reader.pages),
        "Title": metadata.get("/Title", "Not available"),
        "Author": metadata.get("/Author", "Not available"),
        "Creator": metadata.get("/Creator", "Not available"),
        "Producer": metadata.get("/Producer", "Not available"),
        "Creation Date": metadata.get("/CreationDate", "Not available"),
        "Modification Date": metadata.get("/ModDate", "Not available")
    }

def convert_to_markdown(paths: Optional[List[str]]) -> List[str]:
    if not paths:
        return []
    converter = MarkItDown(llm_client=OpenAI())    
    return [converter.convert(p).text_content for p in paths]

def sum_moneys(moneys: List[Money]) -> List[Money]:
    currency_total = {}
    for money in moneys:
        if money.currency not in currency_total:
            currency_total[money.currency] = 0
        currency_total[money.currency] += money.amount
    return [Money(amount=amount, currency=currency) for currency,amount in currency_total.items()]

def extract_pdf_pages_as_markdown(pdf_path: str) -> List[str]:
    """Extract each page of a PDF as separate markdown texts."""
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)
    
    # Create a temporary directory to store individual pages
    temp_dir = Path("temp_pdf_pages")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Extract each page to a separate PDF
        page_paths = []
        for i in range(num_pages):
            
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            page_path = temp_dir / f"page_{i+1}.pdf"
            with open(page_path, "wb") as f:
                writer.write(f)
            page_paths.append(str(page_path))
        
        # Convert each page to markdown
        converter = MarkItDown(llm_client=OpenAI())
        return [converter.convert(p).text_content for p in page_paths]
    
    finally:
        # Clean up temporary files
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def get_first_page_as_markdown(pdf_path: str) -> str:
    """Extract only the first page of a PDF as markdown text."""
    reader = PdfReader(pdf_path)
    if len(reader.pages) == 0:
        return ""
    
    # Create a temporary directory
    temp_dir = Path("temp_pdf_pages")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Extract first page to a separate PDF
        writer = PdfWriter()
        writer.add_page(reader.pages[0])
        page_path = temp_dir / "first_page.pdf"
        with open(page_path, "wb") as f:
            writer.write(f)
        
        # Convert to markdown
        converter = MarkItDown(llm_client=OpenAI())
        return converter.convert(str(page_path)).text_content
    
    finally:
        # Clean up temporary files
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)