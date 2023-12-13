import requests
import re
from bs4 import BeautifulSoup
from error.CustomException import NotFoundException, BadRequestException
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gspread
import os
import pathlib
import io
import uuid
from llmsherpa.readers import LayoutPDFReader
import PyPDF2


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


def get_payload(page_title, heading, text, url, type, base_url, user, src="web"):
    return {
        "page_title": page_title.strip(),
        "heading": heading.strip(),
        "text": text.strip(),
        "url": url.strip(),
        "type": type.strip(),
        "base_url": base_url.strip(),
        "src": src.strip()
    }


def get_point(text, page_title, heading, url, type, base_url, user, src="web"):
    return {
        "content": text.strip(),
        "payload": get_payload(page_title, heading, text, url, type, base_url, user, src)
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
    response = requests.get(url, headers={
        "Authorization": f"Bearer {credentials.token}"
    })
    if response.status_code == 404:
        raise NotFoundException("Document not found. Invalid document link")
    elif response.status_code == 401:
        raise NotFoundException("Unauthorized access. Invalid credentials")
    print(f"Fetching markdown from google doc with id {doc_id}")
    return convert_to_markdown(response.content)


def fetch_google_sheet_private(doc_id, credentials, user, page_title=""):
    print("Strated extracting")
    client = gspread.authorize(credentials)
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
                      chunk.heading, chunk.url, type, url, user,
                      src="drive")
        )
    return data


def get_chunks_from_xlsx(url, credentials, user, page_title=""):
    if url.endswith("/"):
        url = url[:-1]
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    print(f"Getting accessiblility of {url} ")
    if match:
        doc_id = match.group(1)
        url = get_formatted_google_url(doc_id, "xlsx")
        meta_data = fetch_metadata_gdrive(doc_id)
        accessibility = meta_data.get("accessibility")
        print(f"Accessiblility of {url} is {accessibility}")
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


def get_chunks_from_markdown(markdown_content, url, type, user, page_title="", src="web"):
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
                      chunk.heading, chunk.url, type, url, user, src)
        )
    return data


def extract_org_title(org_text):
    document_title = None
    title_match = re.search(r'^\s*#\+title:(.*)', org_text, re.I | re.M)
    if title_match:
        document_title = title_match.group(1).strip()
    else:
        document_title = None
    return document_title


def get_chunks_from_org(org_content, url, type, user, page_title=""):
    print("Extracting headings from org")

    page_title = page_title if page_title != "" else extract_org_title(
        org_content)
    if page_title is None:
        raise BadRequestException("Provide page title for unknown ORG doc.")
    sections = extract_sections_org(org_content)
    print("Generating chunks from org")
    chunks = generate_document_chunks(sections, url, page_title, type)
    data = []
    for chunk in chunks:
        data.append(
            get_point(chunk.text, chunk.page_title,
                      chunk.heading, chunk.url, type, url, user, src="github")
        )
    return data


def get_formatted_google_url(doc_id, type):
    if type == "gdoc":
        return f'https://docs.google.com/document/d/{doc_id}'
    elif type == "xlsx":
        return f'https://docs.google.com/spreadsheets/d/{doc_id}'
    elif type == 'drive':
        return f'https://drive.google.com/file/d/{doc_id}'
    elif type == "folder":
        return f'https://drive.google.com/drive/u/0/folders/{doc_id}'
    return f'https://drive.google.com/file/d/{doc_id}'


def get_github_accessibility_with_content(raw_url):
    access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get(raw_url)
    if response.status_code == 200:
        return "public", response.text
    elif response.status_code == 404:
        response = requests.get(raw_url, headers=headers)
        if response.status_code == 200:
            return "private", response.text
        else:
            raise NotFoundException(
                "Document not found. Invalid document link")
    else:
        raise Exception("Error occurred while fetching document")


def get_chunks_from_md_github(url, user, page_title=""):
    if not url.endswith("md"):
        raise BadRequestException(f'Invalid url format {url}')
    github_raw_url = url.replace("https://github.com",
                                 "https://raw.githubusercontent.com").replace("http://github.com",
                                                                              "https://raw.githubusercontent.com").replace("/blob/", "/")

    print(f"Fetching markdown from {github_raw_url}")

    access, markdown_content = get_github_accessibility_with_content(
        github_raw_url)

    print(f"Markdown fetched from {github_raw_url}")
    data = get_chunks_from_markdown(
        markdown_content, url, "md", user, page_title, src="github")
    newdata = []
    for chunk in data:
        chunk["payload"]["accessibility"] = access
        newdata.append(chunk)
    return newdata


def get_chunks_from_org_github(url, user, page_title=""):
    if not url.endswith("org"):
        raise BadRequestException(f'Invalid url format {url}')
    github_raw_url = url.replace("https://github.com",
                                 "https://raw.githubusercontent.com").replace("http://github.com",
                                                                              "https://raw.githubusercontent.com").replace("/blob/", "/")
    print(f"Fetching ORG from {github_raw_url}")
    access, markdown_content = get_github_accessibility_with_content(
        github_raw_url)
    print(f"ORG fetched from {github_raw_url}")
    data = get_chunks_from_org(
        markdown_content, url, "org", user, page_title)
    newdata = []
    for chunk in data:
        chunk["payload"]["accessibility"] = access
        newdata.append(chunk)
    return newdata


def get_chunks_from_github(url, user, page_title=""):
    # if page_title.strip() == "":
    #     raise Exception("Provide page title for unknown GitHub doc.")
    github_raw_url = url.replace("https://github.com",
                                 "https://raw.githubusercontent.com").replace("http://github.com",
                                                                              "https://raw.githubusercontent.com").replace("/blob/", "/")
    print(f"Fetching GitHub content from {github_raw_url}")
    access, content = get_github_accessibility_with_content(github_raw_url)
    print(f"Content fetched from {github_raw_url}")
    newdata = []
    data = []
    data.append(
        get_point(page_title+"::"+page_title+"::"+content, page_title,
                  page_title, url, "github", url, user, src="github")
    )
    for chunk in data:
        chunk["payload"]["accessibility"] = access
        newdata.append(chunk)
    return newdata


def get_gdoc_accessiblility(link, document_id=""):
    meta_data = fetch_metadata_gdrive(document_id)
    accessibility = meta_data.get("accessibility")
    return accessibility


def get_chunks_from_gdoc(url, credentials, user, page_title=""):
    if url.endswith("/"):
        url = url[:-1]
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    print(f"Getting accessiblility of {url} ")
    if match:
        doc_id = match.group(1)
        url = get_formatted_google_url(doc_id, "gdoc")
        accessibility = get_gdoc_accessiblility(document_id=doc_id, link=url)
        print(f"Accessiblility of {url} is {accessibility}")
        markdown_content = ""
        print(f"Fetching google doc {url}")
        if accessibility == "public":
            markdown_content = fetch_google_doc(doc_id)
        elif accessibility == "private":
            markdown_content = fetch_google_doc_private(doc_id, credentials)
        print(f"Markdown fetched from google doc {url}")
        data = get_chunks_from_markdown(
            markdown_content, url, "gdoc", user, page_title, src="drive")

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


def extract_pdf_sections(file_name):

    def remove_unicode(input_string):
        return re.sub(r'[^\x00-\x7F]', ' ', input_string)

    def get_page_number(lst, current_page=0):
        for s in lst:
            pattern = re.compile(re.escape(s), re.IGNORECASE)
            for i in range(current_page, pgno):
                text = pageText[i]
                if pattern.search(text):
                    current_page = i
                    return i
        return current_page

    def is_valid_heading(heading, text):

        filter1 = heading != text
        filter3 = "=" not in heading
        filter4 = (heading[0] != '(' and heading[-1] != ')')

        filters = [filter1, filter3, filter4]

        return all(filters)

    llmsherpa_api_url = "https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"
    pdf_url = file_name

    obj = PyPDF2.PdfReader(file_name)
    pdf_reader = LayoutPDFReader(llmsherpa_api_url)

    print("Started processing pdf")
    doc = pdf_reader.read_pdf(pdf_url)
    print("Completed pdf processing")

    current_page = 0
    pages = obj.pages
    pgno = len(pages)

    pageText = [pages[i].extract_text() for i in range(0, pgno)]

    sections = []
    print("Started generating sections", len(doc.sections()))
    for _, section in enumerate(doc.sections()):

        title = (remove_unicode(section.title)).strip()
        text = remove_unicode(section.to_text(
            include_children=True, recurse=True).strip())

        # print(json.dumps(
        #     {"title": title, "text": text}, indent=4))

        if is_valid_heading(title, text):
            lines = [t.strip() for t in text.split("\n")[0:10]]
            current_page = get_page_number(lines[:4], current_page)
            trimmed_text = "\n".join(text.split("\n")[1:])

            sections.append(
                {"title": title, "text": trimmed_text, "page": current_page+1})

    print("Sections generated")
    return sections


def generate_pdf_chunks(sections, base_url, page_title, type, user="unknown", accessibility="public"):
    chunks = []
    for section in sections:
        heading = section.get("title", "Untitled").strip()
        cleaned_content = section.get("text", "text").strip()
        link = base_url + f"#page={section.get('page')}"
        chunk = DocumentChunk(
            heading, f"{heading} of {page_title} :: {page_title} :: {cleaned_content}",
            link, page_title)
        chunks.append(chunk)
    data = []
    for chunk in chunks:
        point = get_point(chunk.text, chunk.page_title,
                          chunk.heading, chunk.url, type, base_url, user, src="drive")
        point["payload"]["accessibility"] = accessibility
        data.append(
            point
        )
    return data


def get_google_permissions(doc_id, credentials):
    service = build('drive', 'v3', credentials=credentials)
    permission_id = 'anyoneWithLink'
    permissions = service.permissions().get(
        fileId=doc_id, permissionId=permission_id).execute()

    print(json.dumps(permissions, indent=4))
    file = service.files().get(
        fileId=doc_id, fields='id, name, shared, permissions').execute()
    if file.get('shared'):
        permissions = file.get('permissions', [])
        for p in permissions:
            if p.get('type') == 'anyone' and (p.get('role') == 'reader' or p.get('role') == 'writer'):
                return "public"
        else:
            return "private"
    else:
        return "private"


def fetch_metadata_gdrive(doc_id):
    print("Fetching metadata from google drive")
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = os.path.join(
        pathlib.Path(__file__).parent, "../secrets/service-account-secret.json")
    credentials = None
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials)

    file_metadata = service.files().get(fileId=doc_id).execute()

    try:
        print(doc_id)
        permissions = service.permissions().get(
            fileId=doc_id, permissionId="anyoneWithLink").execute()
        print(json.dumps(permissions, indent=4))
        if permissions.get("role") in ["reader", "writer", "editor", "viewer"]:
            file_metadata["accessibility"] = "public"
        else:
            file_metadata["accessibility"] = "private"
    except Exception as e:
        print(e)
        file_metadata["accessibility"] = "private"

    print("Metadata fetched from google drive")
    print(json.dumps(file_metadata, indent=4))
    return file_metadata


def download_pdf(service, doc_id):
    request = service.files().get_media(fileId=doc_id)
    fh = io.BytesIO()
    downloader = io.BytesIO(request.execute())
    fh.write(downloader.read())
    pdf_file_name = f'pdf_downloads/{uuid.uuid4().hex}.pdf'
    with open(pdf_file_name, 'wb') as f:
        f.write(fh.getvalue())
    print(f"{pdf_file_name} file downloaded successfully.")
    return pdf_file_name


def delete_pdf(file_name):
    print(f"Deleting downloaded {file_name}")
    if os.path.exists(file_name):
        os.remove(file_name)


def get_chunks_from_gdrive(url, credentials, user, page_title=""):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        doc_id = match.group(1)
        url = get_formatted_google_url(doc_id, "drive")
        service = build('drive', 'v3', credentials=credentials)

        meta_data = fetch_metadata_gdrive(
            doc_id)

        pdf_name = meta_data.get("name").replace(
            "-", " ").replace(".", " ").replace("pdf", "PDF")

        page_title = page_title if page_title != "" else pdf_name

        doc_type = meta_data.get("mimeType")

        print("meta data extracted")

        if doc_type != "application/pdf":

            print("Generating chunk for unknown drive format")
            new_doc_type = doc_type.split('/')[1]
            point = get_point(page_title, page_title,
                              page_title, url, new_doc_type, url, user, src="drive")
            point["payload"]["accessibility"] = meta_data.get("accessibility")
            return [point]
        else:
            pdf_file_name = download_pdf(service=service, doc_id=doc_id)
            pdf_sections = extract_pdf_sections(file_name=pdf_file_name)
            delete_pdf(file_name=pdf_file_name)
            return generate_pdf_chunks(pdf_sections, url, page_title=page_title, type="pdf", user=user, accessibility=meta_data.get("accessibility"))
    return []


def get_doc_urls_from_drive(folder_url, credentials):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', folder_url)
    print(f"Getting accessiblility of {folder_url} ")
    if match:
        doc_id = match.group(1)
        folder_url = get_formatted_google_url(doc_id, "folder")
        print(doc_id)
        meta_data = fetch_metadata_gdrive(doc_id)
        name = meta_data.get("name")
        accessibility = meta_data.get("accessibility")
        print(f"Accessiblility of {folder_url} is {accessibility}")
        type = meta_data.get("mimeType")
        if type == "application/vnd.google-apps.folder":
            print(f"Fetching files from google drive folder {folder_url}")
            service = build('drive', 'v3', credentials=credentials)
            results = service.files().list(
                q=f"'{doc_id}' in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
            items = results.get('files', [])
            if not items:
                print('No files found.')
            else:
                print('Files:')
                urls = []
                for item in items:
                    print(u'{0} ({1})'.format(item['name'], item['id']))
                    if item["mimeType"] != "application/vnd.google-apps.folder":
                        f_type = item["mimeType"].split('/')[1]
                        f_type = "xlsx" if f_type == "vnd.google-apps.spreadsheet" else f_type
                        f_type = "gdoc" if f_type == "vnd.google-apps.document" else f_type

                        if f_type == "xlsx":
                            urls.append(
                                {
                                    "url": f"https://docs.google.com/spreadsheets/d/{item['id']}",
                                    "page_title": item["name"],
                                    "type": f_type
                                }
                            )
                        elif f_type == "gdoc":
                            urls.append(
                                {
                                    "url": f"https://docs.google.com/document/d/{item['id']}",
                                    "page_title": item["name"],
                                    "type": f_type
                                }
                            )
                        else:
                            urls.append(
                                {
                                    "url": f"https://drive.google.com/file/d/{item['id']}",
                                    "page_title": item["name"],
                                    "type": f_type
                                }
                            )
                return urls, name, accessibility
        else:
            print("Invalid drive folder")
            raise Exception("Invalid drive folder id")
    else:
        raise Exception("Invalid drive folder")
    return []


def get_chunks_batch(docs, credentials, user):
    print("Getting batch")
    try:
        chunks = []
        base_urls = []
        document_parse_error_url = []
        doc_chunk_idx = []
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

                elif doc["type"] == "drive" or doc["url"].startswith("https://drive.google.com/file/d/"):
                    print("Getting chunks from g-drive")
                    chunk = get_chunks_from_gdrive(
                        doc["url"], credentials=credentials, user=user, page_title=doc["page_title"])

                elif doc["type"] == "link":
                    print("Generating chunk for unknown doc")
                    point = get_point(doc["page_title"], doc["page_title"],
                                      doc["page_title"], doc["url"], doc["type"], doc["url"], user)
                    point["payload"]["accessibility"] = "public"
                    chunk = [point]

                elif doc["type"] == "dir":
                    print("Generating chunk for unknown doc")
                    point = get_point(doc["page_title"], doc["page_title"],
                                      doc["page_title"], doc["url"], doc["type"], doc["url"], user, src="drive")
                    point["payload"]["accessibility"] = doc.get(
                        "accessibility", "public")
                    chunk = [point]

                if (len(chunk) == 0):
                    print("Generating chunk for unknown doc")
                    if doc["page_title"].strip() == "":
                        raise Exception("Provide page title for unknown doc.")
                    point = get_point(doc["page_title"], doc["page_title"],
                                      doc["page_title"], doc["url"], "link", doc["url"], user)
                    point["payload"]["accessibility"] = "public"
                    chunk = [point]

                l = len(chunks)
                for ch in chunk:
                    chunks.append(ch)

                doc_chunk_idx.append(
                    {"url": doc["url"], "l": l, "r": len(chunks)})

                base_urls.append(doc["url"])

            except Exception as e:
                print(e)
                document_parse_error_url.append(
                    {"url": doc["url"], "msg": str(e)})
                # raise Exception(
                #     f"Error occurred while parsing document {idx+1}, {str(e)}")

        print(f"Total document chunks generated {len(chunks)}")

        return chunks, base_urls, document_parse_error_url, doc_chunk_idx

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
