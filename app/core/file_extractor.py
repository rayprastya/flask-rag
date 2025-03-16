from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from typing import List, Optional

def load_pdf(file_path: str) -> str:
    """
    Reads the text content from a PDF file and returns it as a single string.

    Parameters:
    - file_path (str): The file path to the PDF file.

    Returns:
    - str: The concatenated text content of all pages in the PDF.
    """
    # Logic to read pdf
    reader = PdfReader(file_path)

    # Loop over each page and store it in a variable
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n\n"

    # Clean up the text
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize line breaks
    
    return text.strip()

def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Splits text into semantically meaningful chunks using LangChain's RecursiveCharacterTextSplitter.
    
    Parameters:
    - text (str): The input text to be split
    - chunk_size (int): Maximum size of each text chunk
    - chunk_overlap (int): Number of characters to overlap between chunks
    
    Returns:
    - List[str]: List of text chunks
    """
    # Create text splitter with optimized settings
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        is_separator_regex=False
    )
    
    # Split text into chunks
    chunks = text_splitter.split_text(text)
    
    # Post-process chunks
    processed_chunks = []
    for chunk in chunks:
        # Clean up chunk
        chunk = chunk.strip()
        if not chunk:  # Skip empty chunks
            continue
            
        # Ensure chunk ends with proper punctuation
        if not chunk[-1] in '.!?':
            chunk += '.'
            
        processed_chunks.append(chunk)
    
    return processed_chunks
