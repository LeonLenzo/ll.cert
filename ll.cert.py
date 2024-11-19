import streamlit as st
import pandas as pd
import os
from PyPDF2 import PdfReader

# Function to extract data from a single PDF
def extract_data_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

        # Define regex patterns
        import re
        name_pattern = r"This is a statement that:\s*(.+)"
        cert_number_pattern = r"Certificate Number:\s*(\S+)"
        date_pattern = r"Date of Issue:\s*(\d{1,2}-\w{3}-\d{2})"
        course_code_pattern = r"(RII[A-Z]+\d+[A-Z]?)"

        # Extract fields
        name = re.search(name_pattern, text)
        cert_number = re.search(cert_number_pattern, text)
        date_of_issue = re.search(date_pattern, text)
        course_codes = re.findall(course_code_pattern, text)

        # Clean extracted data
        name = name.group(1).strip() if name else None
        cert_number = cert_number.group(1).strip() if cert_number else None
        date_of_issue = date_of_issue.group(1).strip() if date_of_issue else None

        # Create rows for each course code
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
        st.error(f"Error processing file {os.path.basename(pdf_path)}: {e}")
        return []

# Function to compile data from all PDFs
def compile_pdf_data(pdf_files):
    all_rows = []
    for pdf_file in pdf_files:
        rows = extract_data_from_pdf(pdf_file)
        all_rows.extend(rows)
    return pd.DataFrame(all_rows)

# Function to cross-reference data
def cross_reference_data(pdf_data, contact_data):
    merged_data = pd.merge(pdf_data, contact_data, on="Name", how="left")
    merged_data.fillna("", inplace=True)  # Replace NaN with empty strings
    return merged_data

# Streamlit App
st.title("Errun loves it.")

st.markdown("""
This app processes certificate PDFs and cross-references them with a contact information CSV.
Upload your files below to get started.
""")

# File upload widgets
uploaded_pdfs = st.file_uploader("Upload PDF Certificates (multiple files allowed)", type="pdf", accept_multiple_files=True)
uploaded_csv = st.file_uploader("Upload Contact Info CSV", type="csv")

if st.button("Process Files"):
    if uploaded_pdfs and uploaded_csv:
        # Process PDFs
        st.info("Processing PDF files...")
        pdf_data = compile_pdf_data(uploaded_pdfs)

        # Load CSV
        st.info("Processing contact info CSV...")
        contact_data = pd.read_csv(uploaded_csv)

        # Cross-reference data
        st.info("Cross-referencing data...")
        final_data = cross_reference_data(pdf_data, contact_data)

        # Display and allow download
        st.success("Processing complete!")
        st.write("Compiled Data:")
        st.dataframe(final_data)

        # Provide download link
        csv = final_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Compiled Data",
            data=csv,
            file_name="compiled_data.csv",
            mime="text/csv"
        )
    else:
        st.error("Please upload both PDF files and the contact CSV.")
