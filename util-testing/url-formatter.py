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
