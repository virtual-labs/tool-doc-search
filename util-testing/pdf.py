import requests
from io import BytesIO
import fitz  # PyMuPDF

# Replace with the direct download link
pdf_url = "https://drive.google.com/uc?export=download&id=1zdCYmIpdj2JnOIdUKD85in8FjIVHurct"

response = requests.get(pdf_url)
if response.status_code == 200:
    pdf_data = BytesIO(response.content)

    headings_and_sections = []

    pdf = fitz.open(stream=pdf_data, filetype="pdf")

    # pdf = fitz.open(filePath) # filePath is a string that contains the path to the pdf
    for page in pdf:
        dict = page.get_text("dict")
        blocks = dict["blocks"]
        for block in blocks:
            if "lines" in block.keys():
                spans = block['lines']
                for span in spans:
                    data = span['spans']
                    for lines in data:
                        print(lines)
                        # only store font information of a specific keyword
                        # if keyword in lines['text'].lower():
                        #     results.append(
                        #         (lines['text'], lines['size'], lines['font']))
                        # lines['text'] -> string, lines['size'] -> font size, lines['font'] -> font name
    pdf.close()

    # for section in headings_and_sections:
    #     print(section)
else:
    print("Failed to download the PDF file.")
