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
audioFile: "/resource/audio/LMAW.mp3"
title: "Somebody's Charity"
shortTitle: "Help Somethings In Need"
headerImage: "/resource/generic-charity-7/img/mark.jpg"
headline: "Somebody's Foundation for the Something"
tagline: '"Helping people because of a thing for a period of time"'
buttonText: "You should prolly like donate"
marquee: The <marquee> element is obsolete and must not be used. While some browsers still support it, it's not required. In addition, using this element is basically one of the worst things you can do to your users, so please, please don't do it.

theater: "UCB Theater in New York"
theater_twitter: "ucbtny"

enableSection2: true
section2Image: "/resource/generic-charity-7/img/mark.jpg"
section2Title: "Regularly scheduled programming"
section2Heading: "Official Party Bulletin"
section2Description: "Where there's a will, there's a way to distribute a person's assets after their death"
section2Feature1Heading: "What you want"
section2Feature1Description: "Baby I've got it"
section2Feature2Heading: "What you need"
section2Feature2Description: "Is just a little e-check"

enableDevSection: true
devSectionTitle: "You know I'm comin for that cash"
devSectionHeading: "Gimme gimme gimme"
devSectionBody: "Without money we would be unable to collect more money"
devSectionButton: "Money money money money...  MONEEEY!"
devSectionCode: |
    class Charity extends Component {
        getMoneys() {
            return this.state.moneys
        }
        render() {
            return (
                <div>
                    Donations: {this.getMoneys()}
                </div>
            )
        }
    }

enableQuote: true
quoteImage: "/resource/generic-charity-7/img/mark.jpg"
quoteTitle: "Get a load of what this person said:"
quoteBody: "And Alexander wept, for there were no more worlds to conquer"
quoteAttribution: "Hans Gruber, Die Hard"

enableFeatures: true
featureTitle: ""
featureBody: ""
feature1Icon: cut
feature1Header: "We don't wanna cut you, man"
feature1Body: "But best believe we will"
feature2Icon: hand-o-left
feature2Header: "Don't be alt-left"
feature2Body: "Do the right thing and give"
feature3Icon: cc-visa
feature3Header: "We accept all major credit cards"
feature3Body: "And a few from the minors as well"
enableFeaturesLine2: true
feature4Icon: tree
feature4Header: "How about tree fiddy?"
feature4Body: "It was about that time I realized..."
feature5Icon: ticket
feature5Header: "Free raffle entry with donation!"
feature5Body: "Win a wacky waving arm flailing inflatable tube man"
feature6Icon: spinner
feature6Header: "Loading..."
feature6Body: "We appreciate your patience"

enablePlans: true
plansTitle: Please to send funds?
plansBody: "No limits, like Master P"
plan1: Street Rat
plan1Body: "You're clearly not taking this seriously"
plan2: Schmuck
plan2Body: "Exactly what someone who looks like *you* would donate"
plan3: Sucker
plan3Body: "Hey big spender!"

enableQuote2: true
quoteImage2: "/resource/generic-charity-7/img/mark.jpg"
quoteTitle2: "Something else someone said:"
quoteBody2: "281-330-8004"
quoteAttribution2: "Ricky Rose"

enablesectionQ: true
sectionQImage: "/resource/generic-charity-7/img/mark.jpg"
sectionQTitle: "This is the *final* final show!"
sectionQHeading: "Glad you could make it out"
sectionQDescription: "One day (soon) you'll tell your children and your children's children that you were HERE, TONIGHT!"
sectionQFeature1Heading: "Sick"
sectionQFeature1Description: "Woop woop!"
sectionQFeature2Heading: "Blerg"
sectionQFeature2Description: "We'll see who has the last laugh...  Hopefully you!"

""".strip()

MULTISITE_SRC = """
title: Title
pages:
- path: /
  title: Page 1
  heading: This is Page 1
  image: http://putinspussies.club/img/AMIfv94MQuFWVxZAFV3XZUuMFVJ-lWmzJWUiyK-fM9i0FvK8vpDP__fZQbcXuudh-ccocxhNtsavJSoQZQi4IfQxxrN0DtRcQ5iQ22Xkg-6qO0v6S8A14vBIbRoSiRxVm1SdZtJ3dsbdLVftoIPIx_G26tJC-tIoXb-s9vGa_bUmktFkUnJetCgcsNtALiALp_0ByQmwcQhBxVBx-auYMUDQ19QypEiUUa8thxu0lJg9nnn7XeL59Ne03pD4TSCFrOiX_x4MGdad2ikVfe7FisGwrMPmXUuoKMYO9-u-_XxBwvmJFIb5BV0LYKnui2zkDkG-oWf3AZKG41jZeUzsLGYdmMyeIWswrgiIKlcoRCxdv7fLaIXoEHK8EQQXkhRTYbj8Dw9UaJJy
  body:
  - This is the body for page 1.
  - This is another paragraph.
- path: /page2
  title: Page 2
  heading: This is Page 2
  image: http://putinspussies.club/img/AMIfv94MQuFWVxZAFV3XZUuMFVJ-lWmzJWUiyK-fM9i0FvK8vpDP__fZQbcXuudh-ccocxhNtsavJSoQZQi4IfQxxrN0DtRcQ5iQ22Xkg-6qO0v6S8A14vBIbRoSiRxVm1SdZtJ3dsbdLVftoIPIx_G26tJC-tIoXb-s9vGa_bUmktFkUnJetCgcsNtALiALp_0ByQmwcQhBxVBx-auYMUDQ19QypEiUUa8thxu0lJg9nnn7XeL59Ne03pD4TSCFrOiX_x4MGdad2ikVfe7FisGwrMPmXUuoKMYO9-u-_XxBwvmJFIb5BV0LYKnui2zkDkG-oWf3AZKG41jZeUzsLGYdmMyeIWswrgiIKlcoRCxdv7fLaIXoEHK8EQQXkhRTYbj8Dw9UaJJy
  body:
  - This is the body for page 2.
  - This is another paragraph.
""".strip()

DEFAULT_SRCS = {
    'bootstrap-marketing': BOOTSTRAP_MARKETING_SRC,
    'bootstrap-marketing-dark': BOOTSTRAP_MARKETING_SRC,
    'bootstrap-marketing-light': BOOTSTRAP_MARKETING_SRC,
    'bootstrap-startup': BOOSTRAP_STARTUP_SRC,
    'bootstrap-charity': BOOSTRAP_CHARITY_SRC,
    'philadelphia': BOOSTRAP_CHARITY_SRC,
    'bootstrap-charity-dark': BOOSTRAP_CHARITY_SRC,
    'generic-charity': BOOSTRAP_CHARITY_SRC,
    'generic-charity-me': BOOSTRAP_CHARITY_SRC,
    'generic-charity-xp': BOOSTRAP_CHARITY_SRC,
    'generic-charity-vista': BOOSTRAP_CHARITY_SRC,
    'generic-charity-7': BOOSTRAP_CHARITY_SRC,
    'the-matrix-reloaded': BOOSTRAP_CHARITY_SRC,
    'the-matrix-revolutions': BOOSTRAP_CHARITY_SRC,
    'multi-page': MULTISITE_SRC,
}
