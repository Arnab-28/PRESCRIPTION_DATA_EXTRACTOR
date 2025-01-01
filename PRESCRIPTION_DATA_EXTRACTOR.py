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
        "LinkedIn": "https://www.linkedin.com/in/arnabdas28",
        "GitHub": "https://github.com/Arnab-28"
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
def get_gemini_response(input_prompt, input_data):
    try:
        # Generate response
        response = model.generate_content(input_data)
        return response.text
    except Exception as e:
        st.error(f"Error communicating with Gemini model: {e}")
        return ""

# Function to parse Gemini's response into structured data
def parse_gemini_response(response):
    
    # Initialize an empty list to store patient records
    all_details = []

    # Split response into patient blocks using a delimiter or pattern
    patient_blocks = re.split(r"(?=Patient Name:)", response)  # Split on "Patient Name:"

    # Iterate through each block and extract details
    for block in patient_blocks:
        
        if not block.strip():
            continue
        
        # Initialize a default dictionary for patient details
        details = {
            "Patient Name": "N/A",
            "Patient Age (in Years)": "N/A",
            "Patient Gender": "N/A",
            "Doctor Visiting Date": "N/A",
            "Doctor Name": "N/A",
            "Prescribed Medications & Dosage & Duration": "N/A",
            "Disease Name": "N/A",
            "Observations": "N/A",
            "Blood Pressure (in mm of Hg)": "N/A",
            "Pulse Rate (in beats per minute)": "N/A",
            "Body Weight (in Kg)": "N/A",
            "Oxygen Saturation (in %)": "N/A",
            "Pathology Test Required": "N/A",
            "Pathology Test Report": "N/A"
        }
        # Split the response into lines for processing
        lines = block.split("\n")
        
        for line in lines:
            for key in details.keys():
                if key in line:
                    details[key] = line.split(f"{key}:", 1)[-1].strip()
        # Add the extracted details to the list
        all_details.append(details)
    # Convert list of details into a DataFrame
    return pd.DataFrame(all_details)
     
    
# Function to clean the text by removing '*' and extra newlines
def clean_text(text):
    # Remove '*' characters
    cleaned_text = re.sub(r"\*+", "", text)
    # Remove extra newlines and trim leading/trailing whitespaces
    cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text).strip()
    return cleaned_text

# Initialize the Streamlit App
#st.set_page_config(page_title="Prescription Data Extractor")
st.header("Medical Document Data Extractor")

# File uploader for multiple files
uploaded_file = st.file_uploader("Choose an Image/PDF of the Prescription", 
                                 type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    file_type = uploaded_file.type
    input_data = ""
    
    # Process Image File
    if file_type in ["image/jpeg", "image/png"]:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_column_width=True)
        uploaded_file.seek(0)  # Reset file pointer to the beginning
        input_data = [{"mime_type": file_type, "data": uploaded_file.read()}]

    # Process PDF File
    elif file_type == "application/pdf":
        reader = pdf.PdfReader(uploaded_file)
        input_data = "".join([page.extract_text() for page in reader.pages if page.extract_text()])

    # Extract Data Button
    if st.button("Extract Information"):
        if input_data:
            # Define the Default input prompt for Data extraction
            prompt = """You are an expert in understanding Medical Prescription or Pathology Test Report.
            We will upload an image as Medical Prescription and you will have to extract information such as:
            - Patient Name, Patient Age, Patient Gender
            - Doctor Name, Doctor Visiting Date
            - Prescribed Medications & Dosage & Duration
            - Disease Name, Observations, Blood Pressure, Pulse Rate, Body Weight, Oxygen Saturation (SpO2)
            - Pathology Test Required
            - Pathology Test Report.
            Please follow these instructions carefully:
            1. Do not include any additional text, comments, or explanations in your response.
            2. If no information matches the description, return 'N/A' value.
            3. Your output should contain only the data that is explicitly requested, with no other text.
            Please generate in a text content.
            """
            response = get_gemini_response(prompt, input_data)
            if response:
                cleaned_response = clean_text(response)
                st.text_area("Extracted Data (editable)", cleaned_response, height=200)
                # Download the cleaned extracted text as .txt file
                st.download_button("Download Extracted Data (.txt)", cleaned_response, file_name="extracted_data.txt", mime="text/plain")

# Upload the processed text file
uploaded_text_file = st.file_uploader("Upload Extracted Text File for Table Conversion", type=["txt"])

if uploaded_text_file:
    text_data = uploaded_text_file.read().decode("utf-8")
    st.text(text_data)
    # Parse the text data and convert it into structured table format
    details_df = parse_gemini_response(text_data)
    # Display the parsed table
    st.dataframe(details_df)

    # Export table to CSV
    st.download_button("Download Table (CSV)", details_df.to_csv(index=False), file_name="extracted_data_table.csv", mime="text/csv")
