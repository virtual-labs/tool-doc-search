import os
import pathlib
import requests
from flask import session, redirect, request, Blueprint, render_template, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from error.CustomException import BadRequestException
from utils.insert_doc_util import insert_document_batch
from utils.doc_instances import doc_search, doc_record
import json


insert_doc = Blueprint('insert_doc', __name__, url_prefix='/insert_doc')


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "../secrets/client_secret.json")

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
        if "google_id" not in session:
            return redirect('/insert_doc/login')  # Authorization required
        else:
            return function()
    return wrapper


@insert_doc.route("/")
def index():
    return "<a href='/insert_doc/login'><button>Login</button></a>"


@insert_doc.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    print("state variable", session["state"])
    return redirect(authorization_url)


@insert_doc.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    print(("state" in request.args))
    print(("state" in session))
    # if not session["state"] == request.args["state"]:
    #     abort(500)  # State does not match!

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


@insert_doc.route("/logout")
def logout():
    session.clear()
    print("logged out")
    print(session)
    return redirect("/")


@insert_doc.route("/protected_area/", methods=['GET', 'POST'])
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
                            folderUrl=req["data"][0], credentials=credentials,  user=session["name"], operation=op)

                    print("got it")
                    return jsonify(result)

                else:
                    return jsonify({"message": "Invalid action"})
            except BadRequestException as e:
                return jsonify({"message": f"<h1>Error occurred</h1> {str(e)}."}), 500

        return render_template('update_document_page.html', result=result, user_name=session["name"])

    except Exception as e:
        return jsonify({"message": f"{str(e)}."}), 500


@insert_doc.route("/get_docs", methods=['GET'])
def get_docs():
    try:
        args = request.args
        search_query = args.get('search_query')
        page = args.get('page') if args.get('page') else 1
        print(search_query, page)
        return jsonify(doc_record.get_docs(search_query, page))
    except Exception as e:
        return jsonify({"message": f"<h1>Error occurred</h1> {str(e)}."}), 500


@insert_doc.route("/test", methods=['GET', 'POST'])
def test():
    try:
        return render_template('update_document_page.html', result=None, user_name="unknown")
    except Exception as e:
        return f"<h1>Error occurred</h1> {str(e)}. Try to login again"
