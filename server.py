from dotenv import load_dotenv
from flask import Flask, request, jsonify
from utils.doc_search import DocumentSearch
from error.CustomException import CustomException, BadRequestException
import os
from blueprints.insert_doc import insert_doc
import uuid

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex

load_dotenv()
doc_search = DocumentSearch(url=os.getenv("QDRANT_URL"),
                            api_key=os.getenv("QDRANT_API"),
                            collection_name=os.getenv("QDRANT_COLLECTION"))


@app.route('/')
def index():
    return "<h1>DocSearch API</h1>"


# @app.route('/api/insert', methods=['POST'])
# def insert():
#     try:
#         type = ""
#         url = ""
#         data = request.json
#         if "type" not in data:
#             raise BadRequestException(
#                 "Please provide document type (md, gdoc)")
#         if data["type"] != "md" and data["type"] != "gdoc":
#             raise BadRequestException(
#                 "Please provide document type (md, gdoc)")
#         if "url" not in data:
#             raise BadRequestException('''
#             Please provide document url in format
#             gdoc - https://docs.google.com/document/d/{GOOGLE_DOC_ID}
#             md - https://github.com/{GITHUB_ORG_NAME}/{REPOSITORY_NAME}/blob/{BRANCH}/{PATH_TO_MD_DOC}
#             ''')
#         type = data["type"]
#         url = data["url"]
#         chunks = doc_search.insert_doc(type=type,
#                                        url=url)
#         return jsonify({"message": "Document inserted successfully", "chunks_count": len(chunks)})
#     except CustomException as e:
#         return jsonify({'error': 'An error occurred', 'message': str(e), 'status_code': e.status_code}), e.status_code
#     except Exception as e:
#         return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search():
    try:
        limit = 10
        thresh = 0.2
        doc_filter = "Any"
        page_title_filter = ""

        data = request.json

        if "search_query" not in data:
            raise BadRequestException("Please enter search query")
        if (type(data["search_query"])) != str:
            raise BadRequestException("search query must be string")
        if "limit" in data:
            if (type(data["limit"])) != int:
                return BadRequestException("limit must be integer")
            limit = data["limit"]
        if "thresh" in data:
            if (type(data["thresh"])) != float:
                raise BadRequestException("thresh must be float")
            thresh = data["thresh"]
        if "doc_filter" in data:
            if data["doc_filter"] != "md" and data["doc_filter"] != "gdoc" and data["doc_filter"] != "Any":
                raise BadRequestException(
                    "doc_filter must be 'md' or 'gdoc' or 'Any'")
            doc_filter = data["doc_filter"]
        if "page_title_filter" in data:
            if (type(data["page_title_filter"])) != str:
                raise BadRequestException("page_title_filter  must be string")
            page_title_filter = data["page_title_filter"]

        result = doc_search.get_search_result(
            search_query=data["search_query"],
            limit=limit,
            thresh=thresh,
            doc_filter=doc_filter,
            page_title_filter=page_title_filter,)

        return jsonify({"hits": len(result), "result": result})

    except CustomException as e:
        return jsonify({'error': 'An error occurred', 'message': str(e), 'status_code': e.status_code}), e.status_code
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500


@app.errorhandler(404)
def not_found_error(error):
    return "<h1>Route doesn't exist</h1>", 404


if __name__ == '__main__':

    app.register_blueprint(insert_doc)
    app.run(debug=True)
