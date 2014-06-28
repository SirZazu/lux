'''Static site generator

**Requirements**: :mod:`lux.extensions.base`

Usage
=======
Put the ``lux.extensions.static`` extension into your :setting:`EXTENSIONS`
list and build the static web site via the ``build_static`` option in the
command line::

    python managet.py build_static

Parameters
================

.. lux_extension:: lux.extensions.static
'''
import os

from pulsar import ImproperlyConfigured
from pulsar.apps.wsgi import MediaRouter, FileRouter

import lux
from lux import Parameter

from .templates import DEFAULT_TEMPLATE
from .builder import Renderer, Content
from .contents import Snippet
from .blog import Blog


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('STATIC_TEMPLATE', DEFAULT_TEMPLATE,
                  'Default static template'),
        Parameter('SOURCE_SUFFIX', 'md',
                  'The default suffix of source filenames'),
        Parameter('METADATA_PROCESSORS', [],
                  'A list of functions to perocess metadata'),
        Parameter('STATIC_LOCATION', 'build',
                  'Directory where the static site is created'),
        Parameter('STATIC_SITEMAP', {},
                  'Dictionary of contents for the site'),
        Parameter('SNIPPETS_LOCATION', 'snippets',
                  'Directory where to find snippets used as content'),
        Parameter('EXTRA_FILES', (),
                  'List/tuple of additional files to copy to the '
                  ':setting:`STATIC_LOCATION`'),
        Parameter('MD_EXTENSIONS', ['extra', 'meta'],
                  'List/tuple of makrdown extensions'),
        Parameter('RELATIVE_URLS', False,
                  'Display urls as relative paths (useful during development)')
               ]

    def middleware(self, app):
        cur_path = os.curdir
        os.chdir(app.meta.path)
        path = os.path.abspath(app.config['STATIC_LOCATION'])
        if not os.path.isdir(path):
            raise ImproperlyConfigured('Static location "%s" not available' %
                                       path)
        file404 = os.path.join(path, '404.html')
        os.chdir(cur_path)
        middleware = [MediaRouter('', path, default_suffix='html',
                                  raise_404=False)]
        if os.path.isfile(file404):
            middleware.append(FileRouter('<path:path>', file404,
                                         status_code=404))
        return middleware
