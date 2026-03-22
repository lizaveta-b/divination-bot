from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import PyPDF2

def pdf_to_text(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        total_pages = len(pdf_reader.pages)
    result = {}
    for page_num, page in enumerate(extract_pages(pdf_path)):
        if page_num >= total_pages:
            break
        page_lines = []
        elements = [(element.y1, element) for element in page._objs]
        elements.sort(key=lambda a: a[0], reverse=True)
        for _, element in elements:
            if isinstance(element, LTTextContainer):
                text = element.get_text().strip()
                if text:
                    lines = text.split('\n')
                    for line in lines:
                        clean_line = ' '.join(line.split())
                        if clean_line:
                            page_lines.append(clean_line)
        result[page_num + 1] = page_lines
    return result