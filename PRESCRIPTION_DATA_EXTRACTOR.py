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

# Function to download the edited text file
def download_edited_file():
    if "edited_text" in st.session_state and st.session_state["edited_text"]:
        st.download_button("Download Edited Extracted Data (.txt)",st.session_state["edited_text"],file_name="extracted_data.txt",mime="text/plain")
    else:
        st.warning("No data to download. Please edit the text first.")

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
            # Extract Patient Name
            if "Patient Name:" in line:
                # Extract the portion of the line after "Patient Name:"
                patient_name = line.split("Patient Name:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Patient Name"] = re.sub(r"^\*\*|\*\*$", "", patient_name)
                
            # Extract Patient Age
            elif "Patient Age:" in line:
                # Extract the portion of the line after "Patient Age:"
                patient_age = line.split("Patient Age:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Patient Age (in Years)"] = re.sub(r"^\*\*|\*\*$", "", patient_age) 
                
            # Extract Patient Gender
            elif "Patient Gender:" in line:
                # Extract the portion of the line after "Patient Gender:"
                patient_gender = line.split("Patient Gender:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Patient Gender"] = re.sub(r"^\*\*|\*\*$", "", patient_gender)

            # Extract Doctor Name
            elif "Doctor Name:" in line:
                # Extract the portion of the line after "Doctor Name:"
                doctor_name = line.split("Doctor Name:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Doctor Name"] = re.sub(r"^\*\*|\*\*$", "", doctor_name)
            
            # Extract Doctor Visiting Date
            elif "Doctor Visiting Date:" in line:
                # Extract the portion of the line after "Doctor Visiting Date:"
                doctor_visiting_date = line.split("Doctor Visiting Date:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Doctor Visiting Date"] = re.sub(r"^\*\*|\*\*$", "", doctor_visiting_date)
                
            # Extract Prescribed Medications & Dosage & Duration
            elif "Prescribed Medications & Dosage & Duration:" in line:
                # Extract the portion of the line after "Prescribed Medications & Dosage & Duration:"
                prescribed_medications = line.split("Prescribed Medications & Dosage & Duration:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Prescribed Medications & Dosage & Duration"] = re.sub(r"^\*\*|\*\*$", "", prescribed_medications)

            # Extract Disease Name
            elif "Disease Name:" in line:
                # Extract the portion of the line after "Disease Name:"
                disease_name = line.split("Disease Name:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Disease Name"] = re.sub(r"^\*\*|\*\*$", "", disease_name)

            # Extract Disease Name
            elif "Observations:" in line:
                # Extract the portion of the line after "Observations:"
                observations = line.split("Observations:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Observations"] = re.sub(r"^\*\*|\*\*$", "", observations)

            # Extract Blood Pressure (BP)
            elif "Blood Pressure:"  in line:
                # Extract the portion of the line after "Observations:"
                blood_pressure = line.split("Blood Pressure:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Blood Pressure (in mm of Hg)"] = re.sub(r"^\*\*|\*\*$", "", blood_pressure)

            # Extract Pulse Rate (PR)
            elif "Pulse Rate" in line:
                # Extract the portion of the line after "Disease Name:"
                pulse_rate = line.split("Pulse Rate:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Pulse Rate (in beats per minute)"] = re.sub(r"^\*\*|\*\*$", "", pulse_rate)

            # Extract Body Weight
            elif "Body Weight" in line:
                # Extract the portion of the line after "Disease Name:"
                body_weight = line.split("Body Weight:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Body Weight (in Kg)"] = re.sub(r"^\*\*|\*\*$", "", body_weight)

            # Extract Oxygen Saturation
            elif "Oxygen Saturation" in line:
                # Extract the portion of the line after "Disease Name:"
                spo2 = line.split("Oxygen Saturation:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Oxygen Saturation (in %)"] = re.sub(r"^\*\*|\*\*$", "", spo2)

            # Extract Pathology Test Required Details
            elif "Pathology Test Required" in line:
                # Extract the portion of the line after "Disease Name:"
                pathology_test_required = line.split("Pathology Test Required:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Pathology Test Required"] = re.sub(r"^\*\*|\*\*$", "", pathology_test_required)

            # Extract Pathology Test Report Details
            elif "Pathology Test Report" in line:
                # Extract the portion of the line after "Disease Name:"
                pathology_test_report = line.split("Pathology Test Report:", 1)[-1].strip()
                # Remove unwanted characters (e.g., **, trailing spaces)
                details["Pathology Test Report"] = re.sub(r"^\*\*|\*\*$", "", pathology_test_report)
                
        # Add the extracted details to the list only if there's valid information
        if any(value != "N/A" for value in details.values()):
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
st.header("Medical Document Data Extractor")

# Initialize session states if they do not exist
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
- Disease Name, Observations, Blood Pressure, Pulse Rate, Body Weight, Oxygen Saturation
- Pathology Test Required
- Pathology Test Report.

Please follow these instructions carefully:
1. Do not include any additional text, comments, or explanations in your response.
2. If no information matches the description, return 'N/A' value.
3. Your output should contain only the data that is explicitly requested, with no other text.

Please generate in a text content don't generate in the parse format.
"""

# File uploader for multiple files
uploaded_file = st.file_uploader("Choose an Image/PDF of the Medical Document", 
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
    if st.button("Extract Information"):
        if image_part or pdf_text:
            st.write("edited_text")
            st.write("extracted_text")
            response = get_gemini_response(prompt, image_parts=image_part, pdf_text=pdf_text)
            if response:
                st.write("edited_text")
                st.write("extracted_text")
                cleaned_response = clean_text(response)
                st.write("edited_text")
                st.write("extracted_text")

            # Initialize session state for the edited text
            if "edited_text" not in st.session_state:
                st.write("edited_text")
                st.write("extracted_text")
                st.session_state["edited_text"] = cleaned_response
                st.write("edited_text")
                st.write("extracted_text")
                
            # Display the cleaned response in a text area, allowing the user to edit
            st.write("edited_text")
            st.write("extracted_text")
            st.text_area("Extracted Data (editable)", value=st.session_state["edited_text"], height=200, key="edited_text", on_change=download_edited_file)
            st.write("edited_text")
            st.write("extracted_text")
            
# Upload the processed text file
uploaded_text_file = st.file_uploader("Upload Extracted Text File", type=["txt"])

if uploaded_text_file:
    text_data = uploaded_text_file.read().decode("utf-8")
    st.text(text_data)
    # Parse the text data and convert it into structured table format
    details_df = parse_gemini_response(text_data)
    # Display the DataFrame in Streamlit without the index column
    st.dataframe(details_df,hide_index = True)

    # Export table to CSV
    st.download_button("Download Table (CSV)", details_df.to_csv(index=False),file_name="extracted_data_table.csv", mime="text/csv")
