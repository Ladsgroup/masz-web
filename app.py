import os
from functools import wraps

import flask
import mwoauth
import yaml
from flask_session import Session

from masz_web.checkuser import auth_user_in_wiki, allowed_wikis, get_wiki_db_name
from masz.find_socks_web import get_result, compare

app = flask.Flask(__name__)
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))
Session(app)


@app.route("/")
def index():
    return flask.render_template('home.html',
                                 username=flask.session.get('username'))


def authenticated(f):
    @wraps(f)
    def wrapped_f(*args, **kwargs):
        if 'username' in flask.session:
            return f(*args, **kwargs)
        else:
            return 'fuck no'

    return wrapped_f


@app.route('/auth/login')
def login():
    """Initiate an OAuth login.

    Call the MediaWiki server to get request secrets and then redirect the
    user to the MediaWiki server to sign the request.
    """
    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
    try:
        redirect, request_token = mwoauth.initiate(
            app.config['OAUTH_MWURI'], consumer_token)
    except Exception:
        app.logger.exception('mwoauth.initiate failed')
        return flask.redirect(flask.url_for('index'))
    else:
        flask.session['request_token'] = dict(zip(
            request_token._fields, request_token))
        return flask.redirect(redirect)


@app.route('/auth/oauth-callback')
def oauth_callback():
    """OAuth handshake callback."""
    if 'request_token' not in flask.session:
        flask.flash(u'OAuth callback failed. Are cookies disabled?')
        return flask.redirect(flask.url_for('index'))

    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

    try:
        access_token = mwoauth.complete(
            app.config['OAUTH_MWURI'],
            consumer_token,
            mwoauth.RequestToken(**flask.session['request_token']),
            flask.request.query_string)

        identity = mwoauth.identify(
            app.config['OAUTH_MWURI'], consumer_token, access_token)
    except Exception:
        app.logger.exception('OAuth authentication failed')

    else:
        flask.session['access_token'] = dict(zip(
            access_token._fields, access_token))
        flask.session['username'] = identity['username']
    return flask.redirect(flask.url_for('index'))


@app.route('/auth/logout')
def logout():
    """Log the user out by clearing their session."""
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))


@app.route("/checkuser", methods=['GET'])
@authenticated
def checkuser():
    return flask.render_template('checkuser.html', allowed_wikis=allowed_wikis)


@app.route("/checkuser", methods=['POST'])
@authenticated
def checkuser_post():
    wiki = flask.request.form['wiki'].strip()
    user = flask.request.form['username'].strip()
    if not wiki or not user:
        return flask.redirect(flask.url_for('index'))
    if not auth_user_in_wiki(flask.session['username'], wiki):
        return flask.redirect(flask.url_for('index'))
    result = None
    error = None
    wiki_db = get_wiki_db_name(wiki)
    try:
        result = get_result(compare(user, wiki_db))
    except KeyError:
        error = 'User does not have a fingerprint yet. Maybe a typo?'
    except BaseException:
        error = 'Error'
    return flask.render_template(
        'checkuser_done.html',
        wiki=wiki,
        user=user,
        result=result,
        error=error)

def main():
    app.run(host='0.0.0.0', port=5000)
if __name__ == "__main__":
    main()
