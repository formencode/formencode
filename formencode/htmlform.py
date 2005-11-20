"""
.. note::

   This is deprecated, as it's not that helpful.

Class to encapsulate an HTML form, using htmlfill and
htmlfill_schemabuilder

Usage::

    html = '<form action=...>...</form>'
    class FormSchema(schema.Schema):
        f1 = ...
    form = HTMLForm(html, FormSchema())
    errors = {}
    if form_submitted:
        form_result, errors = form.validate(request_dict)
        if not errors:
            do_action(form_result)
            return
    defaults = form.schema.from_python(get_defaults_from_model())
    defaults.update(request_dict)
    write(form.render(defaults, errors)
    
You can also embed the schema in the form, using form:required, etc.,
tags.  

"""

import htmlfill
import htmlfill_schemabuilder
from api import Invalid
import warnings

class HTMLForm(object):

    def __init__(self, form, schema=None,
                 auto_insert_errors=True):
        warnings.warn(
            'HTMLForm has been deprecated; use the htmlfill and '
            'htmlfill_schemabuilder modules directly.',
            DeprecationWarning)
        self.form = form
        self._schema = schema
        self.auto_insert_errors = auto_insert_errors
        
    def schema__get(self):
        if self._schema is not None:
            return self._schema
        self._schema = self.parse_schema()

    def schema__set(self, value):
        self._schema = value

    def schema__del(self):
        self._schema = None

    schema = property(schema__get, schema__set, schema__del)

    def parse_schema(self):
        listener = htmlfill_schemabuilder.SchemaBuilder()
        p = htmlfill.FillingParser(
            defaults={}, listener=listener)
        p.feed(self.form)
        p.close()
        return listener.schema()

    def render(self, defaults={}, errors={}, use_all_keys=False):
        if self.auto_insert_errors:
            auto_error_formatter = htmlfill.default_formatter
        else:
            auto_error_formatter = None
        p = htmlfill.FillingParser(
            defaults=defaults, errors=errors,
            use_all_keys=use_all_keys,
            auto_error_formatter=auto_error_formatter)
        p.feed(self.form)
        p.close()
        return p.text()

    def validate(self, request_dict, state=None):
        schema = self.schema
        try:
            result = schema.to_python(request_dict, state=state)
            return result, None
        except Invalid, e:
            return None, e.unpack_errors()

    
