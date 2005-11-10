import declarative

__all__ = ['NoDefault', 'Invalid', 'Validator', 'Identity',
           'FancyValidator', 'is_validator']

class NoDefault:
    pass

def is_validator(obj):
    return (isinstance(obj, Validator) or
            (isinstance(obj, type) and
             issubclass(obj, Validator)))

class Invalid(Exception):

    """
    This is raised in response to invalid input.  It has several
    public attributes:

    msg:
        The message, *without* values substituted.  For instance, if
        you want HTML quoting of values, you can apply that.
    substituteArgs:
        The arguments (a dictionary) to go with `msg`.
    str(self):
        The message describing the error, with values substituted.
    value:
        The offending (invalid) value.
    state:
        The state that went with this validator.  This is an
        application-specific object.
    error_list:
        If this was a compound validator that takes a repeating value,
        and sub-validator(s) had errors, then this is a list of those
        exceptions.  The list will be the same length as the number of
        values -- valid values will have None instead of an exception.
    error_dict:
        Like `error_list`, but for dictionary compound validators.
    """

    def __init__(self, msg,
                 value, state, error_list=None, error_dict=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.value = value
        self.state = state
        self.error_list = error_list
        self.error_dict = error_dict
        assert (not self.error_list or not self.error_dict), (
                "Errors shouldn't have both error dicts and lists "
                "(error %s has %s and %s)"
                % (self, self.error_list, self.error_dict))

    def __str__(self):
        val = self.msg
        #if self.value:
        #    val += " (value: %s)" % repr(self.value)
        return val    

    def unpack_errors(self):
        """
        Returns the error as a simple data structure -- lists,
        dictionaries, and strings.
        """
        if self.error_list:
            assert not self.error_dict
            result = []
            for item in self.error_list:
                if not item:
                    result.append(item)
                else:
                    result.append(item.unpack_errors())
            return result
        elif self.error_dict:
            result = {}
            for name, item in self.error_dict.items():
                if isinstance(item, (str, unicode)):
                    result[name] = item
                else:
                    result[name] = item.unpack_errors()
            return result
        else:
            return self.msg


############################################################
## Base Classes
############################################################

class Validator(declarative.Declarative):

    """
    The base class of most validators.  See `IValidator` for more, and
    `FancyValidator` for the more common (and more featureful) class.
    """

    _messages = {}
    if_missing = NoDefault
    repeating = False
    compound = False

    __singletonmethods__ = ('to_python', 'from_python')

    def __classinit__(cls, new_attrs):
        if new_attrs.has_key('messages'):
            cls._messages = cls._messages.copy()
            cls._messages.update(cls.messages)
            del cls.messages

    def __init__(self, *args, **kw):
        if kw.has_key('messages'):
            self._messages = self._messages.copy()
            self._messages.update(kw['messages'])
            del kw['messages']
        declarative.Declarative.__init__(self, *args, **kw)

    def to_python(self, value, state=None):
        return value

    def from_python(self, value, state=None):
        return value

    def message(self, msgName, state, **kw):
        try:
            return self._messages[msgName] % kw
        except KeyError, e:
            raise KeyError(
                "Key not found (%s) for %r=%r %% %r (from: %s)"
                % (e, msgName, self._messages.get(msgName), kw,
                   ', '.join(self._messages.keys())))        

class _Identity(Validator):
    def __repr__(self):
        return 'validators.Identity'
Identity = _Identity()

class FancyValidator(Validator):

    """
    FancyValidator is the (abstract) superclass for various validators
    and converters.  A subclass can validate, convert, or do both.
    There is no formal distinction made here.

    Validators have two important external methods:
    
    * .to_python(value, state):
      Attempts to convert the value.  If there is a problem, or the
      value is not valid, an Invalid exception is raised.  The
      argument for this exception is the (potentially HTML-formatted)
      error message to give the user.

    * .from_python(value, state):
      Reverses to_python.

    There are five important methods for subclasses to override,
    however none of these *have* to be overridden, only the ones that
    are appropriate for the validator:
    
    * __init__():
      if the `declarative.Declarative` model doesn't work for this.

    * .validate_python(value, state):
      This should raise an error if necessary.  The value is a Python
      object, either the result of to_python, or the input to
      from_python.

    * .validate_other(value, state):
      Validates the source, before to_python, or after from_python.
      It's more common to use `.validate_python()` however.

    * ._to_python(value, state):
      This returns the converted value, or raises an Invalid
      exception if there is an error.  The argument to this exception
      should be the error message.

    * ._from_python(value, state):
      Should undo .to_python() in some reasonable way, returning
      a string.

    Validators should have no internal state besides the
    values given at instantiation.  They should be reusable and
    reentrant.

    All subclasses can take the arguments/instance variables:
    
    * if_empty:
      If set, then this value will be returned if the input evaluates
      to false (empty list, empty string, None, etc), but not the 0 or
      False objects.  This only applies to ``.to_python()``.
      
    * not_empty:
      If true, then if an empty value is given raise an error.
      (Both with ``.to_python()`` and also ``.from_python()``
      if ``.validate_python`` is true).

    * strip:
      If true and the input is a string, strip it (occurs before empty
      tests).

    * if_invalid:
      If set, then when this validator would raise Invalid during
      ``.to_python()``, instead return this value.
      
    * if_invalid_python:
      If set, when the Python value (converted with
      ``.from_python()``) is invalid, this value will be returned.

    * validate_python:
      If False (default True), then ``.validate_python()`` and
      ``.validate_other()`` will not be called when
      ``.from_python()`` is used.
    """

    if_invalid = NoDefault
    if_invalid_python = NoDefault
    if_empty = NoDefault
    not_empty = False
    validate_python = True
    strip = False

    messages = {
        'empty': "Please enter a value",
        'badType': "The input must be a string (not a %(type)s: %(value)r)",
        'noneType': "The input must be a string (not None)",
        }

    def to_python(self, value, state=None):
        try:
            if self.strip and isinstance(value, (str, unicode)):
                value = value.strip()
            if not value and value != 0:
                # False/0 are not "empty"
                if self.if_empty is not NoDefault:
                    return self.if_empty
                if self.not_empty:
                    raise Invalid(self.message('empty', state), value, state)
            vo = self.validate_other
            if vo:
                vo(value, state)
            tp = self._to_python
            if tp:
                value = tp(value, state)
            vp = self.validate_python
            if vp:
                vp(value, state)
            return value
        except Invalid:
            if self.if_invalid is NoDefault:
                raise
            else:
                return self.if_invalid

    def from_python(self, value, state=None):
        try:
            if self.strip and isinstance(value, (str, unicode)):
                value = value.strip()
            if self.validate_python:
                if (not value and value != 0
                    and self.not_empty):
                    raise Invalid(self.message('empty', state),
                                  value, state)
                vp = self.validate_python
                if vp:
                    vp(value, state)
                fp = self._from_python
                if fp:
                    value = fp(value, state)
                vo = self.validate_other
                if vo:
                    vo(value, state)
                return value
            else:
                fp = self._from_python
                if fp:
                    value = self._from_python(value, state)
                return value
        except Invalid:
            if self.if_invalid_python is NoDefault:
                raise
            else:
                return self.if_invalid_python


    def assert_string(self, value, state):
        if not isinstance(value, (str, unicode)):
            raise Invalid(self.message('badType', state,
                                       type=type(value), value=value),
                          value, state)
    
    validate_python = None
    validate_other = None
    _to_python = None
    _from_python = None

