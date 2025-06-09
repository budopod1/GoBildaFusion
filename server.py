from flask import Flask, request
import requests

with open("inject.js") as file:
    INJECT_JS = file.read()

with open("submitted.html") as file:
    SUBMITTED_HTML = file.read()

target = "https://gobilda.com/"

app = Flask(__name__)

def proxy_request():
    return requests.get(target+request.full_path).text

def inject_js(txt):
    return txt.replace("</head>", f"<script>{INJECT_JS}</script></head>")

@app.route("/submitted")
def serve_submitted():
    return SUBMITTED_HTML

@app.route("/<path:path>")
def serve_path(path):
    return proxy_request()

@app.route("/")
def serve_index():
    return inject_js(proxy_request())

app.run("localhost", 7776)
