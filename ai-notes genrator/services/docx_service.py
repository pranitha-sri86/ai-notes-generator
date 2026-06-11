from docx import Document

def extract_docx_text(docx_file):

    document = Document(docx_file)

    text = []

    for paragraph in document.paragraphs:
        text.append(paragraph.text)

    return "\n".join(text)