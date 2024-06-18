import fitz
import pdfplumber
import pytesseract
import os

input_dir = r'C:\Users\zxx91\Desktop\School of Cities AI\downloads\hamilton'
output_txt_file = 'hamilton\hamilton_PDF_extracted_content.txt'
count = 0

# Ensure the input directory exists
if not os.path.exists(input_dir):
    raise FileNotFoundError(f"The directory {input_dir} does not exist")

# Function to clean and truncate file names for text output
def clean_and_truncate_filename(filename, max_length=100):
    clean_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '_')).rstrip()
    return clean_filename[:max_length]

# Open the output text file in write mode
with open(output_txt_file, 'w', encoding='utf-8') as output_file:
    # Iterate over each PDF file in the directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            print(f"Processing file: {pdf_path}")  # Debugging statement
            
            # Open the PDF file
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            pdf_text += text + "\n"
                    
                    # Clean and truncate filename for writing to the text output
                    clean_filename = clean_and_truncate_filename(filename)
                    
                    # Write the extracted text to the output file
                    output_file.write(f"Content from {clean_filename}:\n")
                    output_file.write(pdf_text)
                    output_file.write("\n\n\n")  # Add at least three lines of space between contents
                    print(f"Extracted text from {filename}")
                    count += 1
                    print(count)
            except Exception as e:
                print(f"Failed to process file: {pdf_path}, Error: {e}")
                continue

print(f"All PDF text content has been extracted and saved to {output_txt_file}")