"""
SQLObject-wrapping schema
"""
import sqlobject
import schema
import validators
from api import Invalid
from declarative import classinstancemethod

class SQLSchema(schema.Schema):

    """
    SQLSchema objects are FormEncode schemas that are attached to
    specific instances or classes.
    
    In ``.from_python(object)`` these schemas serialize SQLObject
    instances to dictionaries of values, or to empty dictionaries
    (when serializing a class).  The object passed in should either be
    None (new or default object) or the object to edit.
    
    In ``.to_python`` these either create new objects (when no ``id``
    field is present) or edit an object by the included id.  The
    returned value is the created object.

    SQLObject validators are applied to the input, as is notNone
    restrictions.  Also column restrictions and defaults are applied.
    Note that you can add extra fields to this schema, and they will
    be applied before the SQLObject validators and restrictions.  This
    means you can use, for instance, ``validators.DateConverter()``
    (assigning it to the same name as the SQLObject class's date
    column) to have this serialize date columns to/from strings.

    You can override ``update_object`` to change the actual
    instantiation.

    The basic idea is that a SQLSchema 'wraps' a class or instance
    (most typically a class).  So it would look like::

        class PersonSchema(SQLSchema):
            wrap = Person

        ps = PersonSchema()
        form_defaults = ps.from_python(None)
        new_object = ps.to_python(form_input)
        form_defaults = ps.from_python(aPerson)
        edited_person = ps.to_python(edited_form_input)

    To override the encoding and decoding, use ``update_object`` and
    ``get_current``.  In this example, lets say that we take a single
    name field instead of a first_name and last_name (which is what
    the database has)::

        class PersonSchema(SQLSchema):
            wrap = Person
            
            def update_object(self, columns, extra, state):
                name = extra.pop('name')
                fname, lname = name.split(None, 1)
                columns['first_name'] = fname
                columns['last_name'] = lname
                return super(PersonSchema).update_object(
                    columns, extra, state)

            def get_current(self, obj, state):
                value = super(PersonSchema).get_current(obj, state)
                value['name'] = '%(first_name)s %(last_name)s' % value
                del value['first_name']
                del value['last_name']
            
    """


    # This is the object that gets wrapped, either a class (this is a
    # creating schema) or an instance (this is an updating schema):
    wrap = None

    # If this is true, then to_python calls that include an id
    # will cause an object update if this schema wraps a class.
    allow_edit = True

    # If this is true, then the IDs will be signed; you must also
    # give a secret if that is true.
    sign_id = False
    # This can be any object with a __str__ method:
    # @@: Should we just take a signer validator?
    secret = None

    # The SQLObject schema will pick these up:
    allow_extra_fields = True
    filter_extra_fields = False
    ignore_key_missing = True

    messages = {
        'invalidID': 'The id is not valid: %(error)s',
        'badID': 'The id %(value)r did not match the expected id',
        'notNone': 'You may not provide None for that value',
        }
    
    def __initargs__(self, new_attrs):
        schema.Schema.__initargs__(self, new_attrs)
        if self.sign_id:
            self._signer = validators.SignedString(secret=self.secret)

    def is_empty(self, value):
        # For this class, None has special meaning, and isn't empty
        return False

    #@classinstancemethod
    def object(self, cls):
        """
        Returns the object this schema wraps
        """
        me = self or cls
        assert me.wrap is not None, (
            "You must give %s an object to wrap" % me)
        if isinstance(me.wrap, (list, tuple)):
            # Special lazy case...
            assert len(me.wrap) == 2, (
                "Lists/tuples must be (class, obj_id); not %r"
                % me.wrap)
            return me.wrap[0].get(me.wrap[1])
        else:
            return me.wrap

    object = classinstancemethod(object)

    #@classinstancemethod
    def instance(self, cls):
        """
        Returns true if we wrap a SQLObject instance, false if
        we wrap a SQLObject class
        """
        me = self or cls
        assert me.wrap is not None, (
            "You must give %s an object to wrap" % me)
        if isinstance(me.wrap, (list, tuple)):
            return True
        elif isinstance(me.wrap, sqlobject.SQLObject):
            return True
        else:
            return False

    instance = classinstancemethod(instance)

    def _from_python(self, obj, state):
        if obj is None:
            obj = self.object()
        if isinstance(obj, sqlobject.SQLObject):
            value_dict = self.get_current(obj, state)
        else:
            value_dict = self.get_defaults(obj, state)
        result = schema.Schema._from_python(self, value_dict, state)
        if 'id' in result and self.sign_id:
            result['id'] = self._signer.from_python(result['id'])
        return result

    def _to_python(self, value_dict, state):
        value_dict = value_dict.copy()
        add_values = {}
        if self.instance() or value_dict.get('id'):
            if not self.instance() and not self.allow_edit:
                raise Invalid(self.message('editNotAllowed', state, value=value_dict['id']),
                              value_dict['id'], state)
            if 'id' not in value_dict:
                raise Invalid(self.message('missingValue', state),
                              None, state)
            id = value_dict.pop('id')
            if self.sign_id:
                id = self._signer.to_python(id)
            try:
                id = self.object().sqlmeta.idType(id)
            except ValueError, e:
                raise Invalid(self.message('invalidID', state, error=e),
                              id, state)
            add_values['id'] = id
        elif 'id' in value_dict and not value_dict['id']:
            # Empty id, which is okay and means we are creating
            # an object
            del value_dict['id']
        result = schema.Schema._to_python(self, value_dict, state)
        result, extra = self._to_python_dictionary(result, state)
        result.update(add_values)
        return self.update_object(result, extra, state)

    def update_object(self, columns, extra_fields, state):
        """
        Actually do the action, like create or update an object.
        """
        if extra_fields:
            errors = {}
            for key in extra_fields.keys():
                errors[key] = Invalid(
                    self.message('notExpected', state, name=repr(key)),
                    columns, state)
            raise Invalid(
                schema.format_compound_error(errors),
                columns, state,
                error_dict=errors)
        obj = self.object()
        create = False
        if self.instance():
            if obj.id != columns['id']:
                raise Invalid(self.message('badID', state, value=columns['id']),
                              columns['id'], state)
            del columns['id']
        elif 'id' in columns:
            obj = obj.get(columns['id'])
            del columns['id']
        else:
            create = True
        if create:
            obj = obj(**columns)
        else:
            obj.set(**columns)
        return obj

    def _to_python_dictionary(self, value_dict, state):
        obj = self.object()
        sqlmeta = obj.sqlmeta
        columns = sqlmeta.columns
        extra = value_dict.copy()
        found = []
        for name, value in value_dict.items():
            if name not in columns:
                continue
            found.append(name)
            del extra[name]
            if columns[name].validator:
                # We throw the result away, but let the exception
                # get through
                columns[name].validator.to_python(value, state)
            if columns[name].notNone and value is None:
                # This isn't present in the validator information
                exc = Invalid(self.message('notNone', state),
                              value, state)
                raise Invalid(
                    '%s: %s' % (name, exc),
                    value_dict, state,
                    error_dict={name: exc})
            
        if not isinstance(obj, sqlobject.SQLObject):
            for name, column in columns.items():
                if (name not in found
                    and column.default is sqlobject.col.NoDefault):
                    exc = Invalid(self.message('missingValue', state),
                                  value_dict, state)
                    raise Invalid(
                        '%s: %s' % (name, exc),
                        value_dict, state,
                        error_dict={name: exc})
        for key in extra:
            del value_dict[key]
        return value_dict, extra

    def get_current(self, obj, state):
        if hasattr(obj.sqlmeta, 'asDict'):
            # Added in 0.8
            result = obj.sqlmeta.asDict()
        else:
            result = {}
            for key in obj.sqlmeta.columns:
                result[key] = getattr(obj, key)
            result['id'] = obj.id
        return result

    def get_defaults(self, soClass, state):
        # @@: Should this take into account column defaults?
        # Yes!  Hmm... need to fix.
        return {}
            
