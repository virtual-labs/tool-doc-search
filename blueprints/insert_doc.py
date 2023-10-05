import os
import pathlib
import requests
from flask import Flask, session, abort, redirect, request, Blueprint, render_template, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from googleapiclient.discovery import build
from dotenv import load_dotenv
from error.CustomException import CustomException, BadRequestException


from utils.doc_search import DocumentSearch

insert_doc = Blueprint('insert_doc', __name__, url_prefix='/insert_doc')
load_dotenv()
doc_search = DocumentSearch(url=os.getenv("QDRANT_URL"),
                            api_key=os.getenv("QDRANT_API"),
                            collection_name=os.getenv("QDRANT_COLLECTION"))

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"],
    redirect_uri="http://127.0.0.1:5000/insert_doc/callback"
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


def insert_document(link, document_type, credentials):
    try:
        if document_type != "md" and document_type != "gdoc":
            raise BadRequestException(
                "Please provide document type (md, gdoc)")
        chunks = doc_search.insert_doc(type=document_type,
                                       url=link, credentials=credentials, user=session["name"])
        return ({"message": "Document inserted successfully", "chunks_count": len(chunks),
                 "page_title": chunks[0]["payload"]["page_title"] if len(chunks) else "No title",
                 "accessibility": chunks[0]["payload"]["accessibility"]})
    except CustomException as e:
        return ({'error': 'An error occurred', 'message': str(e), 'status_code': e.status_code})
    except Exception as e:
        return ({'error': 'An unexpected error occurred', 'message': str(e), 'status_code': 500})
    
def insert_document_batch(docs, credentials):
    try:
        result = doc_search.insert_doc_batch(docs=docs, credentials=credentials, user=session["name"])
        return result
    except CustomException as e:
        return ({'error': 'An error occurred', 'message': str(e), 'status_code': e.status_code})
    except Exception as e:
        return ({'error': 'An unexpected error occurred', 'message': str(e), 'status_code': 500})


@insert_doc.route("/protected_area", methods=['GET', 'POST'])
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
            selected_value = int(request.form['division_count'])
            docs = []
            for i in range(selected_value):
                url = request.form.get(f'url_{i}', '')
                tag = request.form.get(f'hidden_{i}', '')
                docs.append({"url":url, "type":tag})
            print(docs)
            result = insert_document_batch(docs=docs, credentials=credentials)
        return render_template('insert_document_page.html', result=result, user_name=session["name"])
    except Exception as e:
        return f"<h1>Error occurred</h1> {str(e)}. Try to login again"


@insert_doc.route("/test", methods=['GET', 'POST'])
def protected_area():
    try:
        return render_template('insert_document_page.html', result=None, user_name="unknown")
    except Exception as e:
        return f"<h1>Error occurred</h1> {str(e)}. Try to login again"
