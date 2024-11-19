import os
import re
import pandas as pd
from PyPDF2 import PdfReader
import streamlit as st

# File paths for static CSV files
COURSE_FILE = "courses.csv"
CONTACT_FILE = "clients.csv"

def load_course_table(course_file):
    """
    Load the course table from the provided CSV file.
    """
    if not os.path.exists(course_file):
        st.error(f"Course file not found: {course_file}")
        return {}
    course_table = pd.read_csv(course_file)
    # Convert to dictionary: {Unit Code: Course Name}
    return dict(zip(course_table.iloc[:, 1], course_table.iloc[:, 0]))

def load_contact_table(contact_file):
    """
    Load the contact table from the provided CSV file.
    """
    if not os.path.exists(contact_file):
        st.error(f"Contact file not found: {contact_file}")
        return pd.DataFrame()
    return pd.read_csv(contact_file)

def extract_data_from_pdf(pdf_path, course_dict):
    """
    Extract data (Name, Certificate Number, Date of Issue, Course Codes) from a single PDF.
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Define regex patterns for the desired fields
    name_pattern = r"This is a statement that:\s*(.+)"
    cert_number_pattern = r"Certificate Number:\s*(\S+)"
    date_pattern = r"Date of Issue:\s*(\d{1,2}-\w{3}-\d{2})"
    course_code_pattern = r"(RII[A-Z]+\d+[A-Z]?)"

    # Extract fields
    name = re.search(name_pattern, text)
    cert_number = re.search(cert_number_pattern, text)
    date_of_issue = re.search(date_pattern, text)
    course_codes = re.findall(course_code_pattern, text)

    name = name.group(1).strip() if name else None
    cert_number = cert_number.group(1).strip() if cert_number else None
    date_of_issue = date_of_issue.group(1).strip() if date_of_issue else None

    # Map course codes to course names
    rows = []
    for course_code in course_codes:
        rows.append({
            "Name": name,
            "Certificate Number": cert_number,
            "Date of Issue": date_of_issue,
            "Course Code": course_code,
            "Course Name": course_dict.get(course_code, "")  # Lookup course name, blank if not found
        })

    return rows

def compile_pdf_data(uploaded_pdfs, course_dict):
    """
    Compile data from uploaded PDFs.
    """
    all_rows = []
    for uploaded_file in uploaded_pdfs:
        pdf_path = uploaded_file.name
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        rows = extract_data_from_pdf(pdf_path, course_dict)
        all_rows.extend(rows)
    return pd.DataFrame(all_rows)

def cross_reference_data(pdf_data, contact_data):
    """
    Cross-reference PDF data with the contact information.
    """
    return pd.merge(pdf_data, contact_data, on="Name", how="left")

# Streamlit App
st.title("Certificate Processor")

st.markdown("""
This app processes certificate PDFs, matches course codes with course names, 
and cross-references the data with contact information.
""")

# Load the course dictionary
course_dict = load_course_table(COURSE_FILE)
contact_data = load_contact_table(CONTACT_FILE)

if course_dict and not contact_data.empty:
    # Upload PDFs
    uploaded_pdfs = st.file_uploader("Upload Certificate PDFs", type="pdf", accept_multiple_files=True)

    if st.button("Process PDFs"):
        if uploaded_pdfs:
            # Process the uploaded PDFs
            st.info("Processing PDFs...")
            pdf_data = compile_pdf_data(uploaded_pdfs, course_dict)

            # Cross-reference with contact data
            st.info("Cross-referencing with contact information...")
            final_data = cross_reference_data(pdf_data, contact_data)

            # Display the results
            st.success("Processing complete!")
            st.write("Final Data:")
            st.dataframe(final_data)

            # Provide CSV download
            csv = final_data.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Final Data as CSV",
                data=csv,
                file_name="final_data.csv",
                mime="text/csv"
            )
        else:
            st.error("Please upload at least one PDF.")
else:
    st.stop()
