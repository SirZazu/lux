import lux
from lux.extensions.static import HtmlContent, SphinxDocs, Sitemap

from .ui import add_css


APP_NAME = 'Lux'
HTML_TITLE = 'Lux - Crafting super web applications with Python and AngularJS'
SITE_URL = 'http://quantmind.github.io/lux'
#SITE_URL = 'http://localhost:9031/lux'
EXTENSIONS = ('lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.angular',
              'lux.extensions.code',
              'lux.extensions.static')
ANGULAR_UI_ROUTER = True
STATIC_API = 'jsonapi'
CONTEXT_LOCATION = 'luxsite/context'
STATIC_LOCATION = '../docs/luxsite'
MD_EXTENSIONS = ['extra', 'meta', 'toc']
CODE_HIGHLIGHT_THEME = 'railscasts'
FAVICON = 'luxsite/favicon.ico'
REQUIREJS = ('luxsite/luxsite',)
HTML_LINKS = ({'href': 'luxsite/lux-114.png',
               'sizes': '57x57',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-114.png',
               'sizes': '114x114',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-144.png',
               'sizes': '72x72',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-144.png',
               'sizes': '144x144',
               'rel': 'apple-touch-icon'},
              'luxsite/luxsite.css')


class Extension(lux.Extension):

    def middleware(self, app):
        content = HtmlContent('/',
                              Sitemap('/sitemap.xml'),
                              SphinxDocs('/docs/', dir='luxsite/docs',
                                         meta={'template': 'doc.html'}),
                              meta={'template': 'main.html'},
                              dir='luxsite/site',
                              drafts=None)
        return [content]

