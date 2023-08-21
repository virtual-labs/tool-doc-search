

import requests
from bs4 import BeautifulSoup
import re
import gdown


def fetch_google_doc(doc_id):
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
    response = requests.get(url)
    return response.content


def convert_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    markdown = ""

    for tag in soup.find_all():
        if tag.name == 'h1':
            markdown += f"# {tag.text}\n"
        elif tag.name == 'h2':
            heading_id = tag.get('id')
            markdown += f"## {tag.text} {{#{heading_id}}}\n"
        elif tag.name == 'h3':
            heading_id = tag.get('id')
            markdown += f"### {tag.text} {{#{heading_id}}}\n"
        elif tag.name == 'p':
            markdown += f"{tag.text}\n"
        elif tag.name == 'ul':
            for li in tag.find_all('li'):
                markdown += f"- {li.text}\n"

    return markdown


input_str = "Decap CMS {#h.cr6m3db2r43y}"

# Extract the ID within {#} using regex
match = re.search(r'\{#([^}]+)\}', input_str)
if match:
    extracted_id = match.group(1)
    # Remove {#...} from the string
    modified_str = input_str.replace(match.group(0), '')
    print("Extracted ID:", extracted_id)
    print("Modified String:", modified_str)
else:
    print("No ID found within {#}")


def main():

    # Replace with the actual Google Doc ID
    doc_id = "1SxTsELQQafYLNXU7q4dcgR-1K0XbX29i"
    html_content = fetch_google_doc(doc_id)
    markdown_content = convert_to_markdown(html_content)

    # print(markdown_content)


if __name__ == "__main__":
    main()
