import time
import json

from importlib import import_module
from datetime import datetime, timedelta

from pulsar import PermissionDenied, Http404
from pulsar.utils.pep import to_bytes, to_string
from pulsar.utils.importer import module_attribute

import lux
from lux import Router
from lux.forms import Form
from lux.utils.crypt import get_random_string, digest

from .jwtmixin import jwt
from .views import ForgotPassword
from .backend import REASON_BAD_TOKEN


__all__ = ['SessionMixin']


class SessionMixin(object):
    '''Mixin for :class:`.AuthBackend` via sessions.
    '''
    ForgotPasswordRouter = None
    dismiss_message = None

    def __init__(self, app):
        wsgi = self.init_wsgi(app)
        cfg = self.config
        self.encoding = cfg['ENCODING']
        self.secret_key = cfg['SECRET_KEY'].encode()
        self.session_cookie_name = cfg['SESSION_COOKIE_NAME']
        self.session_expiry = cfg['SESSION_EXPIRY']
        self.salt_size = cfg['AUTH_SALT_SIZE']
        self.check_username = cfg['CHECK_USERNAME']
        self.csrf_expiry = cfg['CSRF_EXPIRY']
        algorithm = cfg['CRYPT_ALGORITHM']
        self.crypt_module = import_module(algorithm)
        self.jwt = jwt
        if cfg['SESSION_MESSAGES']:
            wsgi.middleware.append(Router('_dismiss_message',
                                          post=self._dismiss_message))
            reset = cfg['RESET_PASSWORD_URL']
            if reset:
                router = self.ForgotPasswordRouter or ForgotPassword
                wsgi.middleware.append(router(reset))

    def request(self, request):
        key = self.config['SESSION_COOKIE_NAME']
        session_key = request.cookies.get(key)
        session = None
        if session_key:
            session = self.get_session(session_key.value)
        if not session:
            session = self.create_session(request)
        request.cache.session = session
        if session.user:
            request.cache.user = session.user.get()
        if not request.cache.user:
            request.cache.user = self.anonymous()

    def response(self, request, response):
        session = request.cache.session
        if session:
            if response.can_set_cookies():
                key = request.app.config['SESSION_COOKIE_NAME']
                session_key = request.cookies.get(key)
                id = str(session.key.id())
                if not session_key or session_key.value != id:
                    response.set_cookie(key, value=str(id), httponly=True,
                                        expires=session.expiry)

            session.put()
        return response

    def csrf_token(self, request):
        session = request.cache.session
        if session:
            assert self.jwt, 'Requires jwt package'
            return self.jwt.encode({'session': self.session_key(session),
                                    'exp': time.time() + self.csrf_expiry},
                                   self.secret_key)

    def validate_csrf_token(self, request, token):
        if not token:
            raise PermissionDenied(REASON_BAD_TOKEN)
        try:
            assert self.jwt, 'Requires jwt package'
            token = self.jwt.decode(token, self.secret_key)
        except jwt.ExpiredSignature:
            raise PermissionDenied('Expired token')
        except Exception:
            raise PermissionDenied(REASON_BAD_TOKEN)
        else:
            if token['session'] != self.session_key(request.cache.session):
                raise PermissionDenied(REASON_BAD_TOKEN)

    def create_session_id(self):
        while True:
            session_key = get_random_string(32)
            if not self.get_session(session_key):
                break
        return session_key

    def get_session(self, key):
        '''Retrieve a session from its key
        '''
        raise NotImplementedError

    def session_key(self, session):
        '''Session key from session object
        '''
        raise NotImplementedError

    def create_registration(self, request, user, expiry):
        '''Create a registration entry for a user.
        This method should return the registration/activation key.'''
        raise NotImplementedError

    def confirm_registration(self, request, **params):
        '''Confirm registration'''
        raise NotImplementedError

    def create_session(self, request, user=None, expiry=None):
        '''Create a new session
        '''
        raise NotImplementedError

    def auth_key_used(self, key):
        '''The authentication ``key`` has been used and this method is
        for setting/updating the backend model accordingly.
        Used during password retrieval and user registration
        '''
        raise NotImplementedError

    def password_recovery(self, request, email):
        raise NotImplementedError

    def login(self, request, user=None):
        '''Login a user from a model or from post data
        '''
        if user is None:
            data = request.body_data()
            user = self.authenticate(request, **data)
            if user is None:
                raise AuthenticationError('Invalid username or password')
        if not user.is_active():
            return self.inactive_user_login(request, user)
        request.cache.session = self.create_session(request, user)
        request.cache.user = user
        return user

    def inactive_user_login(self, request, user):
        '''Handle a user not yet active'''
        cfg = request.config
        url = '/signup/confirmation/%s' % user.username
        session = request.cache.session
        context = {'email': user.email,
                   'email_from': cfg['DEFAULT_FROM_EMAIL'],
                   'confirmation_url': url}
        message = request.app.render_template('inactive.txt', context)
        session.warning(message)

    def logout(self, request, user=None):
        '''Logout a ``user``
        '''
        session = request.cache.session
        user = user or request.cache.user
        if user and user.is_authenticated():
            request.cache.session = self.create_session(request)
            request.cache.user = self.anonymous()

    def get_or_create_registration(self, request, user, **kw):
        '''Create a registration profile for ``user``.

        This method send an email to the user so that the email
        is verified once the user follows the link in the email.

        Usually called after user registration.
        '''
        if user and user.email:
            days = request.config['ACCOUNT_ACTIVATION_DAYS']
            expiry = datetime.now() + timedelta(days=days)
            auth_key = self.create_registration(request, user, expiry)
            self.send_email_confirmation(request, user, auth_key, **kw)
            return auth_key

    def send_email_confirmation(self, request, user, auth_key,
                                email_subject=None, email_message=None,
                                message=None):
        '''Send an email to user to confirm his/her email address'''
        app = request.app
        cfg = app.config
        ctx = {'auth_key': auth_key,
               'expiration_days': cfg['ACCOUNT_ACTIVATION_DAYS'],
               'email': user.email,
               'site_uri': request.absolute_uri('/')[:-1]}

        subject = app.render_template(
            email_subject or 'activation_email_subject.txt', ctx)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = app.render_template(
            email_message or 'activation_email.txt', ctx)
        user.email_user(subject, body, cfg['DEFAULT_FROM_EMAIL'])
        message = app.render_template(
            message or 'activation_message.txt', ctx)
        request.cache.session.info(message)

    def decript(self, password=None):
        if password:
            p = self.crypt_module.decrypt(to_bytes(password, self.encoding),
                                          self.secret_key)
            return to_string(p, self.encoding)
        else:
            return UNUSABLE_PASSWORD

    # INTERNALS
    def _dismiss_message(self, request):
        response = request.response
        if response.content_type in lux.JSON_CONTENT_TYPES:
            session = request.cache.session
            form = Form(request, data=request.body_data())
            data = form.rawdata['message']
            body = {'success': session.remove_message(data)}
            response.content = json.dumps(body)
            return response

    def _encript(self, password):
        p = self.crypt_module.encrypt(to_bytes(password, self.encoding),
                                      self.secret_key, self.salt_size)
        return to_string(p, self.encoding)
