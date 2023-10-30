import requests
import re
from bs4 import BeautifulSoup
from error.CustomException import NotFoundException, BadRequestException
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas as pd
import gspread
import os
import pathlib
import pandas as pd


class DocumentChunk:
    def __init__(self, heading, text, url, page_title):
        self.heading = heading
        self.text = text
        self.url = url
        self.page_title = page_title


###############################################################################################
# fiftyone-docs-search reference

def remove_footer(page_md):
    return page_md.split("[Next ![]")[0]


def remove_header(page_md):
    md_lines = page_md.split("\n")

    body_lines = []
    in_body = False
    for mdl in md_lines:
        mdl = mdl.strip()
        if len(mdl) > 0 and mdl[0] == "#":
            in_body = True
        if in_body:
            body_lines.append(mdl)
    page_md = "\n".join(body_lines)
    return page_md


def remove_line_numbers(page_md):
    lines = page_md.split('\n')
    lines = [
        re.sub(r'^\s*\d+\s*', '', line)
        for line in lines
    ]

    page_md = '\n'.join(lines)
    return page_md


def remove_table_rows(page_md):
    lines = page_md.split('\n')
    lines = [line
             for line in lines
             if len(line) == 0 or not set(line).issubset(set("| -"))
             ]
    page_md = '\n'.join(lines)
    return page_md


def remove_extra_newlines(page_md):
    page_md = re.sub(r'\n{3,}', '\n\n', page_md)
    return page_md


def remove_unicode(page_md):
    for uchar in ["\u2500", "\u2514", "\u251c", "\u2502"]:
        page_md = page_md.replace(uchar, "")
    for uchar in ["\u2588", "\u2019"]:
        page_md = page_md.replace(uchar, "'")
    for uchar in ["\u201d", "\u201c"]:
        page_md = page_md.replace(uchar, "\"")
    page_md = page_md.replace("\u00a9", "copyright")
    return page_md


def remove_bolding(page_md):
    page_md = page_md.replace("**", "")
    return page_md


def remove_empty_code_blocks(page_md):
    parts = page_md.split('```')
    parts = [
        p
        for i, p in enumerate(parts)
        if i % 2 == 0 or p != "\n"
    ]
    return "```".join(parts)


def remove_links(page_md):
    match = re.search('\[.*?\]\(.*?\)', page_md)
    if match is not None:
        start, end = match.span()
        link = page_md[start:end]
        link_text = link[1:].split(']')[0]
        if link_text != "¶":
            return page_md[:start] + link_text + remove_links(page_md[end:])
        else:
            return page_md[:end] + link + remove_links(page_md[end:])
    return page_md


def remove_images(page_md):
    return re.sub('!\[\]\(data:image\/png;base64.*?\)', '', page_md)


def remove_jupyter_widgets(page_md):
    lines = page_md.split('\n')
    lines = [
        line
        for line in lines
        if len(line) == 0 or (line[0] != "{" and "jupyter-widgets" not in line)
    ]
    return "\n".join(lines)


def remove_xml(page_md):
    lines = page_md.split('\n')
    lines = [line for line in lines if not line.startswith('<?xml')]
    return "\n".join(lines)


def reformat_markdown(page_md):
    page_md = page_md.replace("\_", "_").replace("\*", "*")
    page_md = remove_links(page_md)
    page_md = remove_images(page_md)
    page_md = remove_jupyter_widgets(page_md)
    page_md = remove_xml(page_md)
    return page_md


def parse_page_markdown(page_md):
    page_md = remove_header(page_md)
    page_md = remove_footer(page_md)
    page_md = remove_line_numbers(page_md)
    page_md = remove_table_rows(page_md)
    page_md = remove_extra_newlines(page_md)
    page_md = remove_empty_code_blocks(page_md)
    page_md = remove_extra_newlines(page_md)
    page_md = remove_bolding(page_md)
    page_md = remove_unicode(page_md)

    # reformat now that the markdown is clean
    page_md = reformat_markdown(page_md)
    return page_md

###############################################################################################


def get_payload(page_title, heading, text, url, type, base_url, user):
    return {
        "page_title": page_title.strip(),
        "heading": heading.strip(),
        "text": text.strip(),
        "url": url.strip(),
        "type": type.strip(),
        "base_url": base_url.strip(),
    }


def get_point(text, page_title, heading, url, type, base_url, user):
    return {
        "content": text.strip(),
        "payload": get_payload(page_title, heading, text, url, type, base_url, user)
    }


def fetch_content_from_github(github_url):
    response = requests.get(github_url)
    if response.status_code == 404:
        raise NotFoundException("Document not found. Invalid document link")
    markdown_content = response.text
    return markdown_content


def fetch_google_doc(doc_id):
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
    response = requests.get(url)
    if response.status_code == 404:
        raise NotFoundException("Document not found. Invalid document link")
    print(f"Fetching markdown from google doc with id {doc_id}")
    return convert_to_markdown(response.content)


def fetch_google_doc_private(doc_id, credentials):
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
    response = requests.get(url)
    service = build('drive', 'v3', credentials=credentials)
    request = service.files().export(fileId=doc_id, mimeType='text/html')
    response = request.execute()
    print(f"Fetching markdown from google doc with id {doc_id}")
    return convert_to_markdown(response.decode('utf-8'))


def fetch_google_sheet(doc_id):
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
    response = requests.get(url)
    if response.status_code == 404:
        raise NotFoundException("Document not found. Invalid document link")
    print(f"Fetching markdown from google doc with id {doc_id}")
    return convert_to_markdown(response.content)


def fetch_google_sheet_private(doc_id, credentials, user, page_title=""):
    print("Strated extracting")
    GSHEET_SECRET = json.load(open(os.path.join(
        pathlib.Path(__file__).parent, "g-sheet-secret.json")))
    credentials = service_account.Credentials.from_service_account_info(
        GSHEET_SECRET)
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly',
             'https://www.googleapis.com/auth/drive.readonly']
    creds_with_scope = credentials.with_scopes(scope)
    client = gspread.authorize(creds_with_scope)
    print("gspread authorized")
    spreadsheet = client.open_by_url(
        f'https://docs.google.com/spreadsheets/d/{doc_id}/edit#gid=0')

    page_title = page_title if page_title != "" else spreadsheet.title

    worksheets = spreadsheet.worksheets()
    gsheet = []
    for worksheet in worksheets:
        sheet_title = worksheet.title
        worksheet_gid = worksheet.id
        print(f"Reading data from {sheet_title}:")
        data = worksheet.get_values("A1:Z10")
        gsheet.append({"sheet_title": sheet_title,
                      "sheet_id": worksheet_gid, "content": json.dumps(data)})
    return page_title, gsheet


def generate_worksheet_chunks(sections, base_url, page_title):
    chunks = []
    for section in sections:
        heading = section["sheet_title"].strip()
        link = base_url + "/edit#gid=" + str(section["sheet_id"])
        chunk = DocumentChunk(
            heading, f"{heading} of {page_title} :: {page_title} :: {section['content']}",
            link, page_title)
        chunks.append(chunk)
    return chunks


def get_chunks_from_sheet(worksheet_data, url, type, user, page_title):
    chunks = generate_worksheet_chunks(worksheet_data, url, page_title)
    data = []
    for chunk in chunks:
        data.append(
            get_point(chunk.text, chunk.page_title,
                      chunk.heading, chunk.url, type, url, user)
        )
    return data


def get_chunks_from_xlsx(url, credentials, user, page_title=""):
    if url.endswith("/"):
        url = url[:-1]
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    print(f"Getting accessiblility of {url} ")
    accessibility = "private"
    print(f"Accessiblility of {url} is {accessibility}")
    if match:
        doc_id = match.group(1)
        print(f"Fetching google sheet {url}")
        spreadsheet_title, worksheets = fetch_google_sheet_private(
            doc_id, credentials, user, page_title)
        print(f"Worksheets fetched from google sheet {url}")
        print("Start generating chunks")
        data = get_chunks_from_sheet(
            worksheets, url, "xlsx", user, spreadsheet_title)
        print("Chunks generated")
        newdata = []
        for d in data:
            newpayload = d["payload"]
            newpayload["accessibility"] = accessibility
            newdata.append({
                "content": d["content"],
                "payload": newpayload
            })
        return newdata
    else:
        print("No ID found in the URL")


def convert_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    markdown = ""

    for tag in soup.find_all():
        if tag.name == 'h1':
            heading_id = tag.get('id')
            markdown += f"# {tag.text} {{#{heading_id}}}\n"
        elif tag.name == 'h2':
            heading_id = tag.get('id')
            markdown += f"# {tag.text} {{#{heading_id}}}\n"
        elif tag.name == 'h3':
            heading_id = tag.get('id')
            markdown += f"# {tag.text} {{#{heading_id}}}\n"
        elif tag.name == 'p':
            markdown += f"{tag.text}\n"
        elif tag.name == 'ul':
            for li in tag.find_all('li'):
                markdown += f"- {li.text}\n"
        else:
            markdown += f"{tag.text}\n"

    return markdown


def extract_first_heading(markdown_content, type):
    lines = markdown_content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            match = re.search(r'\{#([^}]+)\}', line)
            if match:
                # print(line.replace(match.group(0), '').strip())
                return line.replace(match.group(0), '').replace("#", "").strip()
            return line[1:].replace("#", "").strip()
    return "Untitled"


def extract_sections(markdown_content):
    sections = []
    lines = markdown_content.split('\n')
    current_section = {"heading": None, "content": ""}

    for line in lines:
        line = line.strip()
        tokens = line.split(' ')
        if tokens[0] == '#' or tokens[0] == '##':
            if current_section["heading"] is not None:
                sections.append(current_section)
            current_section = {"heading": " ".join(tokens[1:]), "content": ""}
        else:
            current_section["content"] += line + '\n'

    if current_section["heading"] is not None:
        sections.append(current_section)
    # print(json.dumps(sections, indent=4))
    return sections


def extract_sections_org(markdown_content):
    sections = []
    lines = markdown_content.split('\n')
    current_section = {"heading": None, "content": ""}

    for line in lines:
        line = line.strip()
        # print(line)
        tokens = line.split(' ')
        if tokens[0] == '*' or tokens[0] == '**':
            if current_section["heading"] is not None:
                sections.append(current_section)
            # print(tokens)
            current_section = {"heading": " ".join(tokens[1:]), "content": ""}
        else:
            current_section["content"] += line + '\n'

    if current_section["heading"] is not None:
        sections.append(current_section)
    # print(json.dumps(sections, indent=4))
    return sections


def get_google_doc_heading_id(heading):
    match = re.search(r'\{#([^}]+)\}', heading)
    if match:
        extracted_id = match.group(1)
        modified_str = heading.replace(match.group(0), '')
        return extracted_id, modified_str
    return None


def get_link_hash(base_url, heading, type):
    if type == "gdoc":
        match = re.search(r'\{([^}]+)\}', heading)
        if match:
            extracted_id = match.group(1)
            modified_heading = heading.replace(match.group(0), '')
            gdoc_url_with_anchor = f"{base_url}#heading={extracted_id}"
            return modified_heading, gdoc_url_with_anchor
    elif type == "md" or type == "org":
        hash = heading.replace(' ', '-').replace('.',
                                                 '-').replace('--', '-').lower()
        hash = hash[1:] if hash[0] == '-' else hash
        github_url_with_anchor = f"{base_url}#{hash}"
        return heading, github_url_with_anchor
    return "", ""


def generate_document_chunks(sections, base_url, page_title, type):
    chunks = []
    for section in sections:
        heading = section["heading"].replace("#", "").replace(":", "").strip()
        cleaned_content = section["content"].replace(
            "\_", "_").replace("\*", "*").replace('*', "").strip()
        heading, link = get_link_hash(base_url, heading, type)
        chunk = DocumentChunk(
            heading, f"{heading} of {page_title} :: {page_title} :: {cleaned_content}",
            link, page_title)
        if cleaned_content:
            chunks.append(chunk)

    return chunks


def get_chunks_from_markdown(markdown_content, url, type, user, page_title=""):
    print("Extracting headings from markdown")
    markdown_content = parse_page_markdown(markdown_content)

    page_title = page_title if page_title != "" else extract_first_heading(
        markdown_content, type)

    sections = extract_sections(markdown_content)
    print("Generating chunks from markdown")
    chunks = generate_document_chunks(sections, url, page_title, type)
    data = []
    for chunk in chunks:
        data.append(
            get_point(chunk.text, chunk.page_title,
                      chunk.heading, chunk.url, type, url, user)
        )
    return data


def extract_org_title(org_text):
    document_title = "Untitled Document"
    title_match = re.search(r'^\s*#\+title:(.*)', org_text, re.I | re.M)
    if title_match:
        document_title = title_match.group(1).strip()
    else:
        document_title = "Untitled Document"
    return document_title


def get_chunks_from_org(org_content, url, type, user, page_title=""):
    print("Extracting headings from org")

    page_title = page_title if page_title != "" else extract_org_title(
        org_content)

    sections = extract_sections_org(org_content)
    print("Generating chunks from org")
    chunks = generate_document_chunks(sections, url, page_title, type)
    data = []
    for chunk in chunks:
        data.append(
            get_point(chunk.text, chunk.page_title,
                      chunk.heading, chunk.url, type, url, user)
        )
    return data


def get_chunks_from_md_github(url, user, page_title=""):
    if not url.endswith("md"):
        raise BadRequestException(f'Invalid url format {url}')
    github_raw_url = url.replace("https://github.com",
                                 "https://raw.githubusercontent.com").replace("http://github.com",
                                                                              "https://raw.githubusercontent.com").replace("/blob/", "/")
    print(f"Fetching markdown from {github_raw_url}")
    markdown_content = fetch_content_from_github(github_raw_url)
    print(f"Markdown fetched from {github_raw_url}")
    data = get_chunks_from_markdown(
        markdown_content, url, "md", user, page_title)
    newdata = []
    for chunk in data:
        chunk["payload"]["accessibility"] = "public"
        newdata.append(chunk)
    return newdata


def get_chunks_from_org_github(url, user, page_title=""):
    if not url.endswith("org"):
        raise BadRequestException(f'Invalid url format {url}')
    github_raw_url = url.replace("https://github.com",
                                 "https://raw.githubusercontent.com").replace("http://github.com",
                                                                              "https://raw.githubusercontent.com").replace("/blob/", "/")
    print(f"Fetching ORG from {github_raw_url}")
    markdown_content = fetch_content_from_github(github_raw_url)
    print(f"ORG fetched from {github_raw_url}")
    data = get_chunks_from_org(
        markdown_content, url, "org", user, page_title)
    newdata = []
    for chunk in data:
        chunk["payload"]["accessibility"] = "public"
        newdata.append(chunk)
    return newdata


def get_chunks_from_github(url, user, page_title=""):
    # if page_title.strip() == "":
    #     raise Exception("Provide page title for unknown GitHub doc.")
    github_raw_url = url.replace("https://github.com",
                                 "https://raw.githubusercontent.com").replace("http://github.com",
                                                                              "https://raw.githubusercontent.com").replace("/blob/", "/")
    print(f"Fetching GitHub content from {github_raw_url}")
    content = fetch_content_from_github(github_raw_url)
    print(f"Content fetched from {github_raw_url}")
    newdata = []
    data = []
    data.append(
        get_point(content, page_title,
                  page_title, url, "github", url, user)
    )
    for chunk in data:
        chunk["payload"]["accessibility"] = "public"
        newdata.append(chunk)
    return newdata


def get_gdoc_accessiblility(link, document_id=""):
    viewer_url = f'https://docs.google.com/document/d/{document_id}/export?format=html'
    response = requests.get(link)
    if 'ServiceLogin' in response.url:
        return "private"
    elif response.status_code == 200:
        return "public"
    elif response.status_code == 404:
        raise NotFoundException("Document not found. Invalid document link")
    return None


def get_chunks_from_gdoc(url, credentials, user, page_title=""):
    if url.endswith("/"):
        url = url[:-1]
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    print(f"Getting accessiblility of {url} ")
    accessibility = get_gdoc_accessiblility(url)
    print(f"Accessiblility of {url} is {accessibility}")
    if match:
        doc_id = match.group(1)
        markdown_content = ""
        print(f"Fetching google doc {url}")
        if accessibility == "public":
            markdown_content = fetch_google_doc(doc_id)
        elif accessibility == "private":
            markdown_content = fetch_google_doc_private(doc_id, credentials)
        print(f"Markdown fetched from google doc {url}")
        data = get_chunks_from_markdown(
            markdown_content, url, "gdoc", user, page_title)

        newdata = []
        for d in data:
            newpayload = d["payload"]
            newpayload["text"] = "" if accessibility == "private" else newpayload["text"]
            newpayload["accessibility"] = accessibility
            newdata.append({
                "content": d["content"],
                "payload": newpayload
            })
        return newdata
    else:
        print("No ID found in the URL")


def get_chunks_batch(docs, credentials, user):
    print("Getting batch")
    try:
        chunks = []
        base_urls = []
        for idx, doc in enumerate(docs):
            try:
                print(
                    f"Getting chunks from document {idx+1} with url {doc['url']}")
                chunk = []
                if doc["type"] == "md":
                    print("Getting chunks from github")
                    chunk = get_chunks_from_md_github(
                        doc["url"], user, page_title=doc["page_title"])
                elif doc["type"] == "gdoc":
                    print("Getting chunks from google doc")
                    chunk = get_chunks_from_gdoc(
                        doc["url"], credentials, user, page_title=doc["page_title"])
                elif doc["type"] == "xlsx":
                    print("Getting chunks from google sheets")
                    chunk = get_chunks_from_xlsx(
                        doc["url"], credentials, user, page_title=doc["page_title"])
                elif doc["type"] == "org":
                    print("Getting chunks from github")
                    chunk = get_chunks_from_org_github(
                        doc["url"], user, page_title=doc["page_title"])
                elif doc["type"] == "github":
                    print("Getting chunks from github")
                    chunk = get_chunks_from_github(
                        doc["url"], user, page_title=doc["page_title"])
                elif doc["type"] == "unknown":
                    print("Generating chunk for unknown doc")
                    point = get_point(doc["page_title"], doc["page_title"],
                                      doc["page_title"], doc["url"], "unknown", doc["url"], user)
                    point["payload"]["accessibility"] = "public"
                    chunk = [point]
                if (len(chunk) == 0):
                    raise Exception(
                        f"No headings found while parsing document {idx+1}")
                for ch in chunk:
                    chunks.append(ch)
                base_urls.append(doc["url"])
            except Exception as e:
                raise Exception(
                    f"Error occurred while parsing document {idx+1}, {str(e)}")
        print(f"Total document chunks generated {len(chunks)}")
        return chunks, base_urls
    except Exception as e:
        raise e


if __name__ == "__main__":
    restult, base = get_chunks_batch([{
        "type": "md",
        "url": "https://github.com/virtual-labs/engineers-forum/blob/master/ph4/services/onboarding-hosting-process.md"
    }], {}, "user")
    print(json.dumps(restult, indent=4))
    pass
    # get_chunks(
    #     {
    #         "url": "https://docs.google.com/document/d/1ye4X5LcUlicv4Q-VE7pxYrjW8yj0Uep6EO3gZpR4SDw/",
    #         "type": "gdoc"
    #     },
    #     # {
    #     #     "url": "https://github.com/virtual-labs/app-exp-create-web/blob/master/docs/developer-doc.md",
    #     #     "type": "md"
    #     # }
    # )
