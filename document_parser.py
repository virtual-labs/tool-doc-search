import markdown
import requests
import json
import re


class DocumentChunk:
    def __init__(self, heading, text, url, page_title):
        self.heading = heading
        self.text = text
        self.url = url
        self.page_title = page_title


################################################################


def remove_footer(page_md):
    return page_md.split("[Next ![]")[0]


def remove_header(page_md):
    md_lines = page_md.split("\n")

    body_lines = []
    in_body = False
    for mdl in md_lines:
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

################################################################


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

################################################################


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


def parse_markdown_from_github(github_url):
    response = requests.get(github_url)
    markdown_content = response.text
    return markdown_content


def extract_first_heading(markdown_content):
    lines = markdown_content.split('\n')
    for line in lines:
        if line.startswith('#'):
            return line[1:].strip()
    return "Untitled"


def extract_sections(markdown_content):
    sections = []
    lines = markdown_content.split('\n')
    current_section = {"heading": None, "content": ""}

    for line in lines:
        if line.startswith('#'):
            if current_section["heading"] is not None:
                sections.append(current_section)
            current_section = {"heading": line[1:].strip(), "content": ""}
        else:
            current_section["content"] += line + '\n'

    if current_section["heading"] is not None:
        sections.append(current_section)

    return sections


def generate_document_chunks(sections, base_github_url, page_title):
    chunks = []

    for section in sections:
        heading = section["heading"].replace("#", "").replace(":", "").strip()
        cleaned_content = section["content"].replace(
            "\_", "_").replace("\*", "*").strip()
        hash = heading.replace(' ', '-').lower()
        hash = hash[1:] if hash[0] == '-' else hash
        github_url_with_anchor = f"{base_github_url}#{hash}"
        chunk = DocumentChunk(
            heading, heading + " :: " + page_title + " :: " + cleaned_content, github_url_with_anchor, page_title)
        if cleaned_content:
            chunks.append(chunk)

    return chunks


def get_chunks(url):

    github_raw_url = url.replace("https://github.com",
                                 "https://raw.githubusercontent.com").replace("http://github.com",
                                                                              "https://raw.githubusercontent.com").replace("/blob/", "/")

    markdown_content = parse_markdown_from_github(github_raw_url)
    markdown_content = parse_page_markdown(markdown_content)
    page_title = extract_first_heading(markdown_content)
    sections = extract_sections(markdown_content)
    chunks = generate_document_chunks(sections, url, page_title)
    data = []
    for chunk in chunks:
        data.append({
            "content": chunk.text,
            "payload": {
                "page_title": chunk.page_title,
                "heading": chunk.heading,
                "text": chunk.text,
                "url": chunk.url
            }
        })
    return data


def get_chunks_from_github(*url_list):
    data = []
    for url in url_list:
        chunks = get_chunks(url)
        for chunk in chunks:
            data.append(chunk)
    print(data)
    return data


# if __name__ == "__main__":
#     url = "https://github.com/virtual-labs/app-exp-create-web/blob/master/docs/user-doc.md"
#     get_chunks_from_github(url)
