from declarative import DeclarativeMeta, Declarative
from api import *

############################################################
## Compound Validators
############################################################

class CompoundValidatorMeta(DeclarativeMeta):
    
    def __new__(meta, class_name, bases, d):
        cls = DeclarativeMeta.__new__(meta, class_name, bases, d)
        cls.validators = cls.validators[:]
        toAdd = []
        for name, value in d.items():
            if name in ('view',):
                continue
            validator = adapt_validator(value)
            if validator and validator is not Identity:
                toAdd.append((name, value))
                # @@: Should we really delete too?
                delattr(cls, name)
        toAdd.sort()
        cls.validators.extend([v for n, v in toAdd])
        return cls

class CompoundValidator(Validator):

    __metaclass__ = CompoundValidatorMeta

    if_invalid = NoDefault

    validators = []

    __unpackargs__ = ('*', 'validatorArgs')

    __mutableattributes__ = ('validators',)

    def __init__(self, *args, **kw):
        Validator.__init__(self, *args, **kw)
        self.validators = self.validators[:]
        self.validators.extend(self.validatorArgs)

    def _reprVars(names):
        return [n for n in Validator._reprVars(names)
                if n != 'validatorArgs']
    _reprVars = staticmethod(_reprVars)

    def validatorForState(self, state):
        if Validator.validatorForState(self, state) is None:
            return None
        changes = 0
        new = []
        for validator in self.validators:
            v = adapt_validator(validator, state=state)
            if v is not validator:
                changes = 1
            if v is not None:
                new.append(v)
        if not changes:
            return self
        return self(validators=new)

    def attempt_convert(self, value, state, convertFunc):
        raise NotImplementedError, "Subclasses must implement attempt_convert"

    def to_python(self, value, state=None):
        return self.attempt_convert(value, state,
                                    to_python)
    
    def from_python(self, value, state=None):
        return self.attempt_convert(value, state,
                                    from_python)

class Any(CompoundValidator):
    
    """
    This class is like an 'or' operator for validators.  The first
    validator/converter that validates the value will be used.  (You
    can pass in lists of validators, which will be ANDed)
    """

    def attempt_convert(self, value, state, convertFunc):
        lastException = None
        for validator in self.validators:
            try:
                return convertFunc(validator, value, state)
            except Invalid, e:
                lastException = e
        if self.if_invalid is NoDefault:
            raise lastException
        else:
            return self.if_invalid

class All(CompoundValidator):

    """
    This class is like an 'and' operator for validators.  All
    validators must work, and the results are passed in turn through
    all validators for conversion.
    """

    def __repr__(self):
        return '<All %s>' % self.validators

    def attempt_convert(self, value, state, validate):
        try:
            for validator in self.validators:
                value = validate(validator, value, state)
            return value
        except Invalid:
            if self.if_invalid is NoDefault:
                raise
            return self.if_invalid

    def with_validator(self, validator):
        """
        Adds the validator (or list of validators) to a copy of
        this validator.
        """
        new = self.validators[:]
        if isinstance(validator, list) or isinstance(validator, tuple):
            new.extend(validator)
        else:
            new.append(validator)
        return self.__class__(*new, **{'if_invalid': self.if_invalid})

    def join(cls, *validators):
        """
        Joins several validators together as a single validator,
        filtering out None and trying to keep `All` validators from
        being nested (which isn't needed).
        """
        validators = filter(lambda v: v and v is not Identity, validators)
        if not validators:
            return Identity
        if len(validators) == 1:
            return validators[0]
        elif isinstance(validators[0], All):
            return validators[0].with_validator(validators[1:])
        else:
            return cls(*validators)
    join = classmethod(join)

    def if_missing__get(self):
        for validator in self.validators:
            v = adapt_validator(validator).if_missing
            if v is not NoDefault:
                return v
        return NoDefault
    if_missing = property(if_missing__get)

def _adaptListToAll(v, protocol):
    if not v:
        return Identity
    if len(v) == 1:
        return adapt_validator(v[0])
    return All(*v)

# @@: maybe this is fishy?
#import protocols
#from interfaces import *
#protocols.declareAdapter(_adaptListToAll, [IValidator],
#                         forTypes=[list, tuple])
