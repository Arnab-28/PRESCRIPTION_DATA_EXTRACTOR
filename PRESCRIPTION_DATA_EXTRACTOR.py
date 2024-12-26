from PIL import Image
import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import pandas as pd
import re

# Configure the Generative AI Model
genai.configure(api_key=st.secrets["api_key"])

st.markdown(
    """
    <style>
    /* Adjust the sidebar and main content widths for responsiveness */
    [data-testid="stSidebar"] {
        width: 250px;
    }
    [data-testid="stAppViewContainer"] {
        padding: 1rem;
    }
    /* Font sizes for different screen sizes */
    h1 {
        font-size: calc(1.5em + 1vw);
    }
    .big-font {
        font-size: calc(1em + 0.8vw);
    }
    /* Responsive charts */
    .chart-container {
        width: 100%;
        height: auto;
    }
    /* Responsive sidebar adjustments */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 100px;
            font-size: 0.8em;
        }
        h1 {
            font-size: 1.5em;
        }
        .big-font {
            font-size: 1em;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar setup
st.sidebar.header("Contact Me")

def display_social_icons():
    # Define social media links
    social_media_links = {
        "LinkedIn": "https://www.linkedin.com/in/your-profile",
        "GitHub": "https://github.com/your-profile"
    }

    # Create HTML for social media icons
    social_media_html = f"""
    <div style="display: flex; justify-content: space-around; align-items: center;">
        <a href="{social_media_links['LinkedIn']}" target="_blank" style="margin: 0 5px;">
            <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
        </a>
        <a href="{social_media_links['GitHub']}" target="_blank" style="margin: 0 5px;">
            <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
        </a>
    </div>
    """
    
    # Use Streamlit to render the HTML in the sidebar
    st.sidebar.markdown(social_media_html, unsafe_allow_html=True)

# Call the function to display social media links in the sidebar
display_social_icons()

# Function to load Gemini 1.5 Flash Model
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to get response from Gemini model
def get_gemini_response(input_prompt, image_parts=None, pdf_text=None):
    # Ensure input data is not empty
    if not image_parts and not pdf_text:
        st.error("No valid data provided for processing.")
        return ""

    # Prepare input for the Gemini model
    input_data = [input_prompt]
    if image_parts:
        input_data.append(image_parts[0])
    if pdf_text:
        input_data.append(pdf_text)

    try:
        # Generate response
        response = model.generate_content(input_data)
        return response.text
    except Exception as e:
        st.error(f"Error communicating with Gemini model: {e}")
        return ""

# Function to parse Gemini's response into structured data
def parse_gemini_response(response):
    details = {
        "Patient Name": "N/A",
        "Patient Age": "N/A",
        "Patient Gender": "N/A",
        "Doctor Visiting Date": "N/A",
        "Doctor Name": "N/A",
        "Prescribed Medications & Dosage & Duration": "N/A",
        "Disease Name": "N/A",
        "Observations": "N/A",
        "Blood Pressure": "N/A",
        "Pulse Rate": "N/A",
        "Body Weight": "N/A",
        "SpO2": "N/A",
        "Pathology Test Required": "N/A"
    }
    # Split the response into lines for processing
    lines = response.split("\n")
    
    for line in lines:
        if "Patient Name:" in line:
            details["Patient Name"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "Patient Age:" in line:
            details["Patient Age"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "Patient Gender:" in line:
            details["Patient Gender"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "Doctor Visiting Date:" in line:
            details["Doctor Visiting Date"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "Doctor Name:" in line:
            details["Doctor Name"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "Prescribed Medications & Dosage & Duration:" in line:
            # Start capturing the block after the "Prescribed Medications" line
            medications_start = response.index(line) + len("Prescribed Medications & Dosage & Duration:")
            medications_block = response[medications_start:].split("Disease Name", 1)[0].strip()  # Stop before the next block
            # Clean the block and extract
            medications_block = re.sub(r"^\*\*|\*\*$", "", medications_block).strip()
            details["Prescribed Medications & Dosage & Duration"] = medications_block

        # Extract Disease Name
        elif "Disease Name, Observations, etc.:" in line:
            disease_start = response.index(line) + len("Disease Name, Observations, etc.:")
            disease_block = response[disease_start:].split("Observations:", 1)[0].strip()  # Stop before the next block
            # Clean the block and extract
            disease_block = re.sub(r"^\*\*|\*\*$", "", disease_block).strip()
            details["Disease Name"] = disease_block
        
        elif "Observations:" in line:
            details["Observations"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "Blood Pressure (BP):"  in line:
            details["Blood Pressure"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "Body Weight" in line:
            details["Body Weight"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "Pulse Rate (PR):" in line:
            details["Pulse Rate"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        elif "SpO2:" in line:
            details["SpO2"] = re.sub(r"^\*\*|\*\*$", "", line.split(":", 1)[-1].strip())

        # Extract pathology test required details
        elif "Pathology Test Required:" in line:
            pathology_start = response.index(line) + len("Pathology Test Required:")
            pathology_block = response[pathology_start:].split("Important Note:", 1)[0].strip()
            # Clean the block and extract
            pathology_block = re.sub(r"^\*\*|\*\*$", "", pathology_block).strip()
            details["Pathology Test Required"] = pathology_block

    return details

# Function to clean the text by removing '*' and extra newlines
def clean_text(text):
    # Remove '*' characters
    cleaned_text = re.sub(r"\*+", "", text)
    # Remove extra newlines and trim leading/trailing whitespaces
    cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text).strip()
    return cleaned_text

# Initialize the Streamlit App
#st.set_page_config(page_title="Prescription Data Extractor")
st.header("Prescription Data Extractor")

# Initialize session states if they do not exist
if "all_details_df" not in st.session_state:
    st.session_state["all_details_df"] = pd.DataFrame()  # Initialize an empty DataFrame
if "extracted_text" not in st.session_state:
    st.session_state["extracted_text"] = ""  # Initialize extracted_text as an empty string
if "edited_text" not in st.session_state:
    st.session_state["edited_text"] = ""  # Initialize edited_text as an empty string

# Define the Default input prompt for Data extraction
prompt = """You are an expert in understanding Medical Prescription.

We will upload an image as Medical Prescription and you will have to extract information such as:
- Patient Name, Patient Age, Patient Gender
- Doctor Name, Doctor Visiting Date
- Prescribed Medications & Dosage & Duration
- Disease Name, Observations, Blood Pressure, Pulse Rate, Body Weight, SpO2
- Pathology Test Required.

Fill missing fields with 'N/A'.
"""

# File uploader for multiple files
uploaded_file = st.file_uploader("Choose an Image/PDF of the Prescription", 
                                 type=["jpg", "jpeg", "png", "pdf"])
st.session_state.clear()

if uploaded_file:
    file_type = uploaded_file.type
    image_part = None
    pdf_text = None
    
    # Process Image File
    if file_type in ["image/jpeg", "image/png"]:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_column_width=True)
        uploaded_file.seek(0)  # Reset file pointer to the beginning
        bytes_data = uploaded_file.read()
        image_part = [{"mime_type": file_type, "data": bytes_data}]

    # Process PDF File
    elif file_type == "application/pdf":
        reader = pdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in range(len(reader.pages)):
            page_obj = reader.pages[page]
            text = page_obj.extract_text()
            if text:
                pdf_text += text
            else:
                st.warning(f"Warning: No extractable text on page {page+1}.")

    # Extract Data Button
    if st.button("Extract Data"):
        if image_part or pdf_text:
            response = get_gemini_response(prompt, image_parts=image_part, pdf_text=pdf_text)
            if response:
                cleaned_response = clean_text(response)
            st.session_state["extracted_text"] = cleaned_response
            st.text_area("Extracted Data (editable)", cleaned_response, height=200)
            
            # Download the cleaned extracted text as .txt file
            st.download_button("Download Extracted Data (.txt)", cleaned_response, file_name="extracted_data.txt", mime="text/plain")

# Upload the processed text file
uploaded_text_file = st.file_uploader("Upload Processed Text File", type=["txt"])

if uploaded_text_file:
    text_data = uploaded_text_file.read().decode("utf-8")
    st.text(text_data)
    # Parse the text data and convert it into structured table format
    parsed_details = parse_gemini_response(text_data)
    details_df = pd.DataFrame([parsed_details])
    
    # Display the parsed table
    st.dataframe(details_df)

    # Export table to CSV
    st.download_button("Download Table (CSV)", details_df.to_csv(index=False), file_name="extracted_data_table.csv", mime="text/csv")
