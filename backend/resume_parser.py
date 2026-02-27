from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document


def extract_text(file_path) -> str:
    file_path = str(file_path) 
    if file_path.lower().endswith(".pdf"):
        try:
            text = extract_pdf_text(file_path)
        except Exception as e:
            print(f"[ERROR] Could not read PDF file: {e}")
            text = ""
    elif file_path.lower().endswith(".docx"):
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"[ERROR] Could not read DOCX file: {e}")
            text = ""
    else:
        raise ValueError(f"Unsupported file type: '{file_path}'. Please upload PDF or DOCX.")

    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return text