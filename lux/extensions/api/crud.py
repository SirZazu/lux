from pulsar import MethodNotAllowed, PermissionDenied, Http404
from pulsar.apps.wsgi import Json

import lux
from lux import route


def html_form(request, Form, name):
    form = Form(request)
    html = form.layout(enctype='application/json',
                       controller=False).data('api', name)
    return html


class ModelManager(object):
    '''Model-based :ref:`ContentManager <api-content>`

    .. attribute:: model

        The model managed by this manager
    '''
    def __init__(self, model=None, form=None, edit_form=None):
        self.model = model
        self.form = form
        self.edit_form = edit_form or form

    def collection(self, limit, offset=0, text=None):
        '''Retrieve a collection of models
        '''
        raise NotImplementedError

    def get(self, id):
        '''Fetch an instance by its id
        '''
        raise NotImplementedError

    def instance(self, instance):
        '''convert the instance into a JSON-serializable dictionary
        '''
        raise NotImplementedError

    def limit(self, request):
        '''Limit for a items request'''
        cfg = request.config
        user = request.cache.user
        MAXLIMIT = (cfg['API_LIMIT_AUTH'] if user.is_authenticated() else
                    cfg['API_LIMIT_NOAUTH'])
        limit = request.body_data().get(cfg['API_LIMIT_KEY'],
                                        cfg['API_LIMIT_DEFAULT'])
        return min(limit, MAXLIMIT)

    def offset(self, request):
        cfg = request.config
        return request.body_data().get(cfg['API_OFFSET_KEY'], 0)

    def create_model(self, data):
        raise NotImplementedError

    def has_permission(self, user, level, instance=None):
        raise NotImplementedError

    def _setup(self, columns):
        pass


class CRUD(lux.Router):
    manager = lux.RouterParam(ModelManager())

    def get(self, request):
        limit = self.manager.limit(request)
        offset = self.manager.offset(request)
        collection = self.manager.collection(limit, offset)
        data = self.collection_data(request, collection)
        return Json(data).http_response(request)

    def post(self, request):
        '''Create a new model
        '''
        manager = self.manager
        form_class = manager.form
        if not form_class:
            raise MethodNotAllowed
        auth = request.cache.auth_backend
        if auth and auth.has_permission(request, auth.CREATE, manager.model):
            data, files = request.data_and_files()
            form = form_class(request, data=data, files=files)
            if form.is_valid():
                instance = manager.create_model(form.cleaned_data)
                data = self.instance_data(request, instance)
                request.response.status_code = 201
            else:
                data = form.tojson()
            return Json(data).http_response(request)
        raise PermissionDenied

    @route('<id>')
    def read(self, request):
        '''Read an instance
        '''
        instance = self.manager.get(request.urlargs['id'])
        if not instance:
            raise Http404
        url = request.absolute_uri()
        data = self.instance_data(request, instance, url=url)
        return Json(data).http_response(request)

    @route('<id>')
    def post_update(self, request):
        manager = self.manager
        instance = manager.get(request.urlargs['id'])
        if not instance:
            raise Http404
        form_class = manager.form
        if not form_class:
            raise MethodNotAllowed
        auth = request.cache.auth_backend
        if auth.has_permission(request, auth.UPDATE, instance):
            data, files = request.data_and_files()
            form = form_class(request, data=data, files=files)
            if form.is_valid():
                instance = manager.update_model(instance, form.cleaned_data)
                data = self.manager.instance(instance)
            else:
                data = form.tojson()
            return Json(data).http_response(request)
        raise PermissionDenied

    def instance_data(self, request, instance, url=None):
        data = self.manager.instance(instance)
        url = url or request.absolute_uri('%s' % data['id'])
        data['api_url'] = url
        return data

    def collection_data(self, request, collection):
        d = self.instance_data
        return [d(request, instance) for instance in collection]

