from formencode.schema import Schema
from formencode import validators

class AbstractEditable(object):
    """
    This represents a basic editable object.  It's more of a
    self-documenting example; you should not subclass this object.
    """

    class_title = '''
    Title that can use class_ and req variables.  Defaults to __name__ if not set
    '''

    class_description = '''
    Longer description that can use class_ and req variables.  Default to __doc__ if not set.
    '''

    title = '''
    Title for an instance that can use self and req variables.  Defaults to repr() if not set.
    '''

    description = '''
    Description for an instance that can use self and req variables.  Defaults to empty if not set.
    '''

    @classmethod
    def get_from_url(cls, urlsegment, req, crudapp):
        """
        Gets one object from a url segment.  You should only use the
        req object for access control.  You may raise a
        webob.exc.HTTPException exception.
        """
        raise NotImplementedError

    @classmethod
    def get_all(cls, req, crudapp):
        """
        Returns all the objects for this class, as a dictionary of
        {urlsegment: object} or a list of [(urlsegment, object)] (or
        an iterator of those tuples).
        """
        raise NotImplementedError

    @classmethod
    def default_attrs(cls, req, crudapp):
        """
        Returns a dictionary of the default attrs for a new object
        """
        raise NotImplementedError

    @classmethod
    def create_object(cls, req, crudapp, **attrs):
        """
        Creates a new object using the given attrs, and returns that object.
        """
        raise NotImplementedError

    def object_attrs(self, req, crudapp):
        """
        Returns the object attrs for this object.
        """
        raise NotImplementedError

    urlsegment = property(doc="Gives the instance's urlsegment for fetching")

    def update_object(self, req, crudapp, **attrs):
        """
        Updates an existing instance using the given attrs.
        """
        raise NotImplementedError
    
    # Used to provide an ordering for fields; if this exists then any
    # fields not listed will end up last.  Other fields will be
    # ordered according to this:
    field_order = ['field1', 'field2']

    # A schema to validate and convert the attrs:
    schema = Schema()

    @classmethod
    def validate_fields(cls, attrs, req, crudapp, state, self):
        """
        This is a simpler setup for validating the attrs; it may
        update the attrs in-place.

        state is the formencode state object

        self will be None if this is a create
        """
        pass

    @classmethod
    def fields(cls, req, crudapp, self=None):
        """
        A classmethod (if called on an instance, then self is also
        passed in).  This returns a list of fields to use to edit the
        form.
        """
        

class State(object):

    _states = {}

    class_title = 'States'
    class_description = '''
    All the states.  Contains the full state name and the state postal code.
    '''
    title = '''The state {{self.name}} (code {{self.code}})'''
    
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self._states[code] = self

    @classmethod
    def get_from_url(cls, urlsegment, req, crudapp):
        ## FIXME: not found?
        return cls._states[urlsegment]

    @classmethod
    def get_all(cls, req, crudapp):
        return cls._states

    @classmethod
    def create_object(cls, req, crudapp, name, code):
        return cls(name, code)

    def object_attrs(self, req, crudapp):
        return dict(name=self.name, code=self.code)

    @property
    def urlsegment(self):
        return self.code

    def update_object(self, req, crudapp, name, code):
        self.name = name
        self.code = code

    field_order = ['name', 'code']

    def validate_fields(self, attrs, req, crudapp, state):
        code = attrs['code']
        if self is None:
            if code in self._states:
                return {'code': 'A state with the code %s already exists' % code}
        attrs['code'] = attrs['code'].upper()

    class schema(Schema):
        name = validators.String(not_empty=True)
        code = validators.String(min=2, max=2)

class Address(object):

    _addresses = []
    
    def __init__(self, name, street, city, state, postal):
        self.name = name
        self.street = street
        self.city = city
        self.state = state
        self.postal = postal
        self._addresses.append(self)

    
    
