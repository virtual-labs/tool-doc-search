from flask_cors import CORS
import uuid
from utils.doc_info import is_valid_doc_type
from utils.doc_instances import doc_search
import json
from dotenv import load_dotenv, find_dotenv
from error.CustomException import CustomException, BadRequestException
from flask import Flask, request, jsonify, abort
import os
import pathlib
import requests
from flask import session, redirect, request, render_template, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from error.CustomException import BadRequestException
from utils.insert_doc_util import insert_document_batch
from utils.doc_instances import doc_search, doc_record


app = Flask(__name__)
app.secret_key = 'db42f1f479b34801ae7fb2636ea57402'

CORS(app, resources={r'/*': {'origins': '*'}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index():
    return "<h1>DocSearch API.</h1>"


@app.route('/post_req', methods=['POST'])
def index1():
    data = request.json
    return jsonify(data)


@app.errorhandler(404)
def not_found_error(error):
    return "<h1>Route doesn't exist</h1>", 404


@app.route('/api/search', methods=['POST'])
def search():
    print("Getting Search request")
    try:
        limit = 10
        thresh = 0.0
        doc_filter = "Any"
        src_filter = "Any"
        acc_filter = "Any"
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
            doc_filter = data["doc_filter"]

        if "src_filter" in data:
            src_filter = data["src_filter"]

        if "acc_filter" in data:
            acc_filter = data["acc_filter"]

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
            src_filter=src_filter,
            acc_filter=acc_filter,
            page_title_filter=page_title_filter,)

        response = jsonify({"hits": len(result), "result": result})

        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods',
                             'DELETE, POST, GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, X-Requested-With')

        return response

    except CustomException as e:
        print(e)
        return jsonify({'error': 'An error occurred', 'message': str(e), 'status_code': e.status_code, "err": True}), e.status_code
    except Exception as e:
        print(e)
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e), "err": True}), 500


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "./secrets/client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "openid"],
    redirect_uri=os.getenv("CALLBACK_URL")
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        print("in wrapper", "google_id" not in session, session)
        if ("google_id" in session):
            print(session["google_id"])
        # if "google_id" not in session:
        #     return redirect('/insert_doc/login')  # Authorization required
        # else:
        #     return function()

        if 'google_id' in session:
            return function()
        authorization_url, state = flow.authorization_url()
        session['state'] = state
        session.modified = True
        return redirect(authorization_url)

    return wrapper


@app.route("/insert_doc")
def insert_doc():
    return "<a href='/insert_doc/login'><button>Login</button></a>"


@app.route("/insert_doc/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    print("state variable", session["state"])
    return redirect(authorization_url)


@app.route("/insert_doc/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    print(("state" in request.args))
    print(("state" in session))
    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/insert_doc/protected_area")


@app.route("/insert_doc/logout")
def logout():
    session.clear()
    print("logged out")
    print(session)
    return redirect("/")


@app.route("/insert_doc/protected_area/", methods=['GET', 'POST'])
@login_is_required
def protected_area():
    try:
        credentials = flow.credentials
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        result = None
        print("Getting ", request.method)
        if request.method == 'POST':
            req = request.json

            # print(json.dumps(req, indent=4, sort_keys=True))
            # return jsonify({"message": "Invalid action"})
            try:
                if "action" not in req:
                    raise BadRequestException("Please provide action")

                if (req["action"] == "insert" or req["action"] == "update"):
                    if "data" not in req:
                        raise BadRequestException("Please provide data")
                    result = insert_document_batch(
                        docs=req["data"], credentials=credentials, name=session["name"], doc_search=doc_search, operation=req["action"])
                    return jsonify(result)

                elif (req["action"] == "delete"):
                    if "data" not in req:
                        raise BadRequestException("Please provide data")
                    print("in delete")
                    print(req["data"])
                    result = doc_search.delete_doc(
                        urls=req["data"],  user=session["name"])
                    print("got it")
                    return jsonify(result)

                elif (req["action"] == "folder-insert" or req["action"] == "folder-update" or req["action"] == "folder-delete"):
                    if "data" not in req:
                        raise BadRequestException("Please provide data")
                    print("in delete")
                    print(req["data"])

                    if len(req["data"]) == 0:
                        raise BadRequestException("Please provide a folder")
                    if len(req["data"]) > 1:
                        raise BadRequestException(
                            "Please provide only one folder")

                    if req["action"] == "folder-delete":
                        print("Started deleting folder")
                        result = doc_record.delete_folder(
                            folderUrl=req["data"][0],  user=session["name"])
                    else:
                        op = "insert" if req["action"] == "folder-insert" else "update"
                        result = doc_search.insert_drive_folder(
                            folder=req["data"][0], credentials=credentials,  user=session["name"], operation=op)

                    print("got it")
                    return jsonify(result)

                else:
                    return jsonify({"message": "Invalid action", "error": True})
            except BadRequestException as e:
                return jsonify({"message": f"<h1>Error occurred</h1> {str(e)}.", "error": True}), 500

        return render_template('update_document_page.html', result=result, user_name=session["name"])

    except Exception as e:
        if (str(e) == "There is no access token for this session, did you call fetch_token?"):
            session.clear()
            return redirect("/insert_doc/login")
        return jsonify({"message": f"{str(e)}.", "err": True}), 500


@app.route("/insert_doc/get_docs", methods=['GET'])
def get_docs():
    try:
        args = request.args
        search_query = args.get('search_query')
        page = args.get('page') if args.get('page') else 1
        print(search_query, page)
        return jsonify(doc_record.get_docs(search_query, page))
    except Exception as e:
        return jsonify({"message": f"<h1>Error occurred</h1> {str(e)}.", "err": True}), 500


if __name__ == '__main__':
    # app.register_blueprint(insert_doc)

    print("Starting server")
    app.run(debug=True)
