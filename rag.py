import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import io

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Assistant",
    layout="centered"
)

st.title("Assistant Reader")
st.markdown("""
Upload your PDF documents, enter your Gemini API key, and ask questions about the content.
The assistant will use provide answers.
""")

# --- API Key Input ---
st.subheader("Enter your Gemini API Key")
gemini_api_key = st.text_input(
    "Gemini API Key - https://aistudio.google.com/app/apikey",
    type="password",
    help="You can get your API key from Google AI Studio: https://aistudio.google.com/app/apikey"
)

# Configure the generative AI model if API key is provided
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")
        st.stop()
else:
    st.warning("Please enter your Gemini API Key to proceed.")
    st.stop()

# --- PDF Upload ---
st.subheader("Upload your PDF Documents")
uploaded_files = st.file_uploader(
    "Choose PDF files",
    type="pdf",
    accept_multiple_files=True,
    help="You can upload multiple PDF files."
)

# --- Extract Text from PDFs ---
def extract_text_from_pdfs(files):
    """
    Extracts text from a list of uploaded PDF files.
    """
    all_text = ""
    for uploaded_file in files:
        # Read the PDF file from the BytesIO object
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            all_text += page.extract_text() + "\n"
    return all_text

document_text = ""
if uploaded_files:
    with st.spinner("Extracting text from PDFs..."):
        document_text = extract_text_from_pdfs(uploaded_files)
    if document_text:
        st.success(f"Successfully extracted text from {len(uploaded_files)} PDF(s).")
        # Optionally, show a snippet of the extracted text
        # with st.expander("View Extracted Text (first 500 chars)"):
        #     st.text(document_text[:500] + "..." if len(document_text) > 500 else document_text)
    else:
        st.error("Could not extract text from the uploaded PDFs. They might be scanned images or empty.")
        st.stop()
else:
    st.info("Please upload one or more PDF documents.")
    st.stop()

# --- Question Input ---
st.header("Ask a Question about the PDFs")
user_question = st.text_area(
    "Your Question",
    placeholder="e.g., What is the main topic discussed in these documents?",
    height=100
)

# --- Generate Answer ---
if st.button("Get Answer", type="primary"):
    if not user_question:
        st.warning("Please enter a question.")
    elif not document_text:
        st.warning("No text extracted from PDFs. Please upload valid PDFs.")
    else:
        try:
            # Initialize the generative model
            model = genai.GenerativeModel('gemini-2.0-flash')

            # Construct the prompt for the model
            # It's crucial to provide context (document_text) along with the question.
            prompt = f"""
            You are an AI assistant specialized in answering questions based on provided documents.
            Analyze the following text from PDF documents and answer the user's question.
            If the answer is not found in the provided text, state that you cannot find the answer in the documents.

            --- Document Content ---
            {document_text}
            --- End Document Content ---

            --- User Question ---
            {user_question}
            --- End User Question ---

            Your Answer:
            """

            with st.spinner("Generating answer..."):
                # Generate content using the model
                response = model.generate_content(prompt)

                # Display the answer
                if response.candidates and response.candidates[0].content:
                    st.subheader("Answer:")
                    st.write(response.candidates[0].content.parts[0].text)
                else:
                    st.warning("No answer could be generated. The model might have been blocked or returned an empty response.")
                    if response.prompt_feedback:
                        st.write("Prompt feedback:", response.prompt_feedback)

        except Exception as e:
            st.error(f"An error occurred while generating the answer: {e}")
            st.info("Please check your API key and ensure the content is appropriate.")

st.markdown("---")
st.caption("Alexandre K")