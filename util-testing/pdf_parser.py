from llmsherpa.readers import LayoutPDFReader
import json
import PyPDF2
import re


file_name = r"z.pdf"


def extract_pdf_sections(file_name):
    def remove_unicode(input_string):
        return re.sub(r'[^\x00-\x7F]+', '', input_string)
    obj = PyPDF2.PdfReader(file_name)
    llmsherpa_api_url = "https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"
    pdf_url = file_name
    pdf_reader = LayoutPDFReader(llmsherpa_api_url)
    doc = pdf_reader.read_pdf(pdf_url)
    sections = []

    current_page = 0

    def get_page_number(lst):
        for S in lst:
            for i in range(current_page, pgno):
                PgOb = obj.pages[i]
                Text = PgOb.extract_text()
                if re.search(S, Text):
                    current_page = i
                    return i
        return current_page

    pgno = len(obj.pages)
    for section in doc.sections():
        title = (remove_unicode(section.title)).strip()
        text = remove_unicode(section.to_text(
            include_children=True, recurse=True).strip())
        if title != text and len(title) >= 7:
            lines = [t.strip() for t in text.split("\n")[0:10]]
            sections.append(
                {"title": title, "text": text[:200]+" ...", "page": get_page_number(lines)+1})


sections = extract_pdf_sections(file_name=file_name)
print(json.dumps(sections, indent=4))
print(len(sections))
