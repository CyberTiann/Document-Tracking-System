import pytesseract
import re
from PIL import Image
import os
from pdfminer.high_level import extract_text, extract_pages

# Ensure pytesseract is configured correctly
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def perform_ocr(file_path):
    extracted_text = ""

    # Get the file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
        try:
            # Open the image file
            with Image.open(file_path) as img:
                # Use pytesseract to do OCR on the image
                extracted_text = pytesseract.image_to_string(img)
        except Exception as e:
            print(f"Error processing image: {e}")  # Debug print
    elif file_extension == '.pdf':
        extracted_text = perform_pdfextract(file_path)
    else:
        raise ValueError("Unsupported file type. Please provide a PDF or an image file.")

    return extracted_text

def perform_pdfextract(file_path):
    extracted_text = ""

    try:
        # Extract text from the first page only
        extracted_text = extract_text(file_path, page_numbers=[0])  # Page numbers are zero-indexed
        print(f"Extracted {len(extracted_text)} characters from the first page of the PDF.")
        
        if not extracted_text.strip():
            print("No text extracted from the first page of the PDF.")  # Debug print
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")  # Debug print

    return extracted_text

