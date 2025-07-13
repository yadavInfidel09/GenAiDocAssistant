import fitz  # PyMuPDF
import os

def parse_pdf(file_path):
    doc = fitz.open(file_path)
    parsed = []
    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        for para_num, para in enumerate(paragraphs, 1):
            parsed.append({
                'text': para,
                'page': page_num,
                'paragraph': para_num
            })
    return parsed

def parse_txt(file_path):
    parsed = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        for idx, para in enumerate(lines, 1):
            parsed.append({
                'text': para,
                'page': 1,
                'paragraph': idx
            })
    return parsed

def parse_document(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.pdf':
        return parse_pdf(file_path)
    elif ext == '.txt':
        return parse_txt(file_path)
    else:
        raise ValueError('Unsupported file type: ' + ext)
