DOCUMENT_TYPES = [
    {"type": "Any"},
    {"type": "md"},
    {"type": "org"},
    {"type": "gdoc"},
    {"type": "xlsx"},
    {"type": "github"},
    {"type": "drive"},
    {"type": "unknown"},
]


def is_valid_doc_type(doc_type):
    for dtype in DOCUMENT_TYPES:
        if dtype.get("type", None) == doc_type:
            return True
    return False
