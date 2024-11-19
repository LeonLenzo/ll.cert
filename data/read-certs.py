import fitz  # PyMuPDF library
import pandas as pd
import os
import re

# Function to extract specific fields from a single PDF file
def extract_fields_from_pdf(pdf_path):
    with fitz.open(pdf_path) as pdf:
        text = ""
        for page_num in range(pdf.page_count):
            text += pdf[page_num].get_text()
            
    # Extract relevant fields using updated regex patterns
    name = re.search(r"\bThis is a statement that:\s*([A-Za-z\s\-\']+)(?=\s*Certificate Number)", text)
    cert_number = re.search(r"Certificate Number:\s*([\w-]+)", text)
    issue_date = re.search(r"Date of Issue:\s*([\d]{1,2}-[A-Za-z]{3}-[\d]{2})", text)
    # Find each unit of competency including both code and description
    units = re.findall(r"(RII\w+\s[^\n]+)", text)
    
    # Clean and format extracted data
    name = name.group(1).strip() if name else "N/A"
    cert_number = cert_number.group(1) if cert_number else "N/A"
    issue_date = issue_date.group(1) if issue_date else "N/A"
    
    # Return a list of rows, one for each unit of competency
    rows = []
    for unit in units:
        rows.append([name, cert_number, issue_date, unit.strip()])
    
    return rows

# Function to save extracted data to a CSV file, overwriting any existing file
def save_data_to_csv(data, csv_path):
    df = pd.DataFrame(data, columns=["Name", "Certificate Number", "Date of Issue", "Units of Competency", "DOB", "Email"])
    df.to_csv(csv_path, index=False)

# Main function to process all PDFs in a directory and cross-reference with another spreadsheet
def process_pdf_directory(directory_path, csv_path, reference_path):
    data = []
    
    # Load the reference spreadsheet
    reference_df = pd.read_csv(reference_path)
    
    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            # Extract rows for each unit from each PDF file
            extracted_data = extract_fields_from_pdf(pdf_path)
            
            # Cross-reference and add additional columns from the reference data
            for row in extracted_data:
                name = row[0]
                cert_number = row[1]
                
                # Attempt to find matching reference data based on Name or Certificate Number
                match = reference_df[(reference_df['Name'] == name) | (reference_df['Certificate Number'] == cert_number)]
                
                # If a match is found, add DOB and Email; otherwise, leave as "N/A"
                if not match.empty:
                    dob = match.iloc[0]['DOB']
                    email = match.iloc[0]['Email']
                else:
                    dob = "N/A"
                    email = "N/A"
                
                # Append the additional data to the row
                data.append(row + [dob, email])
    
    # Save all extracted data to the CSV file (overwrite mode), including additional columns
    save_data_to_csv(data, csv_path)

# Usage
directory_path = "./certificates"
csv_path = "certificates.csv"
reference_path = "database.csv"

# Process all PDFs in the directory, cross-reference, and save to CSV
process_pdf_directory(directory_path, csv_path, reference_path)
