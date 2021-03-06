from pulsar import Http404
from pulsar.utils.html import nicename

import lux
from lux import route
from lux.extensions import rest
from lux.extensions.angular import grid

# Override Default Admin Router for a model
adminMap = {}


class register:
    '''Decorator to register an admin router class with
    REST model.

    :param model: a string or a :class:`~lux.extensions.rest.RestModel`
    '''
    def __init__(self, model):
        if not isinstance(model, rest.RestModel):
            model = rest.RestModel(model)
        self.model = model

    def __call__(self, cls):
        assert issubclass(cls, AdminModel)
        assert cls is not AdminModel
        cls.model = self.model
        adminMap[self.model.name] = cls


class AdminRouter(lux.HtmlRouter):
    '''Base class for all Admin Routers
    '''
    def response_wrapper(self, callable, request):
        app = request.app
        backend = request.cache.auth_backend
        permission = app.config['ADMIN_PERMISSIONS']
        if backend and permission:
            if backend.has_permission(request, permission, rest.READ):
                return callable(request)
            else:
                raise Http404
        else:
            return callable(request)

    def context(self, request, context):
        '''Add the admin navigation to the javascript context
        '''
        admin = self.admin_root()
        if admin:
            doc = request.html_document
            doc.jscontext['navigation'] = admin.sitemap(request.app)

    def get_html(self, request):
        return request.app.render_template('partials/admin.html')

    def admin_root(self):
        router = self
        while router and not isinstance(router, Admin):
            router = router.parent
        return router


class Admin(AdminRouter):
    '''Admin Root

    This router containes all Admin router managing models
    '''
    _sitemap = None

    def __init__(self, *args, **kwargs):
        # set self as the angular root
        self._angular_root = self
        super().__init__(*args, **kwargs)

    def sitemap(self, app):
        if self._sitemap is None:
            sections = {}
            sitemap = []
            for child in self.routes:
                if isinstance(child, AdminModel):
                    section, info = child.info(app)

                    if section not in sections:
                        items = []
                        sections[section] = {'name': section,
                                             'items': items}
                        sitemap.append(sections[section])
                    else:
                        items = sections[section]['items']

                    items.append(info)

            self._sitemap = sitemap
        return self._sitemap


class AdminModel(rest.RestMixin, AdminRouter):
    '''Router for rendering an admin section relative to
    a given rest model
    '''
    section = None
    icon = None
    '''An icon for this Admin section
    '''
    def info(self, app):
        '''Information for admin navigation
        '''
        name = nicename(self.model.name)
        info = {'title': name,
                'name': name,
                'href': self.full_route.path,
                'icon': self.icon}
        return self.section, info

    def get_html(self, request):
        model = self.model
        app = request.app
        options = dict(target=model.get_target(request))
        context = {'grid': grid(options)}
        return app.render_template('partials/admin-list.html', context)


class CRUDAdmin(AdminModel):
    '''An Admin model Router for adding and updating models
    '''
    form = None
    updateform = None
    addtemplate = 'partials/admin-add.html'

    @route()
    def add(self, request):
        '''Add a new model
        '''
        return self.get_form(request, self.form)

    @route('<id>')
    def update(self, request):
        '''Edit an existing model
        '''
        form = self.updateform or self.form
        return self.get_form(request, form, request.urlargs['id'])

    def get_form(self, request, form, id=None):
        if not form:
            raise Http404
        target = self.model.get_target(request, id)
        html = form().as_form(action=target)
        context = {'html_form': html.render()}
        html = request.app.render_template(self.addtemplate, context)
        return self.get(request, html=html)
