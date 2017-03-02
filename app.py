from google.appengine.ext import vendor
vendor.add('venv/lib/python2.7/site-packages')

import json
import flask
import yaml
import mimetypes
import werkzeug.security
from werkzeug.http import parse_options_header

from flask import Flask

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

app = Flask(__name__)

class Website(ndb.Model):

    data = ndb.TextProperty()
    domain = ndb.StringProperty()
    template = ndb.StringProperty()

@app.route('/admin/')
def admin():
    websites = Website.query().fetch()
    return flask.render_template(
        'admin/root.jinja2',
        websites=websites,
    )

@app.route('/admin/<key>/')
def website(key):
    if key == 'new':
        website = Website()
    else:
        website = ndb.Key(urlsafe=key).get()
    return flask.render_template(
        'admin/website.jinja2',
        website=website,
        DEFAULT_SRCS=json.dumps(DEFAULT_SRCS),
    )

@app.route('/admin/<key>/', methods=['POST'])
def websiteSave(key):
    if key == 'new':
        website = Website()
    else:
        website = ndb.Key(urlsafe=key).get()

    website.domain = flask.request.values['domain']
    website.template = flask.request.values['template']
    website.data = flask.request.values['data']
    website.put()
    return flask.redirect('/admin/%s/' % website.key.urlsafe())

@app.route('/admin/upload/')
def upload():
    url = blobstore.create_upload_url('/admin/upload/')
    return flask.render_template(
        'admin/upload.jinja2',
        url=url,
    )

@app.route('/admin/upload/', methods=["POST"])
def doUpload():
    f = flask.request.files['file']
    header = f.headers['Content-Type']
    parsed_header = parse_options_header(header)
    blob_key = parsed_header[1]['blob-key']
    imageUrl = "/img/%s" % blob_key
    url = blobstore.create_upload_url('/admin/upload/')
    return flask.render_template(
        'admin/upload.jinja2',
        url=url,
        uploaded=imageUrl,
    )

@app.route("/img/<bkey>")
def img(bkey):
    blob_info = blobstore.get(bkey)
    response = flask.make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response

@app.route('/force-domain/<domain>/', defaults={'path': ''})
@app.route('/force-domain/<domain>/<path:path>')
def forceDomain(domain, path):
    return render(domain, path)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def deliver(path):
    host = flask.request.headers['Host'].split(":")[0]
    mainHost = ".".join(host.split('.')[-2:])
    return render(mainHost, path)

def render(domain, path):
    website = Website.query()\
        .filter(Website.domain == domain)\
        .get()
    if website:
        return renderWebsite(website)

    if path == "":
        path = "index.html"
    mime = mimetypes.guess_type(path)[0]
    fullPath = werkzeug.security.safe_join(('sites/%s' % domain), path)
    with open(fullPath) as f:
        return flask.Response(
            f.read(),
            mimetype=mime
        )

def renderWebsite(website):
    data = yaml.safe_load(website.data)
    data['domain'] = website.domain
    return flask.render_template(
        'bootstrap-marketing/index.html',
        **data
    )

BOOTSTRAP_MARKETING_SRC = """
title:

topImage:
headline:
tagline:
marquee:

quoteImage:
quote:
quoteAuthor:

statsEnabled: false
statsImage:
statsIntro:
stat1:
stat1Unit:
stat2:
stat2Unit:
stat3:
stat3Unit:
stat4: 5
stat4Unit: ANNUAL BOTCHED FORESKIN OPERTIONS

featureListEnabled: false
featureListIntro:
feature1Icon:
feature1Title:
feature1Text:
feature2Icon:
feature2Title:
feature2Text:
feature3Icon:
feature3Title:
feature3Text:
feature4Icon:
feature4Title:
feature4Text:
""".strip()

DEFAULT_SRCS = {
    'bootstrap-marketing': BOOTSTRAP_MARKETING_SRC,
}
