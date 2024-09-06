from dotenv import load_dotenv

load_dotenv()
import streamlit as st
import fitz
import base64
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(input,pdf_content,prompt):
    model=genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content([input,pdf_content[0],prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Open the PDF file using PyMuPDF
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")

        # Get the first page of the PDF
        first_page = pdf_document.load_page(0)
        
        # Convert the first page to an image (pixmap)
        pix = first_page.get_pixmap()

        # Convert the pixmap to an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]

        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")


input_prompt1="""
You are an experienced HR with Tech Experience in the field of Data Science,Full Stack Web Development,
Big Data Engineering, DEVOPS, Data Analyst, Project Manager,your task is to review 
the provided resume against the job description for these profiles.
Please share your professsional evaluation on whether the candidate's profile aligns with the roles
highlight the strengths and weaknesses of the applicant in related to specific job requirements.
"""



input_prompt2="""
You are an skilled ATS(Applicant Tracking System) scanner with a deep undserstanding of data Science,Full Stack Web Development,
Big Data Engineering, DEVOPS, Data Analyst, Project Manage and  deep ATS functionality
your task is to evaluate the resume against the provided job description. give me the percentage match if the resume matches the job description
First the output should come as percentage and then keywords missing and last final thoughts
  """


# Streamlit App
st.set_page_config(page_title="ATS Resume Expert", layout="wide")

# Title and Description with styling (Title in Beige)
st.markdown("<h1 style='text-align: center; color: red;'>ATS Resume Checker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Evaluate your resume against ATS job requirements for Data Science, Full Stack Web Development, and more.</p>", unsafe_allow_html=True)

# Columns for better layout
col1, col2 = st.columns([1, 2])

with col1:
    st.sidebar.header("Input Section")
    
    # Sidebar for Inputs
    input_text = st.sidebar.text_area("Job Description: ", key="input")
    uploaded_file = st.sidebar.file_uploader("Upload your resume (PDF)...", type=["pdf"])

    if uploaded_file is not None:
        st.sidebar.success("PDF Uploaded Successfully")

    # Action buttons
    submit1 = st.sidebar.button("Tell Me About the Resume")
    submit2 = st.sidebar.button("Percentage Match")

# Centering the main content
with col2:
   

    # Instructions
    with st.expander("How to Use", expanded=True):
        st.write("""
        1. Upload your resume in PDF format.
        2. Enter the job description for which you're applying.
        3. Click on either 'Tell Me About the Resume' for feedback or 'Percentage Match' to see how well your resume matches the job description.
        """)

# Spinners for loading feedback
if submit1:
    if uploaded_file is not None:
        with st.spinner('Evaluating Resume...'):
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_prompt1, pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
    else:
        st.write("Please Upload the resume")

elif submit2:
    if uploaded_file is not None:
        with st.spinner('Calculating Percentage Match...'):
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_prompt2, pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
    else:
        st.write("Please Upload the resume")

# Adding a footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: red;'>Powered by Gemini AI & Streamlit</p>", unsafe_allow_html=True)
