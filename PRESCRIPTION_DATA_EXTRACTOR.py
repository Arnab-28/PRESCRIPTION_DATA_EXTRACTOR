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
        "Blood Pressure (BP)": "N/A",
        "Pulse Rate (PR)": "N/A",
        "Body Weight": "N/A",
        "Oxygen Saturation (SpO2)": "N/A",
        "Pathology Test Required": "N/A"
        "Pathology Test Report": "N/A"
    }
    # Split the response into lines for processing
    lines = response.split("\n")
    
    for line in lines:
        # Extract Patient Name
        if "Patient Name:" in line:
            # Extract the portion of the line after "Patient Name:"
            patient_name = line.split("Patient Name:", 1)[-1].strip()
            # Remove unwanted characters (e.g., **, trailing spaces)
            details["Patient Name"] = re.sub(r"^\*\*|\*\*$", "", patient_name)
            
        # Extract Patient Age
        elif "Patient Age:" in line:
            # Extract the portion of the line after "Patient Name:"
            patient_age = line.split("Patient Age:", 1)[-1].strip()
            # Remove unwanted characters (e.g., **, trailing spaces)
            details["Patient Age"] = re.sub(r"^\*\*|\*\*$", "", patient_age) 
            
        # Extract Patient Gender
        elif "Patient Gender:" in line:
            # Extract the portion of the line after "Patient Name:"
            patient_gender = line.split("Patient Gender:", 1)[-1].strip()
            # Remove unwanted characters (e.g., **, trailing spaces)
            details["Patient Gender"] = re.sub(r"^\*\*|\*\*$", "", patient_gndere)

        # Extract Doctor Name
        elif "Doctor Name:" in line:
            doctor_name_start = response.index(line) + len("Doctor Name:")
            doctor_name_block = response[doctor_name_start:].split("Doctor Visiting Date:", 1)[-1].strip()  # Stop before the next block
            # Clean the block and extract
            details["Doctor Name"] = re.sub(r"^\*\*|\*\*$", "", doctor_name_block).strip()
        
        # Extract Doctor Visiting Date
        elif "Doctor Visiting Date:" in line:
            doctor_visiting_date_start = response.index(line) + len("Doctor Visiting Date:")
            doctor_visiting_date_block = response[doctor_visiting_date_start:].split("Prescribed Medications & Dosage & Duration:", 1)[-1].strip()  # Stop before the next block
            # Clean the block and extract
            details["Doctor Visiting Date"] = re.sub(r"^\*\*|\*\*$", "", doctor_visiting_date_block).strip()
            
        # Extract Prescribed Medications & Dosage & Duration
        elif "Prescribed Medications & Dosage & Duration:" in line:
            medications_start = response.index(line) + len("Prescribed Medications & Dosage & Duration:")
            medications_block = response[medications_start:].split("Disease Name, Observations, Vital Signs:", 1)[-1].strip()  # Stop before the next block
            # Clean the block and extract
            details["Prescribed Medications & Dosage & Duration"] = re.sub(r"^\*\*|\*\*$", "", medications_block).strip()

        # Extract Disease Name
        elif "Disease Name:" in line:
            disease_start = response.index(line) + len("Disease Name:")
            disease_block = response[disease_start:].split("Observations:", 1)[-1].strip()  # Stop before the next block
            # Clean the block and extract
            details["Disease Name"] = re.sub(r"^\*\*|\*\*$", "", disease_block).strip()

        # Extract Disease Name
        elif "Observations:" in line:
            observations_start = response.index(line) + len("Observations:")
            observations_block = response[observations_start:].split("Blood Pressure (BP):", 1)[-1].strip()  # Stop before the next block
            # Clean the block and extract 
            details["Observations"] = re.sub(r"^\*\*|\*\*$", "", observations_block).strip()

        # Extract Blood Pressure (BP)
        elif "Blood Pressure (BP):"  in line:
            blood_pressure_start = response.index(line) + len("Blood Pressure (BP):")
            blood_pressure_block = response[blood_pressure_start:].split("Pulse Rate (PR):", 1)[-1].strip()  # Stop before the next block
            # Clean the block and extract
            details["Blood Pressure (BP)"] = re.sub(r"^\*\*|\*\*$", "", blood_pressure_block).strip()

        # Extract Pulse Rate (PR)
        elif "Pulse Rate (PR):" in line:
            pulse_rate_start = response.index(line) + len("Pulse Rate (PR):")
            pulse_rate_block = response[pulse_rate_start:].split("Body Weight:", 1)[-1].strip()  # Stop before the next block
            # Clean the block and extract
            details["Pulse Rate (PR)"] = re.sub(r"^\*\*|\*\*$", "", pulse_rate_block).strip()

        # Extract Body Weight
        elif "Body Weight" in line:
            body_weight_start = response.index(line) + len("Body Weight:")
            body_weight_block = response[body_weight_start:].split("SpO2:", 1)[-1].strip()  # Stop before the next block
            # Clean the block and extract
            details["Body Weight"] = re.sub(r"^\*\*|\*\*$", "", body_weight_block).strip()

        # Extract Oxygen Saturation (SpO2)
        elif "SpO2:" in line:
            oxygen_saturation_spo2_start = response.index(line) + len("Pathology Test Required:")
            oxygen_saturation_spo2_block = response[oxygen_saturation_spo2_start:].split("Pathology Test Required:", 1)[-1].strip() # Stop before the next block
            # Clean the block and extract
            details["Oxygen Saturation (SpO2)"] = re.sub(r"^\*\*|\*\*$", "", oxygen_saturation_spo2_block).strip()

        # Extract Pathology Test Required Details
        elif "Pathology Test Required:" in line:
            pathology_start = response.index(line) + len("Pathology Test Required:")
            pathology_block = response[pathology_start:].split("Important Note:", 1)[-1].strip() # Stop before the next block
            # Clean the block and extract
            details["Pathology Test Required"] = re.sub(r"^\*\*|\*\*$", "", pathology_block).strip()

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
prompt = """You are an expert in understanding Medical Prescription or Pathology Test Report.

We will upload an image as Medical Prescription and you will have to extract information such as:
- Patient Name, Patient Age, Patient Gender
- Doctor Name, Doctor Visiting Date
- Prescribed Medications & Dosage & Duration
- Disease Name, Observations, Blood Pressure, Pulse Rate, Body Weight, SpO2
- Pathology Test Required
- Pathology Test Result.

Please follow these instructions carefully:
1. Do not include any additional text, comments, or explanations in your response.
2. If no information matches the description, return 'N/A' value.
3. Your output should contain only the data that is explicitly requested, with no other text.
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
        st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_container_width=True)
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
