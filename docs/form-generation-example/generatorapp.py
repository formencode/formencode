from webob import Request, Response
from webob import exc
from tempita import HTMLTemplate, html
import os
import generatoreditable
import textwrap

template_dir = os.path.dirname(__file__)
# Dict of template_name: (template_mtime, template_object)
_templates = {}

def get_template(template_name):
    filename = os.path.join(template_dir, template_name)
    mtime = os.stat(filename).st_mtime
    if (template_name not in _templates
        or _templates[template_name][0] < mtime):
        _templates[template_name] = (mtime, HTMLTemplate.from_filename(filename))
    return _templates[template_name][1]



class CrudApp(object):

    def __init__(self):
        self.objects = {}
        self.object_classes = dict(
            State: generatoreditable.State,
            )

    def __call__(self, environ, start_response):
        req = Request(environ)
        name = req.path_info_peek()
        req.urlvars['generatorapp.root'] = req.application_uri
        if not name:
            # Index page:
            resp = self.index(req)
        elif name not in self.object_classes:
            resp = exc.HTTPNotFound(
                "No class is registered with the name %r" % name)
        else:
            resp = self.crud(req, self.object_classes[name])
        return resp(environ, start_response)

    def index(self, req):
        tmpl = get_template('index.html.tmpl')
        return Response(
            tmpl.substitute(req=req,
                            crudapp=self,
                            object_classes=self.object_classes))
    
    def crud(self, req, object_class):
        obj_class = req.urlvars['generatorapp.class']
        name = req.path_info_peek()
        if not name:
            return self.crud_index(req, object_class)
        elif name == '__create__':
            return self.crud_edit(req, object_class, None)
        else:
            try:
                obj = obj_class.get_from_url(name, req, self)
            except exc.HTTPException, e:
                return e
            return self.crut_edit(req, object_class, obj)

    def crud_index(self, req, object_class):
        tmpl = get_template('crud_index.html.tmpl')
        objects = object_class.get_all(req, crudapp)
        if isinstance(objects, dict):
            objects = sorted(objects.iteritems())
        if not isinstance(objects, list):
            objects = list(objects)
        return Response(
            tmpl.substitute(req=req,
                            crudapp=self,
                            objects=objects,
                            object_class=object_class))

    ## Adapters for use with templates:

    def render_template(self_, obj, attr, default, **kw):
        tmpl = getattr(obj, attr, None)
        if not tmpl:
            return default
        if isinstance(obj, type):
            obj_class = obj
        else:
            obj_class = obj.__class__
        if isinstance(tmpl, basestring):
            tmpl = textwrap.dedent(tmpl).strip()
            tmpl = HTMLTemplate(tmpl, name="%s.%s.%s" % 
                                (obj_class.__module__, object_class.__name__, attr))
        return tmpl.substitute(crudapp=self_, **kw)|html

    def object_class_title(self, req, cls):
        return self.render_template(
            cls, 'class_title', cls.__name__, req=req, class_=cls)
    
    def object_class_description(self, req, cls):
        return self.render_template(
            cls, 'class_description', cls.__doc__, req=req, class_=cls)

    def object_title(self, req, obj):
        return self.render_template(
            obj, 'title', repr(obj), req=req, self=obj)

    def object_description(self, req, obj):
        return self.render_template(
            obj, 'description', None, req=req, self=obj)

    
    
