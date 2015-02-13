from io import BytesIO, StringIO

import lux

from pulsar import get_actor
from pulsar.apps.test import unittest, mock, HttpTestClient, TestSuite
from pulsar.apps.test.plugins import bench, profile
from pulsar.utils.pep import ispy3k
from pulsar.utils.httpurl import encode_multipart_formdata


def get_params(*names):
    cfg = get_actor().cfg
    values = []
    for name in names:
        value = cfg.get(name)
        if value:
            values.append(value)
        else:
            return None
    return values


skipUnless = unittest.skipUnless


class TestCase(unittest.TestCase):
    '''TestCase class for lux tests.

    It provides several utilities methods.
    '''
    config_file = 'tests.config'
    '''THe config file to use when building an :meth:`application`'''
    config_params = {}
    '''Dictionary of parameters to override the parameters from
    :attr:`config_file`'''
    apps = None

    def application(self, config_file=None, argv=None, **params):
        '''Return an application for testing. Override if needed.
        '''
        kwargs = self.config_params.copy()
        kwargs.update(params)
        if 'EMAIL_BACKEND' not in kwargs:
            kwargs['EMAIL_BACKEND'] = 'lux.core.mail.LocalMemory'
        config_file = config_file or self.config_file
        if argv is None:
            argv = []
        if '--log-level' not in argv:
            argv.append('--log-level')
            levels = self.cfg.loglevel if hasattr(self, 'cfg') else ['none']
            argv.extend(levels)
        app = lux.App(config_file, argv=argv, **kwargs).setup()
        if self.apps is None:
            self.apps = []
        self.apps.append(app)
        return app

    def request_start_response(self, app, path=None, HTTP_ACCEPT=None,
                               headers=None, body=None, **extra):
        extra['HTTP_ACCEPT'] = HTTP_ACCEPT or '*/*'
        request = app.wsgi_request(path=path, headers=headers, body=body,
                                   extra=extra)
        start_response = mock.MagicMock()
        return request, start_response

    def request(self, app=None, **params):
        if not app:
            app = self.application()
        request, sr = self.request_start_response(app, **params)
        response = app(request.environ, sr)
        self.assertEqual(response, request.response)
        return request

    def fetch_command(self, command, out=None):
        '''Fetch a command.'''
        out = out or StringIO() if ispy3k else BytesIO()
        app = self.application()
        cmd = app.get_command(command, stdout=out)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd

    def authenticity_token(self, doc):
        name = doc.find('meta', attrs={'name': 'csrf-param'})
        value = doc.find('meta', attrs={'name': 'csrf-token'})
        if name and value:
            name = name.attrs['content']
            value = value.attrs['content']
            return {name: value}

    def post(self, app=None, path=None, content_type=None, body=None,
             headers=None, **extra):
        extra['REQUEST_METHOD'] = 'POST'
        headers = headers or []
        if body and not isinstance(body, bytes):
            if content_type is None:
                body, content_type = encode_multipart_formdata(body)
        if content_type:
            headers.append(('content-type', content_type))
        return self.request(app, path=path, headers=headers,
                            body=body, **extra)