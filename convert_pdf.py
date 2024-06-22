from glob import glob
import pdfplumber
import re

def get_document_title(pdf_path):
    return re.findall('^(.+?).pdf', pdf_path)

def pdf_to_text(pdf_path, output_text_path=""):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        full_text = []
        # Iterate over each page and extract text
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # Ensure the page contains text
                full_text.append(page_text)
        # Join all text into a single string
        full_text = "\n".join(full_text)
    # Save the extracted text to a file
    output_text_path += get_document_title(pdf_path)[0] + ".txt"
    with open(output_text_path, "w", encoding="utf-8") as text_file:
        text_file.write(full_text)
    print(f"Text extracted from {pdf_path} and saved to {output_text_path}")

# Convert the PDF to text
if __name__ == "__main__":
    pdf_path = glob("*.pdf")[0]
    output_text_path = ""
    pdf_to_text(pdf_path, output_text_path)

