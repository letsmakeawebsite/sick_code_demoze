from google.appengine.ext import vendor
vendor.add('venv/lib/python2.7/site-packages')

import flask
import mimetypes
import werkzeug.security

from flask import Flask

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def deliver(path):
    host = flask.request.headers['Host'].split(":")[0]
    mainHost = ".".join(host.split('.')[-2:])
    if path == "":
        path = "index.html"
    mime = mimetypes.guess_type(path)[0]
    fullPath = werkzeug.security.safe_join(('sites/%s' % mainHost), path)
    with open(fullPath) as f:
        return flask.Response(
            f.read(),
            mimetype=mime
        )
