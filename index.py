# import streamlit as st
# import pandas as pd
# from io import BytesIO
# import PyPDF2
# import re

# uploaded_file = st.file_uploader("Choose a file")
# if uploaded_file is not None:
#     bytes_data = BytesIO(uploaded_file.getvalue())
#     pdfReader = PyPDF2.PdfReader(bytes_data)

#     text = ""
#     for page in pdfReader.pages:
#         text += page.extract_text() or ""  # Handle potential None values

#     invoice_number_pattern = r"\s+(INV-\d{6})"
#     invoice_number_match = re.search(invoice_number_pattern, text)
#     date = re.search(r"Date\s*([\d/-]+)", text)

#     st.write(f"**Invoice Number:** {invoice_number_match.group(0) if invoice_number_match else 'Not found'}")
import streamlit as st
import boto3
import tempfile
from streamlit_pdf_viewer import pdf_viewer
from streamlit_option_menu import option_menu
import pandas  as pd
from PIL import Image
import os

container_pdf, container_chat = st.columns([50, 50])
# Initialize AWS Textract Client
# Title of the app
session = boto3.Session(
    aws_access_key_id=st.secrets["secrets"]["access_key"],
    aws_secret_access_key=st.secrets["secrets"]["secret_key"],
    region_name='us-east-1'
)
textract = session.client("textract", region_name="us-east-1")  # Change region if needed

def analyze_invoice(file_bytes):
    response = textract.analyze_expense(Document={"Bytes": file_bytes})

    # Extract Invoice Number
    extracted_data = {"Field": [], "Value": []}
    vendor = {"Field": [], "Value": []}
    vendorData = ["VENDOR_NAME", "INVOICE_RECEIPT_DATE","INVOICE_RECEIPT_ID"]
    for expense_doc in response["ExpenseDocuments"]:
        for field in expense_doc["SummaryFields"]:
            label = field.get("Type", {}).get("Text", "")
            value = field.get("ValueDetection", {}).get("Text", "")

            if label and value:
                extracted_data["Field"].append(label)
                extracted_data["Value"].append(value)
            if label not in vendor["Field"] and label in vendorData:
                # print("========",vendor)
                vendor["Field"].append(label)
                vendor["Value"].append(value)
    df = pd.DataFrame(extracted_data)
    dv = pd.DataFrame(vendor)

    return df, dv, vendor

# Streamlit UI

with st.sidebar:
    selected = option_menu("Main Menu", ["HOME","Invoice OCR", 'File Rename', "Pipeline Flow", "settings"],
     icons=['house','bi-file-earmark-break', 'bi-file-earmark', 'bi-activity', 'settings'], menu_icon="cast", default_index=0)
    print(selected)

if selected == "HOME":
    # st.image(image="C:\Users\cim0011\Downloads\Invoice Data Extractor.png")
    st.image("./img/Logo.svg")
    st.title("Invoice Data Extractor Demo")
    st.info('for Amalgamations')

    image = Image.open("./img/Homepage.png")
# Display image
    st.image(image, caption="Sample Invoice")
elif selected == "Invoice OCR":
    st.title("📄 Invoice Data Extractor")

    # File Upload
    uploaded_file = st.file_uploader("Upload an Invoice (JPG, PNG, or PDF)", type=["jpg", "jpeg", "png", "pdf"])
    if uploaded_file is not None:
        # Read File Bytes
        file_bytes = uploaded_file.read()
        
        
        # Process File
        with st.spinner("Extracting Invoice Data..."):
            df, dv, vendor = analyze_invoice(file_bytes)
        if not df.empty:
            st.dataframe(dv)
            st.success("✅ Invoice Data Extracted Successfully!")
            st.dataframe(df)
        else:
            st.error("❌ No key-value pairs found in the document.")

        if file_bytes:
            binary_data = file_bytes
            pdf_viewer(input=binary_data,
                    width="100%", height=100)

elif selected == "File Rename":
    st.title("📂 Upload and Rename File")

    uploaded_file = st.file_uploader("Upload a file", type=["jpg", "png", "pdf", "txt"])

    with st.spinner("File re-name progress..."):
        if uploaded_file is not None:
            # User provides a new name
            df, dv, vendor = analyze_invoice(uploaded_file.read())

            # Get file extension
            file_extension = uploaded_file.name.split(".")[-1]
            print(vendor["Value"][1] + "_" + vendor["Value"][2])
            # Combine new name with extension
            renamed_file = f"{vendor["Value"][1].replace("/","-") + "_" + vendor["Value"][2]}.{file_extension}"

            # Save the renamed file
            save_path = os.path.join("./uploads", renamed_file)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f" File saved as: `{renamed_file}`")

elif selected == "Pipeline Flow":
    st.title("Pipeline for Invoice Data Extraction")
    st.image("./img/pipeline v2.png")
# elif selected == "settings":
#     st.title("Access Key and Secret Key Input")
#     # Create input fields for access key and secret key
#     access_key = st.text_input("Enter Access Key", type="password")
#     secret_key = st.text_input("Enter Secret Key", type="password")

#     if st.button("Submit"):
#         st.secrets["access_key"] = access_key
#         st.secrets["secret_key"] = secret_key
#         st.success("you are Access and secret keys is add")
    
#     if st.button("Clear Cache"):
#         st.secrets["access_key"] = ""
#         st.secrets["secret_key"] = ""
#         st.success("Successfully your cache are cleared")