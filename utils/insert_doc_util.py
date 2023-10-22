from error.CustomException import BadRequestException, CustomException


def insert_document(link, document_type, credentials, name, doc_search):
    try:
        if document_type != "md" and document_type != "gdoc":
            raise BadRequestException(
                "Please provide document type (md, gdoc)")
        chunks = doc_search.insert_doc(type=document_type,
                                       url=link, credentials=credentials, user=name)
        return ({"message": "Document(s) upserted successfully", "chunks_count": len(chunks),
                 "page_title": chunks[0]["payload"]["page_title"] if len(chunks) else "No title",
                 "accessibility": chunks[0]["payload"]["accessibility"]})
    except CustomException as e:
        return ({'error': 'An error occurred', 'message': str(e), 'status_code': e.status_code})
    except Exception as e:
        return ({'error': 'An unexpected error occurred', 'message': str(e), 'status_code': 500})


def insert_document_batch(docs, credentials, name, doc_search, operation="insert"):
    try:
        result = doc_search.insert_doc_batch(
            docs=docs, credentials=credentials, user=name, operation=operation)
        return result
    except CustomException as e:
        return ({'error': 'An error occurred', 'message': str(e), 'status_code': e.status_code})
    except Exception as e:
        return ({'error': 'An unexpected error occurred', 'message': str(e), 'status_code': 500})
