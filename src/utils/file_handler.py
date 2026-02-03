import PyPDF2
import pdfplumber
import docx
from io import BytesIO

def extract_text_from_file(uploaded_file):
    """
    Extracts text from PDF, DOCX, or TXT file.
    Args:
        uploaded_file: Streamlit UploadedFile object.
    Returns:
        str: Extracted text.
    """
    file_type = uploaded_file.name.split('.')[-1].lower()
    text = ""

    try:
        if file_type == 'pdf':
            # Try pdfplumber first for better extraction
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            except Exception as e:
                # Fallback to PyPDF2
                uploaded_file.seek(0)
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        
        elif file_type in ['docx', 'doc']:
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
                
        elif file_type == 'txt':
            text = uploaded_file.getvalue().decode("utf-8")
            
    except Exception as e:
        return f"Error reading file: {str(e)}"

    return text
