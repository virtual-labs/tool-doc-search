from flask import Flask
from blueprints.insert_doc import insert_doc
from blueprints.search_doc import search_doc
import uuid
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex

CORS(app, resources={r'/*': {'origins': '*'}})
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index():
    return "<h1>DocSearch API</h1>"


@app.errorhandler(404)
def not_found_error(error):
    return "<h1>Route doesn't exist</h1>", 404


if __name__ == '__main__':
    app.register_blueprint(insert_doc)
    app.register_blueprint(search_doc)
    app.run(debug=True)
