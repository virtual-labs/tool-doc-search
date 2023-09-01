from dotenv import load_dotenv
from flask import Flask, request, jsonify
from utils.doc_search import DocumentSearch
from error.handler import bad_request_error
import os

app = Flask(__name__)


@app.route('/')
def index():
    return "<h1>DocSearch API</h1>"


@app.route('/api/insert', methods=['POST'])
def insert():
    type = ""
    url = ""
    data = request.json
    if "type" not in data:
        return bad_request_error("Please provide document type (md, gdoc)")
    if data["type"] != "md" and data["type"] != "gdoc":
        return bad_request_error("Please provide document type (md, gdoc)")
    if "url" not in data:
        return '''
        Please provide document url in format
        gdoc - https://docs.google.com/document/d/{GOOGLE_DOC_ID}
        md - https://github.com/{GITHUB_ORG_NAME}/{REPOSITORY_NAME}/blob/{BRANCH}/{PATH_TO_MD_DOC}
        ''', 400
    type = data["type"]
    url = data["url"]
    chunks = doc_search.insert_doc(type=type,
                                   url=url)
    return jsonify({"message": "Document inserted successfully", "chunks_count": len(chunks)})


@app.route('/api/search', methods=['POST'])
def search():
    limit = 10
    thresh = 0.2
    doc_filter = "Any"
    page_title_filter = ""

    data = request.json

    if "search_query" not in data:
        return bad_request_error("Please enter search query")
    if (type(data["search_query"])) != str:
        return bad_request_error("search query must be string")
    if "limit" in data:
        if (type(data["limit"])) != int:
            return bad_request_error("limit must be integer")
        limit = data["limit"]
    if "thresh" in data:
        if (type(data["thresh"])) != float:
            return bad_request_error("thresh must be float")
        thresh = data["thresh"]
    if "doc_filter" in data:
        if data["doc_filter"] != "md" and data["doc_filter"] != "gdoc":
            return bad_request_error("doc_filter must be 'md' or 'gdoc'")
        doc_filter = data["doc_filter"]
    if "page_title_filter" in data:
        if (type(data["page_title_filter"])) != str:
            return bad_request_error("page_title_filter  must be string")
        page_title_filter = data["page_title_filter"]

    # print(data["search_query"], thresh, limit, page_title_filter, doc_filter)
    result = doc_search.get_search_result(
        search_query=data["search_query"],
        limit=limit,
        thresh=thresh,
        doc_filter=doc_filter,
        page_title_filter=page_title_filter,)

    return {"hits": len(result), "result": result}


@app.errorhandler(404)
def not_found_error(error):
    return "<h1>Route doesn't exist</h1>", 404


if __name__ == '__main__':
    load_dotenv()
    global doc_search
    doc_search = DocumentSearch(url=os.getenv("QDRANT_URL"),
                                api_key=os.getenv("QDRANT_API"),
                                collection_name=os.getenv("QDRANT_COLLECTION"))
    app.run()
