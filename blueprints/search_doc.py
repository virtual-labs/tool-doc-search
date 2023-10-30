from flask import Blueprint
from flask import Flask, request, jsonify
from error.CustomException import CustomException, BadRequestException
from utils.doc_search import DocumentSearch
from dotenv import load_dotenv
import os
from flask_cors import CORS, cross_origin
import json
from utils.doc_instances import doc_search
load_dotenv()

search_doc = Blueprint('search_doc', __name__, url_prefix='/api/search')


@search_doc.route('', methods=['POST'])
def index():
    print("Getting Search request")
    try:
        limit = 10
        thresh = 0.0
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
            if data["doc_filter"] != "md" and data["doc_filter"] != "xlsx" and data["doc_filter"] != "gdoc" and data["doc_filter"] != "Any":
                raise BadRequestException(
                    "doc_filter must be 'md' or 'gdoc' or 'Any'")
            doc_filter = data["doc_filter"]
        if "page_title_filter" in data:
            if (type(data["page_title_filter"])) != str:
                raise BadRequestException("page_title_filter  must be string")
            page_title_filter = data["page_title_filter"]
        print(json.dumps(data, indent=4))
        result = doc_search.get_search_result(
            search_query=data["search_query"],
            limit=limit,
            thresh=thresh,
            doc_filter=doc_filter,
            page_title_filter=page_title_filter,)
        # print(json.dumps(result, indent=4))
        response = jsonify({"hits": len(result), "result": result})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods',
                             'DELETE, POST, GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, X-Requested-With')

        # "Access-Control-Allow-Methods", "DELETE, POST, GET, OPTIONS"
        return response

    except CustomException as e:
        print(e)
        return jsonify({'error': 'An error occurred', 'message': str(e), 'status_code': e.status_code}), e.status_code
    except Exception as e:
        print(e)
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500
