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
        '%s/index.html' % website.template,
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

BOOSTRAP_STARTUP_SRC = """
title: "Somebody Sells Something"
shortTitle: "Somebody's Somethings"
headerImage: ""
headline: ""
tagline: ""
buttonText: ""

enableSection2: false
section2Image: ""
section2Title: "Social Local Mobile"
section2Heading: ""
section2Description: ""
section2Feature1Heading: "Quick Views"
section2Feature1Description: ""
section2Feature2Heading: "Detailed Drilldowns"
section2Feature2Description: ""

enableDevSection: false
devSectionTitle: "Optimized For Developers"
devSectionHeading: "Developers run the world."
devSectionBody: ""
devSectionButton: "Read Our Docs"
devSectionCode: |
  LABEL START
  PUT "U" >> STDOUT
  PUT "R" >> STDOUT
  PUT " " >> STDOUT
  PUT "D" >> STDOUT
  PUT "U" >> STDOUT
  PUT "M" >> STDOUT
  PUT "B" >> STDOUT
  GO TO START

enableQuote: false
quoteImage:
quoteTitle: "Don't take our word for it"
quoteBody: ""
quoteAttribution: "Name, Job"

enableFeatures: false
featureTitle: ""
featureBody: ""
feature1Header: "Mobile Optimized"
feature1Body: ""
feature2Header: "Save Money"
feature2Body: ""
feature3Header: "Save Time"
feature3Body: ""
enableFeaturesLine2: true
feature4Header: "Complex Calculations"
feature4Body: ""
feature5Header: "24/7 Support"
feature5Body: ""
feature6Header: "Kid Tested, Mother Approved"
feature6Body: ""

enablePlans: false
plansTitle: Flexible Plans
planUnits: "Monthly Allowance"
plansBody: "We don't believe that one size fits all, so we have 3 plans to fit your needs best!"
plan1: Personal
plan1Body: "You're just a person. Your vote doesn't count. We don't care about you."
plan2: Business
plan2Body: "Business runs the world, but not all business is big business!"
plan3: Corporate
plan3Body: "Corporations run the world, and you're a big-wig. This one's for you!"
""".strip()

BOOSTRAP_CHARITY_SRC = """
title: "Somebody's Charity"
shortTitle: "Help Somethings In Need"
headerImage: "/img/SiUcfaZre4lkveoNuaHWzg=="
headline: "Somebody's Foundation for the Something"
tagline: '"Helping people because of a thing for a period of time"'
buttonText: "You should prolly like donate"
marquee: The <marquee> element is obsolete and must not be used. While some browsers still support it, it's not required. In addition, using this element is basically one of the worst things you can do to your users, so please, please don't do it.

enableSection2: true
section2Image: "/img/CTGlcNPKpwOGR_NWSvidOA=="
section2Title: "Annual prospectus agenda letter"
section2Heading: "Telling people about the cause, just 'cause"
section2Description: '"It''s the right thing to do!" - Krang, Chief Charity Coordinator'
section2Feature1Heading: "Don't be Evil"
section2Feature1Description: "Right in the feels"
section2Feature2Heading: "The Human Fund"
section2Feature2Description: "Money for people"

enableDevSection: true
devSectionTitle: "Are you donating yet?"
devSectionHeading: "Give us money"
devSectionBody: "With your money, we'll have the resources to buy things, which are invaluable in our fight to help the people the thing that happened happened to."
devSectionButton: "Gimme the loot"
devSectionCode: |
  159,265+ Lira raised
  3.1 million things saved
  200+ bad things happen each year
  4/5 dentists agree
  1 person can make a difference...

enableQuote: true
quoteImage: "/img/42NHLi2fPHB3mNqNR2Uylw=="
quoteTitle: "Don't take our word for it"
quoteBody: "Veni, vidi, vici"
quoteAttribution: "Julius Caesar, Sr. Social Strategist"

enableFeatures: true
featureTitle: ""
featureBody: ""
feature1Icon: heartbeat
feature1Header: "Literally saving lives"
feature1Body: "One life at a time"
feature2Icon: money
feature2Header: 'It''s a tax write off'
feature2Body: "Mama's gotta wet her beak"
feature3Icon: facebook-square
feature3Header: "Something to brag about"
feature3Body: "Make your friends bitter that you're clearly better than them"
enableFeaturesLine2: true
feature4Icon: life-saver
feature4Header: "World class maritime support"
feature4Body: "Nobody handles boat charity like us"
feature5Icon: paper-plane-o
feature5Header: "Primitive aeronautics"
feature5Body: "Wait what do paper planes have to do with any of this?"
feature6Icon: mortar-board
feature6Header: "Don't be an idiot"
feature6Body: "Gosh, just give already, geez"

enablePlans: true
plansTitle: Choose your own ad-gift-ure
planUnits: "It's hella flexible"
plansBody: "Pick a sponsorship that works right for you"
plan1: Louse
plan1Body: "Is that the best that you can do?"
plan2: Cheapskate
plan2Body: "Everybody knows you could afford more."
plan3: Decent Person
plan3Body: "Now we're cooking with gas!"
""".strip()

DEFAULT_SRCS = {
    'bootstrap-marketing': BOOTSTRAP_MARKETING_SRC,
    'bootstrap-marketing-dark': BOOTSTRAP_MARKETING_SRC,
    'bootstrap-marketing-light': BOOTSTRAP_MARKETING_SRC,
    'bootstrap-startup': BOOSTRAP_STARTUP_SRC,
    'bootstrap-charity': BOOSTRAP_CHARITY_SRC,
}
