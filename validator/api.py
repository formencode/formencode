try:
    import protocols
    dummy = False
except ImportError:
    import dummy_protocols as protocols
    dummy = True
from interfaces import *
from declarative import Declarative

__all__ = ['NoDefault', 'adapt_validator', 'to_python',
           'from_python', 'Invalid', 'Validator', 'Identity',
           'FancyValidator']

class NoDefault:
    pass

def adapt_validator(obj, state=None):
    try:
        if isinstance(obj, type) and issubclass(obj, Declarative):
            obj = obj.singleton()
        if dummy:
            if not isinstance(obj, Validator):
                return None
            else:
                return obj
        validator = protocols.adapt(
            obj, IValidator)
        if validator and state:
            validator = validator.validatorForState(state)
        return validator
    except protocols.AdaptationFailure:
        return None

def to_python(validator, value, state=None):
    """
    Validates `value` (with `state`) using `validator`.  Does the
    appropriate adaptation as necessary.  Also handles the suppression
    of validation if the state's protocol doesn't match the
    validators.  (These protocols are distinct from the `protocols`
    package's concept)
    """
    validator = adapt_validator(validator, state=state)
    if validator:
        return validator.to_python(value, state)
    else:
        return value


def from_python(validator, value, state=None):
    """
    Validates `value` (with `state`) using `validator`.  Does the
    appropriate adaptation as necessary.  Also handles the suppression
    of validation if the state's protocol doesn't match the
    validators.  (These protocols are distinct from the `protocols`
    package's concept)
    """
    # @@: Ack, this isn't right at all for adaptation:
    if isinstance(validator, type):
        validator = validator.singleton()
    validator = adapt_validator(validator, state=state)
    if validator:
        return validator.from_python(value, state)
    else:
        return value


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

class Validator(Declarative):

    """
    The base class of most validators.  See `IValidator` for more, and
    `FancyValidator` for the more common (and more featureful) class.
    """

    protocols.advise(
        instancesProvide=[IValidator])

    _messages = {}
    protocols = None
    if_missing = NoDefault
    repeating = False
    compound = False

    def __classinit__(cls):
        if hasattr(cls, 'messages'):
            cls._messages = cls._messages.copy()
            cls._messages.update(cls.messages)
            del cls.messages

    def __init__(self, *args, **kw):
        Declarative.__init__(self, *args, **kw)
        if hasattr(self, 'messages'):
            self._messages = self._messages.copy()
            self._messages.update(self.messages)
            del self.messages

    def to_python(self, value, state=None):
        return value

    def from_python(self, value, state=None):
        return value

    def message(self, msgName, state, **kw):
        try:
            return self._messages[msgName] % kw
        except KeyError:
            raise KeyError, "Key not found for %r=%r %% %r" \
                  % (msgName, self._messages.get(msgName), kw)

    def validatorForState(self, state):
        myProt = self.protocols
        if myProt is None:
            return self
        stateProt = getattr(state, 'protocol', None)
        if stateProt is None:
            return self
        if stateProt in myProt:
            return self
        return None

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

    Generally these are actually invoked from the top-level to_python()
    and from_python() functions.  These functions also do protocol
    matching, so that validators can cover only specific protocols.

    There are five important methods for subclasses to override,
    however none of these *have* to be overridden, only the ones that
    are appropriate for the validator:
    * __init__():
      if the `Declarative` model doesn't work for this.
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
      to false (empty list, empty string, None, etc).
    * not_empty:
      If true, then if an empty value is given raise an error.
    * if_invalid:
      If set, then when this validator would raise Invalid, instead
      return this value.
    """

    if_invalid = NoDefault
    if_empty = NoDefault
    not_empty = False

    messages = {
        'empty': "Please enter a value",
        'badType': "The input must be a string (not a %(type)s: %(value)r)",
        'noneType': "The input must be a string (not None)",
        }

    def attempt_convert(self, value, state, pre, convert, post):
        """
        Handles both .to_python() and .from_python().
        """
        if not value:
            if self.if_empty is not NoDefault:
                return self.if_empty
            if self.not_empty:
                raise Invalid(self.message('empty', state), value, state)
        try:
            if pre:
                pre(value, state)
            if convert:
                converted = convert(value, state)
            else:
                converted = value
            if post:
                post(value, state)
            return converted
        except Invalid:
            if self.if_invalid is NoDefault:
                raise
            else:
                return self.if_invalid

    def to_python(self, value, state=None):
        return self.attempt_convert(value, state,
                                    self.validate_other,
                                    self._to_python,
                                    self.validate_python)
    
    def from_python(self, value, state=None):
        return self.attempt_convert(value, state,
                                    self.validate_python,
                                    self._from_python,
                                    self.validate_other)

    def assert_string(self, value, state):
        if not isinstance(value, (str, unicode)):
            if value is None:
                raise Invalid(self.message('noneType', state),
                              value, state)
            raise Invalid(self.message('badType', state,
                                       type=str(type(value)),
                                       value=value),
                          value, state)

    validate_python = None
    validate_other = None
    _to_python = None
    _from_python = None

