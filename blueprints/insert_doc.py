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

GOOGLE_CLIENT_ID = "235297947063-u5kjaptgnu61j4kl5i4980l5h91e44au.apps.googleusercontent.com"
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
        if "google_id" not in session:
            return redirect('/insert_doc/login')  # Authorization required
        else:
            return function()
    return wrapper


@insert_doc.route("/")
def index():
    return "Hello World <a href='/insert_doc/login'><button>Login</button></a>"


@insert_doc.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@insert_doc.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

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


@insert_doc.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# def get_doc(credentials):
#     service = build('drive', 'v3', credentials=credentials)
#     doc_id = '1MQATKjor7Z_qpgChRwJw4BcRk22scFpCyMqN5FeqNn8'
#     request = service.files().export(fileId=doc_id, mimeType='text/html')
#     response = request.execute()
#     # print("html content", response.decode('utf-8'))


def insert_document(link, document_type, credentials):
    try:
        if document_type != "md" and document_type != "gdoc":
            raise BadRequestException(
                "Please provide document type (md, gdoc)")
        chunks = doc_search.insert_doc(type=document_type,
                                       url=link, credentials=credentials)
        print(chunks)
        return ({"message": "Document inserted successfully", "chunks_count": len(chunks),
                 "page_title": chunks[0]["payload"]["page_title"] if len(chunks) else "No title"})
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
        print("POST", request.method)
        if request.method == 'POST':
            # get_doc(credentials=credentials)
            link = request.form.get('link')
            document_type = request.form.get('document_type')
            result = insert_document(
                link=link, document_type=document_type, credentials=credentials)
            # print(result)
        return render_template('insert_document_page.html', result=result)
    except Exception as e:
        return f"<h1>Error occurred</h1> {str(e)}. Try to login again"
