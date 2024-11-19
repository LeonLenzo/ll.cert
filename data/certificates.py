import os
import re
import pandas as pd
from PyPDF2 import PdfReader

def extract_data_from_pdf(pdf_path):
    """
    Extract data (Name, Certificate Number, Date of Issue, Course Codes) from a single PDF.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # Debug: Print raw text (optional, can be commented out)
        #print(f"Raw text from {os.path.basename(pdf_path)}:\n{text[:500]}")

        # Define regex patterns for the desired fields
        name_pattern = r"This is a statement that:\s*(.+)"
        cert_number_pattern = r"Certificate Number:\s*(\S+)"
        date_pattern = r"Date of Issue:\s*(\d{1,2}-\w{3}-\d{2})"
        course_code_pattern = r"(RII[A-Z]+\d+[A-Z]?)"

        # Extract fields with debugging
        name = re.search(name_pattern, text)
        print(f"Name match: {name.group(1).strip() if name else 'None'}")
        cert_number = re.search(cert_number_pattern, text)
        print(f"Certificate Number match: {cert_number.group(1).strip() if cert_number else 'None'}")
        date_of_issue = re.search(date_pattern, text)
        print(f"Date of Issue match: {date_of_issue.group(1).strip() if date_of_issue else 'None'}")
        course_codes = re.findall(course_code_pattern, text)
        print(f"Course Codes match: {course_codes}")

        # Extracted values
        name = name.group(1).strip() if name else None
        cert_number = cert_number.group(1).strip() if cert_number else None
        date_of_issue = date_of_issue.group(1).strip() if date_of_issue else None

        # Create a list of rows for each course code
        rows = []
        for course_code in course_codes:
            rows.append({
                "Name": name,
                "Certificate Number": cert_number,
                "Date of Issue": date_of_issue,
                "Course Code": course_code
            })

        return rows
    except Exception as e:
        print(f"Error processing file {os.path.basename(pdf_path)}: {e}")
        return []

def compile_pdf_data(directory):
    """
    Compile data from all PDFs in a directory, logging extracted rows for each file.
    """
    all_rows = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)
            print(f"Processing file: {filename}")
            rows = extract_data_from_pdf(pdf_path)
            print(f"Extracted {len(rows)} rows from file: {filename}")
            all_rows.extend(rows)
    
    return pd.DataFrame(all_rows)

def cross_reference_data(pdf_data, contact_data):
    """
    Cross-reference PDF data with a CSV containing contact information.
    Ensures all rows from PDF data are retained, even if there's no match in contact data.
    """
    merged_data = pd.merge(pdf_data, contact_data, on="Name", how="left")
    merged_data.fillna("", inplace=True)  # Replace NaN values with empty strings for clarity
    return merged_data

def main():
    pdf_directory = "./certificates"  # Replace with actual directory path
    contact_csv_path = "clients.csv"  # Replace with actual CSV path

    # Step 1: Compile data from PDFs
    pdf_data = compile_pdf_data(pdf_directory)
    
    # Step 2: Load contact information
    contact_data = pd.read_csv(contact_csv_path)
    
    # Step 3: Cross-reference with contact information
    final_data = cross_reference_data(pdf_data, contact_data)
    
    # Step 4: Save the compiled and merged data
    output_path = "compiled_data.csv"
    final_data.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
