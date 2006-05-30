## FormEncode, a  Form processor
## Copyright (C) 2003, Ian Bicking <ianb@colorstudy.com>
##  
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this library; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
## NOTE: In the context of the Python environment, I interpret "dynamic
## linking" as importing -- thus the LGPL applies to the contents of
## the modules, but make no requirements on code importing these
## modules.
"""
Validator/Converters for use with FormEncode.
"""

import re
DateTime = None
mxlookup = None
httplib = None
urlparse = None
socket = None
from interfaces import *
from api import *
sha = random = None
try:
    import sets
except ImportError:
    sets = None

import cgi

import fieldstorage

True, False = (1==1), (0==1)

############################################################
## Utility methods
############################################################

# These all deal with accepting both mxDateTime and datetime
# modules and types
datetime_module = None
mxDateTime_module = None

def import_datetime(module_type):
    global datetime_module, mxDateTime_module
    if module_type is None:
        try:
            if datetime_module is None:
                import datetime as datetime_module
            return datetime_module
        except ImportError:
            if mxDateTime_module is None:
                from mx import DateTime as mxDateTime_module
            return mxDateTime_module

    module_type = module_type.lower()
    assert module_type in ('datetime', 'mxdatetime')
    if module_type == 'datetime':
        if datetime_module is None:
            import datetime as datetime_module
        return datetime_module
    else:
        if mxDateTime_module is None:
            from mx import DateTime as mxDateTime_module
        return mxDateTime_module

def datetime_now(module):
    if module.__name__ == 'datetime':
        return module.datetime.now()
    else:
        return module.now()

def datetime_makedate(module, year, month, day):
    if module.__name__ == 'datetime':
        return module.date(year, month, day)
    else:
        try:
            return module.DateTime(year, month, day)
        except module.RangeError, e:
            raise ValueError(str(e))

############################################################
## Wrapper Validators
############################################################

class ConfirmType(FancyValidator):

    """
    Confirms that the input/output is of the proper type.

    Uses the parameters:

    subclass:
        The class or a tuple of classes; the item must be an instance
        of the class or a subclass.
    type:
        A type or tuple of types (or classes); the item must be of
        the exact class or type.  Subclasses are not allowed.

    Examples::
    
        >>> cint = ConfirmType(subclass=int)
        >>> cint.to_python(True)
        True
        >>> cint.to_python('1')
        Traceback (most recent call last):
            ...
        Invalid: '1' is not a subclass of <type 'int'>
        >>> cintfloat = ConfirmType(subclass=(float, int))
        >>> cintfloat.to_python(1.0), cintfloat.from_python(1.0)
        (1.0, 1.0)
        >>> cintfloat.to_python(1), cintfloat.from_python(1)
        (1, 1)
        >>> cintfloat.to_python(None)
        Traceback (most recent call last):
            ...
        Invalid: None is not a subclass of one of the types <type 'float'>, <type 'int'>
        >>> cint2 = ConfirmType(type=int)
        >>> cint2(accept_python=False).from_python(True)
        Traceback (most recent call last):
            ...
        Invalid: True must be of the type <type 'int'>
    """

    subclass = None
    type = None

    messages = {
        'subclass': "%(object)r is not a subclass of %(subclass)s",
        'inSubclass': "%(object)r is not a subclass of one of the types %(subclassList)s",
        'inType': "%(object)r must be one of the types %(typeList)s",
        'type': "%(object)r must be of the type %(type)s",
        }

    def __init__(self, *args, **kw):
        FancyValidator.__init__(self, *args, **kw)
        if self.subclass:
            if isinstance(self.subclass, list):
                self.subclass = tuple(self.subclass)
            elif not isinstance(self.subclass, tuple):
                self.subclass = (self.subclass,)
            self.validate_python = self.confirm_subclass
        if self.type:
            if isinstance(self.type, list):
                self.type = tuple(self.type)
            elif not isinstance(self.type, tuple):
                self.type = (self.type,)
            self.validate_python = self.confirm_type

    def confirm_subclass(self, value, state):
        if not isinstance(value, self.subclass):
            if len(self.subclass) == 1:
                msg = self.message('subclass', state, object=value,
                                   subclass=self.subclass[0])
            else:
                subclass_list = ', '.join(map(str, self.subclass))
                msg = self.message('inSubclass', state, object=value,
                                   subclassList=subclass_list)
            raise Invalid(msg, value, state)

    def confirm_type(self, value, state):
        for t in self.type:
            if type(value) is t:
                break
        else:
            if len(self.type) == 1:
                msg = self.message('type', state, object=value,
                                   type=self.type[0])
            else:
                msg = self.message('inType', state, object=value,
                                   typeList=', '.join(map(str, self.type)))
            raise Invalid(msg, value, state)
        return value

    def is_empty(self, value):
        return False

class Wrapper(FancyValidator):

    """
    Used to convert functions to validator/converters.

    You can give a simple function for `to_python`, `from_python`,
    `validate_python` or `validate_other`.  If that function raises an
    exception, the value is considered invalid.  Whatever value the
    function returns is considered the converted value.

    Unlike validators, the `state` argument is not used.  Functions
    like `int` can be used here, that take a single argument.

    Examples::

        >>> def downcase(v):
        ...     return v.lower()
        >>> wrap = Wrapper(to_python=downcase)
        >>> wrap.to_python('This')
        'this'
        >>> wrap.from_python('This')
        'This'
        >>> wrap2 = Wrapper(from_python=downcase)
        >>> wrap2.from_python('This')
        'this'
        >>> wrap2.from_python(1)
        Traceback (most recent call last):
          ...
        Invalid: 'int' object has no attribute 'lower'
        >>> wrap3 = Wrapper(validate_python=int)
        >>> wrap3.to_python('1')
        '1'
        >>> wrap3.to_python('a')
        Traceback (most recent call last):
          ...
        Invalid: invalid literal for int(): a
    """

    func_to_python = None
    func_from_python = None
    func_validate_python = None
    func_validate_other = None

    def __init__(self, *args, **kw):
        for n in ['to_python', 'from_python', 'validate_python',
                  'validate_other']:
            if kw.has_key(n):
                kw['func_%s' % n] = kw[n]
                del kw[n]
        FancyValidator.__init__(self, *args, **kw)
        self._to_python = self.wrap(self.func_to_python)
        self._from_python = self.wrap(self.func_from_python)
        self.validate_python = self.wrap(self.func_validate_python)
        self.validate_other = self.wrap(self.func_validate_other)

    def wrap(self, func):
        if not func:
            return None
        def result(value, state, func=func):
            try:
                return func(value)
            except Exception, e:
                raise Invalid(str(e), {}, value, state)
        return result
 
class Constant(FancyValidator):

    """
    This converter converts everything to the same thing.

    I.e., you pass in the constant value when initializing, then all
    values get converted to that constant value.

    This is only really useful for funny situations, like::

      fromEmailValidator = ValidateAny(
                               ValidEmailAddress(),
                               Constant('unknown@localhost'))
                               
    In this case, the if the email is not valid
    ``'unknown@localhost'`` will be used instead.  Of course, you
    could use ``if_invalid`` instead.

    Examples::

        >>> Constant('X').to_python('y')
        'X'
    """

    __unpackargs__ = ('value',)

    def _to_python(self, value, state):
        return self.value

    _from_python = _to_python

############################################################
## Normal validators
############################################################

class MaxLength(FancyValidator):

    """
    Invalid if the value is longer than `maxLength`.  Uses len(),
    so it can work for strings, lists, or anything with length.

    Examples::

        >>> max5 = MaxLength(5)
        >>> max5.to_python('12345')
        '12345'
        >>> max5.from_python('12345')
        '12345'
        >>> max5.to_python('123456')
        Traceback (most recent call last):
          ...
        Invalid: Enter a value less than 5 characters long
        >>> max5(accept_python=False).from_python('123456')
        Traceback (most recent call last):
          ...
        Invalid: Enter a value less than 5 characters long
        >>> max5.to_python([1, 2, 3])
        [1, 2, 3]
        >>> max5.to_python([1, 2, 3, 4, 5, 6])
        Traceback (most recent call last):
          ...
        Invalid: Enter a value less than 5 characters long
        >>> max5.to_python(5)
        Traceback (most recent call last):
          ...
        Invalid: Invalid value (value with length expected)
    """

    __unpackargs__ = ('maxLength',)
    messages = {
        'tooLong': "Enter a value less than %(maxLength)i characters long",
        'invalid': "Invalid value (value with length expected)",
        }

    def validate_python(self, value, state):
        try:
            if value and \
               len(value) > self.maxLength:
                raise Invalid(self.message('tooLong', state,
                                           maxLength=self.maxLength),
                              value, state)
            else:
                return None
        except TypeError:
            raise Invalid(self.message('invalid', state),
                          value, state)

class MinLength(FancyValidator):

    """
    Invalid if the value is shorter than `minlength`.  Uses len(),
    so it can work for strings, lists, or anything with length.

    Examples::

        >>> min5 = MinLength(5)
        >>> min5.to_python('12345')
        '12345'
        >>> min5.from_python('12345')
        '12345'
        >>> min5.to_python('1234')
        Traceback (most recent call last):
          ...
        Invalid: Enter a value more than 5 characters long
        >>> min5(accept_python=False).from_python('1234')
        Traceback (most recent call last):
          ...
        Invalid: Enter a value more than 5 characters long
        >>> min5.to_python([1, 2, 3, 4, 5])
        [1, 2, 3, 4, 5]
        >>> min5.to_python([1, 2, 3])
        Traceback (most recent call last):
          ...
        Invalid: Enter a value more than 5 characters long
        >>> min5.to_python(5)
        Traceback (most recent call last):
          ...
        Invalid: Invalid value (value with length expected)
        
    """

    __unpackargs__ = ('minLength',)

    messages = {
        'tooShort': "Enter a value at least %(minLength)i characters long",
        'invalid': "Invalid value (value with length expected)",
        }

    def validate_python(self, value, state):
        try:
            if len(value) < self.minLength:
                raise Invalid(self.message('tooShort', state,
                                           minLength=self.minLength),
                              value, state)
        except TypeError:
            raise Invalid(self.message('invalid', state),
                          value, state)

class NotEmpty(FancyValidator):

    """
    Invalid if value is empty (empty string, empty list, etc).

    Generally for objects that Python considers false, except zero
    which is not considered invalid.

    Examples::

        >>> ne = NotEmpty(messages={'empty': 'enter something'})
        >>> ne.to_python('')
        Traceback (most recent call last):
          ...
        Invalid: enter something
        >>> ne.to_python(0)
        0
    """
    not_empty = True

    messages = {
        'empty': "Please enter a value",
        }

    def validate_python(self, value, state):
        if value == 0:
            # This isn't "empty" for this definition.
            return value
        if not value:
            raise Invalid(self.message('empty', state),
                          value, state)

class Empty(FancyValidator):

    """
    Invalid unless the value is empty.  Use cleverly, if at all.

    Examples::

        >>> Empty.to_python(0)
        Traceback (most recent call last):
          ...
        Invalid: You cannot enter a value here
    """

    messages = {
        'notEmpty': "You cannot enter a value here",
        }

    def validate_python(self, value, state):
        if value or value == 0:
            raise Invalid(self.message('notEmpty', state),
                          value, state)

class Regex(FancyValidator):

    """
    Invalid if the value doesn't match the regular expression `regex`.

    The regular expression can be a compiled re object, or a string
    which will be compiled for you.

    Use strip=True if you want to strip the value before validation,
    and as a form of conversion (often useful).

    Examples::

        >>> cap = Regex(r'^[A-Z]+$')
        >>> cap.to_python('ABC')
        'ABC'

    Note that ``.from_python()`` calls (in general) do not validate
    the input::
    
        >>> cap.from_python('abc')
        'abc'
        >>> cap(accept_python=False).from_python('abc')
        Traceback (most recent call last):
          ...
        Invalid: The input is not valid
        >>> cap.to_python(1)
        Traceback (most recent call last):
          ...
        Invalid: The input must be a string (not a <type 'int'>: 1)
        >>> Regex(r'^[A-Z]+$', strip=True).to_python('  ABC  ')
        'ABC'
        >>> Regex(r'this', regexOps=('I',)).to_python('THIS')
        'THIS'
    """

    regexOps = ()
    strip = False
    regex = None

    __unpackargs__ = ('regex',)

    messages = {
        'invalid': "The input is not valid",
        }
    
    def __init__(self, *args, **kw):
        FancyValidator.__init__(self, *args, **kw)
        if isinstance(self.regex, str):
            ops = 0
            assert not isinstance(self.regexOps, str), (
                "regexOps should be a list of options from the re module "
                "(names, or actual values)")
            for op in self.regexOps:
                if isinstance(op, str):
                    ops |= getattr(re, op)
                else:
                    ops |= op
            self.regex = re.compile(self.regex, ops)

    def validate_python(self, value, state):
        self.assert_string(value, state)
        if self.strip and (isinstance(value, str) or isinstance(value, unicode)):
            value = value.strip()
        if not self.regex.search(value):
            raise Invalid(self.message('invalid', state),
                          value, state)

    def _to_python(self, value, state):
        if self.strip and \
               (isinstance(value, str) or isinstance(value, unicode)):
            return value.strip()
        return value

class PlainText(Regex):

    """
    Test that the field contains only letters, numbers, underscore,
    and the hyphen.  Subclasses Regex.

    Examples::

        >>> PlainText.to_python('_this9_')
        '_this9_'
        >>> PlainText.from_python('  this  ')
        '  this  '
        >>> PlainText(accept_python=False).from_python('  this  ')
        Traceback (most recent call last):
          ...
        Invalid: Enter only letters, numbers, or _ (underscore)
        >>> PlainText(strip=True).to_python('  this  ')
        'this'
        >>> PlainText(strip=True).from_python('  this  ')
        'this'
    """

    regex = r"^[a-zA-Z_\-0-9]*$"

    messages = {
        'invalid': 'Enter only letters, numbers, or _ (underscore)',
        }

class OneOf(FancyValidator):

    """
    Tests that the value is one of the members of a given list.

    If ``testValueLists=True``, then if the input value is a list or
    tuple, all the members of the sequence will be checked (i.e., the
    input must be a subset of the allowed values).

    Use ``hideList=True`` to keep the list of valid values out of the
    error message in exceptions.

    Examples::

        >>> oneof = OneOf([1, 2, 3])
        >>> oneof.to_python(1)
        1
        >>> oneof.to_python(4)
        Traceback (most recent call last):
          ...
        Invalid: Value must be one of: 1; 2; 3 (not 4)
        >>> oneof(testValueList=True).to_python([2, 3, [1, 2, 3]])
        [2, 3, [1, 2, 3]]
        >>> oneof.to_python([2, 3, [1, 2, 3]])
        Traceback (most recent call last):
          ...
        Invalid: Value must be one of: 1; 2; 3 (not [2, 3, [1, 2, 3]])
    """

    list = None
    testValueList = False
    hideList = False

    __unpackargs__ = ('list',)

    messages = {
        'invalid': "Invalid value",
        'notIn': "Value must be one of: %(items)s (not %(value)r)",
        }
    
    def validate_python(self, value, state):
        if self.testValueList and isinstance(value, (list, tuple)):
            for v in value:
                self.validate_python(v, state)
        else:
            if not value in self.list:
                if self.hideList:
                    raise Invalid(self.message('invalid', state),
                                  value, state)
                else:
                    items = '; '.join(map(str, self.list))
                    raise Invalid(self.message('notIn', state,
                                               items=items,
                                               value=value),
                                  value, state)

class DictConverter(FancyValidator):

    """
    Converts values based on a dictionary which has values as keys for
    the resultant values.

    If ``allowNull`` is passed, it will not balk if a false value
    (e.g., '' or None) is given (it will return None in these cases).

    to_python takes keys and gives values, from_python takes values and
    gives keys.

    If you give hideDict=True, then the contents of the dictionary
    will not show up in error messages.

    Examples::

        >>> dc = DictConverter({1: 'one', 2: 'two'})
        >>> dc.to_python(1)
        'one'
        >>> dc.from_python('one')
        1
        >>> dc.to_python(3)
        Traceback (most recent call last):
        Invalid: Enter a value from: 1; 2
        >>> dc2 = dc(hideDict=True)
        >>> dc2.hideDict
        True
        >>> dc2.dict
        {1: 'one', 2: 'two'}
        >>> dc2.to_python(3)
        Traceback (most recent call last):
        Invalid: Choose something
        >>> dc.from_python('three')
        Traceback (most recent call last):
        Invalid: Nothing in my dictionary goes by the value 'three'.  Choose one of: 'one'; 'two'
    """

    dict = None
    hideDict = False

    __unpackargs__ = ('dict',)

    messages = {
        'keyNotFound': "Choose something",
        'chooseKey': "Enter a value from: %(items)s",
        'valueNotFound': "That value is not known",
        'chooseValue': "Nothing in my dictionary goes by the value %(value)s.  Choose one of: %(items)s",
        }
    
    def _to_python(self, value, state):
        try:
            return self.dict[value]
        except KeyError:
            if self.hideDict:
                raise Invalid(self.message('keyNotFound', state),
                              value, state)
            else:
                items = '; '.join(map(repr, self.dict.keys()))
                raise Invalid(self.message('chooseKey', state,
                                           items=items),
                              value, state)

    def _from_python(self, value, state):
        for k, v in self.dict.items():
            if value == v:
                return k
        if self.hideDict:
            raise Invalid(self.message('valueNotFound', state),
                          value, state)
        else:
            items = '; '.join(map(repr, self.dict.values()))
            raise Invalid(self.message('chooseValue', state,
                                       value=repr(value),
                                       items=items),
                          value, state)

class IndexListConverter(FancyValidator):

    """
    Converts a index (which may be a string like '2') to the value in
    the given list.

    Examples::

        >>> index = IndexListConverter(['zero', 'one', 'two'])
        >>> index.to_python(0)
        'zero'
        >>> index.from_python('zero')
        0
        >>> index.to_python('1')
        'one'
        >>> index.to_python(5)
        Traceback (most recent call last):
        Invalid: Index out of range
        >>> index(not_empty=True).to_python(None)
        Traceback (most recent call last):
        Invalid: Please enter a value
        >>> index.from_python('five')
        Traceback (most recent call last):
        Invalid: Item 'five' was not found in the list
    """

    list = None

    __unpackargs__ = ('list',)

    messages = {
        'integer': "Must be an integer index",
        'outOfRange': "Index out of range",
        'notFound': "Item %(value)s was not found in the list",
        }
    
    def _to_python(self, value, state):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise Invalid(self.message('integer', state),
                          value, state)
        try:
            return self.list[value]
        except IndexError:
            raise Invalid(self.message('outOfRange', state),
                          value, state)

    def _from_python(self, value, state):
        for i in range(len(self.list)):
            if self.list[i] == value:
                return i
        raise Invalid(self.message('notFound', state,
                                   value=repr(value)),
                      value, state)        

class DateValidator(FancyValidator):

    """
    Validates that a date is within the given range.  Be sure to call
    DateConverter first if you aren't expecting mxDateTime input.

    ``earliest_date`` and ``latest_date`` may be functions; if so,
    they will be called each time before validating.

    ``after_now`` means a time after the current timestamp; note that
    just a few milliseconds before now is invalid!  ``today_or_after``
    is more permissive, and ignores hours and minutes.

    Examples::

        >>> from datetime import datetime, timedelta
        >>> d = DateValidator(earliest_date=datetime(2003, 1, 1))
        >>> d.to_python(datetime(2004, 1, 1))
        datetime.datetime(2004, 1, 1, 0, 0)
        >>> d.to_python(datetime(2002, 1, 1))
        Traceback (most recent call last):
            ...
        Invalid: Date must be after Wednesday, 01 January 2003
        >>> d.to_python(datetime(2003, 1, 1))
        datetime.datetime(2003, 1, 1, 0, 0)
        >>> d = DateValidator(after_now=True)
        >>> now = datetime.now()
        >>> d.to_python(now+timedelta(seconds=5)) == now+timedelta(seconds=5)
        True
        >>> d.to_python(now-timedelta(days=1))
        Traceback (most recent call last):
            ...
        Invalid: The date must be sometime in the future
        >>> d.to_python(now+timedelta(days=1)) > now
        True
        >>> d = DateValidator(today_or_after=True)
        >>> d.to_python(now) == now
        True
    
    """

    earliest_date = None
    latest_date = None
    after_now = False
    # Like after_now, but just after this morning:
    today_or_after = False
    # Use 'datetime' to force the Python 2.3+ datetime module, or
    # 'mxDateTime' to force the mxDateTime module (None means use
    # datetime, or if not present mxDateTime)
    datetime_module = None

    messages = {
        'after': "Date must be after %(date)s",
        'before': "Date must be before %(date)s",
        # Double %'s, because this will be substituted twice:
        'date_format': "%%A, %%d %%B %%Y",
        'future': "The date must be sometime in the future",
        }

    def validate_python(self, value, state):
        if self.earliest_date:
            if callable(self.earliest_date):
                earliest_date = self.earliest_date()
            else:
                earliest_date = self.earliest_date
            if value < earliest_date:
                date_formatted = earliest_date.strftime(
                    self.message('date_format', state))
                raise Invalid(
                    self.message('after', state,
                                 date=date_formatted),
                    value, state)
        if self.latest_date:
            if callable(self.latest_date):
                latest_date = self.latest_date()
            else:
                latest_date = self.latest_date
            if value > latest_date:
                date_formatted = latest_date.strftime(
                    self.message('date_format', state))
                raise Invalid(
                    self.message('before', state,
                                 date=date_formatted),
                    value, state)
        if self.after_now:
            dt_mod = import_datetime(self.datetime_module)
            now = datetime_now(dt_mod)
            if value < now:
                date_formatted = now.strftime(
                    self.message('date_format', state))
                raise Invalid(
                    self.message('future', state,
                                 date=date_formatted),
                    value, state)
        if self.today_or_after:
            dt_mod = import_datetime(self.datetime_module)
            now = datetime_now(dt_mod)
            today = datetime_makedate(dt_mod,
                                      now.year, now.month, now.day)
            value_as_date = datetime_makedate(
                dt_mod, value.year, value.month, value.day)
            if value_as_date < today:
                date_formatted = now.strftime(
                    self.message('date_format', state))
                raise Invalid(
                    self.message('future', state,
                                 date=date_formatted),
                    value, state)
            

class Bool(FancyValidator):

    """
    Always Valid, returns True or False based on the value and the
    existance of the value.

    If you want to convert strings like ``'true'`` to booleans, then
    use ``StringBoolean``.

    Examples::

        >>> Bool.to_python(0)
        False
        >>> Bool.to_python(1)
        True
        >>> Bool.to_python('')
        False
        >>> Bool.to_python(None)
        False
    """

    if_missing = False

    def _to_python(self, value, state):
        return bool(value)
    _from_python = _to_python        

    def empty_value(self, value):
        return False

class Int(FancyValidator):

    """
    Convert a value to an integer.

    Example::

        >>> Int.to_python('10')
        10
        >>> Int.to_python('ten')
        Traceback (most recent call last):
            ...
        Invalid: Please enter an integer value
    """

    messages = {
        'integer': "Please enter an integer value",
        }

    def _to_python(self, value, state):
        try:
            return int(value)
        except (ValueError, TypeError):
            raise Invalid(self.message('integer', state),
                          value, state)

    _from_python = _to_python

class Number(FancyValidator):

    """
    Convert a value to a float or integer.  Tries to convert it to
    an integer if no information is lost.

    ::

        >>> Number.to_python('10')
        10
        >>> Number.to_python('10.5')
        10.5
        >>> Number.to_python('ten')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a number

    """
    
    messages = {
        'number': "Please enter a number",
        }
    
    def _to_python(self, value, state):
        try:
            value = float(value)
            if value == int(value):
                return int(value)
            return value
        except ValueError:
            raise Invalid(self.message('number', state),
                          value, state)

class String(FancyValidator):
    """
    Converts things to string, but treats empty things as the empty
    string.

    Also takes a `max` and `min` argument, and the string length must
    fall in that range.

    ::

        >>> String(min=2).to_python('a')
        Traceback (most recent call last):
            ...
        Invalid: Enter a value 2 characters long or more
        >>> String(max=10).to_python('xxxxxxxxxxx')
        Traceback (most recent call last):
            ...
        Invalid: Enter a value less than 10 characters long
        >>> String().from_python(None)
        ''
        >>> String().from_python([])
        ''
    """

    min = None
    max = None

    messages = {
        'tooLong': "Enter a value less than %(max)i characters long",
        'tooShort': "Enter a value %(min)i characters long or more",
        }
    
    def validate_python(self, value, state):
        if (self.max is not None and value is not None
            and len(value) > self.max):
            raise Invalid(self.message('tooLong', state,
                                       max=self.max),
                          value, state)
        if (self.min is not None
            and (not value or len(value) < self.min)):
            raise Invalid(self.message('tooShort', state,
                                       min=self.min),
                          value, state)

    def _from_python(self, value, state):
        if value:
            return str(value)
        if value == 0:
            return str(value)
        return ""

    def empty_value(self, value):
        return ''

class UnicodeString(String):
    """
    Converts things to unicode string, this is a specialization of
    the String class.
    
    In addition to the String arguments, an encoding argument is also
    accepted. By default the encoding will be utf-8.
    
    All converted strings are returned as Unicode strings.
    
    ::
    
        >>> UnicodeString().from_python(None)
        u''
        >>> UnicodeString().from_python([])
        u''
        >>> UnicodeString(encoding='utf-7').from_python('Ni Ni Ni')
        u'Ni Ni Ni'
    """
    
    encoding = 'utf-8'
    
    def _from_python(self, value, state):
        if value:
            if isinstance(value, unicode):
                return value
            if hasattr(value, '__unicode__'):
                return unicode(value)
            return unicode(value, self.encoding)
        if value == 0:
            return unicode(value, self.encoding)
        return unicode("", self.encoding)
    
    def _from_python(self, value, state):
        if hasattr(value, '__unicode__'):
            value = unicode(value)
        if isinstance(value, unicode):
            return value.encode(self.encoding)
        return str(value)

    def empty_value(self, value):
        return unicode("", self.encoding)

class Set(FancyValidator):

    """
    This is for when you think you may return multiple values for a
    certain field.

    This way the result will always be a list, even if there's only
    one result.  It's equivalent to ForEach(convertToList=True).

    If you give ``use_set=True``, then it will return an actual
    ``sets.Set`` object.

    ::

       >>> Set.to_python(None)
       []
       >>> Set.to_python('this')
       ['this']
       >>> Set.to_python(('this', 'that'))
       ['this', 'that']
       >>> s = Set(use_set=True)
       >>> s.to_python(None)
       Set([])
       >>> s.to_python('this')
       Set(['this'])
       >>> s.to_python(('this',))
       Set(['this'])
    """

    use_set = False

    def _to_python(self, value, state):
        if self.use_set:
            if isinstance(value, sets.Set):
                return value
            elif isinstance(value, (list, tuple)):
                return sets.Set(value)
            elif value is None:
                return sets.Set()
            else:
                return sets.Set([value])
        else:
            if isinstance(value, list):
                return value
            elif sets and isinstance(value, sets.Set):
                return list(value)
            elif isinstance(value, tuple):
                return list(value)
            elif value is None:
                return []
            else:
                return [value]

    def empty_value(self, value):
        if self.use_set:
            return sets.Set([])
        else:
            return []

class Email(FancyValidator):
    r"""
    Validate an email address.

    If you pass ``resolve_domain=True``, then it will try to resolve
    the domain name to make sure it's valid.  This takes longer, of
    course.  You must have the `pyDNS <http://pydns.sf.net>`_ modules
    installed to look up MX records.

    ::

        >>> e = Email()
        >>> e.to_python(' test@foo.com ')
        'test@foo.com'
        >>> e.to_python('test')
        Traceback (most recent call last):
            ...
        Invalid: An email address must contain a single @
        >>> e.to_python('test@foobar.com.5')
        Traceback (most recent call last):
            ...
        Invalid: The domain portion of the email address is invalid (the portion after the @: foobar.com.5)
        >>> e.to_python('o*reilly@test.com')
        'o*reilly@test.com'
        >>> e = Email(resolve_domain=True)
        >>> e.resolve_domain
        True
        >>> e.to_python('doesnotexist@colorstudy.com')
        'doesnotexist@colorstudy.com'
        >>> e.to_python('test@thisdomaindoesnotexistithinkforsure.com')
        Traceback (most recent call last):
            ...
        Invalid: The domain of the email address does not exist (the portion after the @: thisdomaindoesnotexistithinkforsure.com)
        
    """ 

    resolve_domain = False

    usernameRE = re.compile(r"^[^ \t\n\r@<>()]+$", re.I)
    domainRE = re.compile(r"^[a-z0-9][a-z0-9\.\-_]*\.[a-z]+$", re.I)

    messages = {
        'empty': 'Please enter an email address',
        'noAt': 'An email address must contain a single @',
        'badUsername': 'The username portion of the email address is invalid (the portion before the @: %(username)s)',
        'badDomain': 'The domain portion of the email address is invalid (the portion after the @: %(domain)s)',
        'domainDoesNotExist': 'The domain of the email address does not exist (the portion after the @: %(domain)s)',
        }
    
    def __init__(self, *args, **kw):
        global mxlookup
        FancyValidator.__init__(self, *args, **kw)
        if self.resolve_domain:
            if mxlookup is None:
                try:
                    import DNS.Base
                    DNS.Base.ParseResolvConf()
                    from DNS.lazy import mxlookup
                except ImportError:
                    import warnings
                    warnings.warn(
                        "pyDNS <http://pydns.sf.net> is not installed on "
                        "your system (or the DNS package cannot be found).  "
                        "I cannot resolve domain names in addresses")
                    raise

    def validate_python(self, value, state):
        if not value:
            raise Invalid(
                self.message('empty', state),
                value, state)
        value = value.strip()
        splitted = value.split('@', 1)
        if not len(splitted) == 2:
            raise Invalid(
                self.message('noAt', state),
                value, state)
        if not self.usernameRE.search(splitted[0]):
            raise Invalid(
                self.message('badUsername', state,
                             username=splitted[0]),
                value, state)
        if not self.domainRE.search(splitted[1]):
            raise Invalid(
                self.message('badDomain', state,
                             domain=splitted[1]),
                value, state)
        if self.resolve_domain:
            domains = mxlookup(splitted[1])
            if not domains:
                raise Invalid(
                    self.message('domainDoesNotExist', state,
                                 domain=splitted[1]),
                    value, state)

    def _to_python(self, value, state):
        return value.strip()

class URL(FancyValidator):

    """
    Validate a URL, either http://... or https://.  If check_exists
    is true, then we'll actually make a request for the page.

    If add_http is true, then if no scheme is present we'll add
    http://

    ::

        >>> u = URL(add_http=True)
        >>> u.to_python('foo.com')
        'http://foo.com'
        >>> u.to_python('http://hahaha/bar.html')
        Traceback (most recent call last):
            ...
        Invalid: That is not a valid URL
        >>> u.to_python('https://test.com')
        'https://test.com'
        >>> u = URL(add_http=False, check_exists=True)
        >>> u.to_python('http://google.com')
        'http://google.com'
        >>> u.to_python('http://colorstudy.com/doesnotexist.html')
        Traceback (most recent call last):
            ...
        Invalid: The server responded that the page could not be found
        >>> u.to_python('http://this.domain.does.not.exists.formencode.org/test.html')
        Traceback (most recent call last):
            ...
        Invalid: An error occured when trying to connect to the server: (7, 'No address associated with ...')
        
    """

    check_exists = False
    add_http = True

    url_re = re.compile(r'^(http|https)://'
                        r'[a-z0-9][a-z0-9\-\._]*\.[a-z]+'
                        r'(?:[0-9]+)?'
                        r'(?:/.*)?$', re.I) 
    scheme_re = re.compile(r'^[a-zA-Z]+:')

    messages = {
        'noScheme': 'You must start your URL with http://, https://, etc',
        'badURL': 'That is not a valid URL',
        'httpError': 'An error occurred when trying to access the URL: %(error)s',
        'socketError': 'An error occured when trying to connect to the server: %(error)s',
        'notFound': 'The server responded that the page could not be found',
        'status': 'The server responded with a bad status code (%(status)s)',
        }

    def _to_python(self, value, state):
        value = value.strip()
        if self.add_http:
            if not self.scheme_re.search(value):
                value = 'http://' + value
        match = self.scheme_re.search(value)
        if not match:
            raise Invalid(
                self.message('noScheme', state),
                value, state)
        value = match.group(0).lower() + value[len(match.group(0)):]
        if not self.url_re.search(value):
            raise Invalid(
                self.message('badURL', state),
                value, state)
        if self.check_exists and (value.startswith('http://')
                                  or value.startswith('https://')):
            self._check_url_exists(value, state)
        return value

    def _check_url_exists(self, url, state):
        global httplib, urlparse, socket
        if httplib is None:
            import httplib
        if urlparse is None:
            import urlparse
        if socket is None:
            import socket
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(
            url, 'http')
        if scheme == 'http':
            ConnClass = httplib.HTTPConnection
        else:
            ConnClass = httplib.HTTPSConnection
        try:
            conn = ConnClass(netloc)
            if params:
                path += ';' + params
            if query:
                path += '?' + query
            conn.request('HEAD', path)
            res = conn.getresponse()
        except httplib.HTTPException, e:
            raise Invalid(
                self.message('httpError', state, error=e),
                state, url)
        except socket.error, e:
            raise Invalid(
                self.message('socketError', state, error=e),
                state, url)
        else:
            if res.status == 404:
                raise Invalid(
                    self.message('notFound', state),
                    state, url)
            if (res.status < 200
                or res.status >= 500):
                raise Invalid(
                    self.message('status', state, status=res.status),
                    state, url)
        
        

class StateProvince(FancyValidator):
    
    """
    Valid state or province code (two-letter).

    Well, for now I don't know the province codes, but it does state
    codes.  Give your own `states` list to validate other state-like
    codes; give `extra_states` to add values without losing the
    current state values.

    ::

        >>> s = StateProvince('XX')
        >>> s.to_python('IL')
        'IL'
        >>> s.to_python('XX')
        'XX'
        >>> s.to_python('xx')
        'XX'
        >>> s.to_python('YY')
        Traceback (most recent call last):
            ...
        Invalid: That is not a valid state code
    """

    states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE',
              'FL', 'GA', 'HI', 'IA', 'ID', 'IN', 'IL', 'KS', 'KY',
              'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT',
              'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH',
              'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
              'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

    extra_states = []

    __unpackargs__ = ('extra_states',)

    messages = {
        'empty': 'Please enter a state code',
        'wrongLength': 'Please enter a state code with TWO letters',
        'invalid': 'That is not a valid state code',
        }

    def validate_python(self, value, state):
        value = str(value).strip().upper()
        if not value:
            raise Invalid(
                self.message('empty', state),
                value, state)
        if not value or len(value) != 2:
            raise Invalid(
                self.message('wrongLength', state),
                value, state)
        if value not in self.states \
           and not (self.extra_states and value in self.extra_states):
            raise Invalid(
                self.message('invalid', state),
                value, state)
    
    def _to_python(self, value, state):
        return str(value).strip().upper()

class PhoneNumber(FancyValidator):

    """
    Validates, and converts to ###-###-####, optionally with
    extension (as ext.##...)
    
    @@: should add international phone number support

    ::

        >>> p = PhoneNumber()
        >>> p.to_python('333-3333')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a number, with area code, in the form ###-###-####, optionally with "ext.####"
        >>> p.to_python('555-555-5555')
        '555-555-5555'
        >>> p.to_python('1-393-555-3939')
        '1-393-555-3939'
        >>> p.to_python('321.555.4949')
        '321.555.4949'
        >>> p.to_python('3335550000')
        '3335550000'
    """
    # for emacs: "

    _phoneRE = re.compile(r'^\s*(?:1-)?(\d\d\d)[\- \.]?(\d\d\d)[\- \.]?(\d\d\d\d)(?:\s*ext\.?\s*(\d+))?\s*$', re.I)

    messages = {
        'phoneFormat': 'Please enter a number, with area code, in the form ###-###-####, optionally with "ext.####"',
        }
        
    def _to_python(self, value, state):
        self.assert_string(value, state)
        match = self._phoneRE.search(value)
        if not match:
            raise Invalid(
                self.message('phoneFormat', state),
                value, state)
        return value

    def _from_python(self, value, state):
        self.assert_string(value, state)
        match = self._phoneRE.search(value)
        if not match:
            raise Invalid(self.message('phoneFormat', state),
                          value, state)
        result = '%s-%s-%s' % (match.group(1), match.group(2), match.group(3))
        if match.group(4):
            result = result + " ext.%s" % match.group(4)
        return result

class FieldStorageUploadConverter(FancyValidator):

    """
    Converts a cgi.FieldStorage instance to
    a value that FormEncode can use for file
    uploads.
    """
    def _to_python(self, value, state):
        if isinstance(value, cgi.FieldStorage):
            return fieldstorage.convert_fieldstorage(value)
        else:
            return value

class FileUploadKeeper(FancyValidator):
    """
    Takes two inputs (a dictionary with keys ``static`` and
    ``upload``) and converts them into one value on the Python side (a
    dictionary with ``filename`` and ``content`` keys).  The upload
    takes priority over the static value.  The filename may be None if
    it can't be discovered.

    Handles uploads of both text and ``cgi.FieldStorage`` upload
    values.

    This is basically for use when you have an upload field, and you
    want to keep the upload around even if the rest of the form
    submission fails.  When converting *back* to the form submission,
    there may be extra values ``'original_filename'`` and
    ``'original_content'``, which may want to use in your form to show
    the user you still have their content around.
    """

    upload_key = 'upload'
    static_key = 'static'

    def _to_python(self, value, state):
        upload = value.get(self.upload_key)
        static = value.get(self.static_key, '').strip()
        filename = content = None
        if isinstance(upload, cgi.FieldStorage):
            filename = upload.filename
            content = upload.value
        elif isinstance(upload, str) and upload:
            filename = None
            content = upload
        if not content and static:
            filename, content = static.split(None, 1)
            if filename == '-':
                filename = ''
            else:
                filename = filename.decode('base64')
            content = content.decode('base64')
        return {'filename': filename, 'content': content}

    def _from_python(self, value, state):
        filename = value.get('filename', '')
        content = value.get('content', '')
        if filename or content:
            result = self.pack_content(filename, content)
            return {self.upload_key: '',
                    self.static_key: result,
                    'original_filename': filename,
                    'original_content': content}
        else:
            return {self.upload_key: '',
                    self.static_key: ''}

    def pack_content(self, filename, content):
        enc_filename = self.base64encode(filename) or '-'
        enc_content = (content or '').encode('base64')
        result = '%s %s' % (enc_filename, enc_content)
        return result

class DateConverter(FancyValidator):

    """
    Validates and converts a textual date, like mm/yy, dd/mm/yy,
    dd-mm-yy, etc, always assumes month comes second value is the
    month.

    Accepts English month names, also abbreviated.  Returns value as
    mx.DateTime object.  Two year dates are assumed to be within
    1950-2020, with dates from 21-49 being ambiguous and signaling an
    error.

    Use accept_day=False if you just want a month/year (like for a
    credit card expiration date).

    ::

        >>> d = DateConverter()
        >>> d.to_python('12/3/09')
        datetime.date(2009, 12, 3)
        >>> d.to_python('12/3/2009')
        datetime.date(2009, 12, 3)
        >>> d.to_python('2/30/04')
        Traceback (most recent call last):
            ...
        Invalid: That month only has 29 days
        >>> d.to_python('13/2/05')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a month from 1 to 12
    """
    ## @@: accepts only US-style dates

    accept_day = True
    # also allowed: 'dd/mm/yyyy'
    month_style = 'mm/dd/yyyy'
    # Use 'datetime' to force the Python 2.3+ datetime module, or
    # 'mxDateTime' to force the mxDateTime module (None means use
    # datetime, or if not present mxDateTime)
    datetime_module = None

    _day_date_re = re.compile(r'^\s*(\d\d?)[\-\./\\](\d\d?|jan|january|feb|febuary|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)[\-\./\\](\d\d\d?\d?)\s*$', re.I)
    _month_date_re = re.compile(r'^\s*(\d\d?|jan|january|feb|febuary|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)[\-\./\\](\d\d\d?\d?)\s*$', re.I)

    _month_names = {
        'jan': 1, 'january': 1,
        'feb': 2, 'febuary': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12,
        }

    ## @@: Feb. should be leap-year aware (but mxDateTime does catch that)
    _monthDays = {
        1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31,
        9: 30, 10: 31, 11: 30, 12: 31}

    messages = {
        'badFormat': 'Please enter the date in the form %(format)s',
        'monthRange': 'Please enter a month from 1 to 12',
        'invalidDay': 'Please enter a valid day',
        'dayRange': 'That month only has %(days)i days',
        'invalidDate': 'That is not a valid day (%(exception)s)',
        'unknownMonthName': "Unknown month name: %(month)s",
        'invalidYear': 'Please enter a number for the year',
        'fourDigitYear': 'Please enter a four-digit year',
        'wrongFormat': 'Please enter the date in the form %(format)s',
        }

    def _to_python(self, value, state):
        if self.accept_day:
            return self.convert_day(value, state)
        else:
            return self.convert_month(value, state)

    def convert_day(self, value, state):
        self.assert_string(value, state)
        match = self._day_date_re.search(value)
        if not match:
            raise Invalid(self.message('badFormat', state,
                                       format=self.month_style),
                          value, state)
        day = int(match.group(1))
        try:
            month = int(match.group(2))
        except TypeError:
            month = self.make_month(match.group(2), state)
        else:
            if self.month_style == 'mm/dd/yyyy':
                month, day = day, month
        year = self.make_year(match.group(3), state)
        if month > 12 or month < 1:
            raise Invalid(self.message('monthRange', state),
                          value, state)
        if day < 1:
            raise Invalid(self.message('invalidDay', state),
                          value, state)
        if self._monthDays[month] < day:
            raise Invalid(self.message('dayRange', state,
                                       days=self._monthDays[month]),
                          value, state)
        dt_mod = import_datetime(self.datetime_module)
        try:
            return datetime_makedate(dt_mod, year, month, day)
        except ValueError, v:
            raise Invalid(self.message('invalidDate', state,
                                       exception=str(v)),
                          value, state)
        
    def make_month(self, value, state):
        try:
            return int(value)
        except ValueError:
            value = value.lower().strip()
            if self._month_names.has_key(value):
                return self._month_names[value]
            else:
                raise Invalid(self.message('unknownMonthName', state,
                                           month=value),
                              value, state)

    def make_year(self, year, state):
        try:
            year = int(year)
        except ValueError:
            raise Invalid(self.message('invalidYear', state),
                          year, state)
        if year <= 20:
            year = year + 2000
        if year >= 50 and year < 100:
            year = year + 1900
        if year > 20 and year < 50:
            raise Invalid(self.message('fourDigitYear', state),
                          year, state)
        return year

    def convert_month(self, value, state):
        match = self._month_date_re.search(value)
        if not match:
            raise Invalid(self.message('wrongFormat', state,
                                       format='mm/yyyy'),
                          value, state)
        month = self.make_month(match.group(1), state)
        year = self.make_year(match.group(2), state)
        if month > 12 or month < 1:
            raise Invalid(self.message('monthRange', state),
                          value, state)
        dt_mod = import_datetime(self.datetime_module)
        return datetime_makedate(dt_mod, year, month, 1)

    def _from_python(self, value, state):
        if self.if_empty is not NoDefault and not value:
            return ''
        if self.accept_day:
            return self.unconvert_day(value, state)
        else:
            return self.unconvert_month(value, state)

    def unconvert_day(self, value, state):
        # @@ ib: double-check, improve
        return value.strftime("%m/%d/%Y")
        
    def unconvert_month(self, value, state):
        # @@ ib: double-check, improve
        return value.strftime("%m/%Y")

class TimeConverter(FancyValidator):

    """
    Converts times in the format HH:MM:SSampm to (h, m, s).
    Seconds are optional.

    For ampm, set use_ampm = True.  For seconds, use_seconds = True.
    Use 'optional' for either of these to make them optional.

    Examples::

        >>> tim = TimeConverter()
        >>> tim.to_python('8:30')
        (8, 30)
        >>> tim.to_python('20:30')
        (20, 30)
        >>> tim.to_python('30:00')
        Traceback (most recent call last):
            ...
        Invalid: You must enter an hour in the range 0-23
        >>> tim.to_python('13:00pm')
        Traceback (most recent call last):
            ...
        Invalid: You must enter an hour in the range 1-12
        >>> tim.to_python('12:-1')
        Traceback (most recent call last):
            ...
        Invalid: You must enter a minute in the range 0-59
        >>> tim.to_python('12:02pm')
        (12, 2)
        >>> tim.to_python('12:02am')
        (0, 2)
        >>> tim.to_python('1:00PM')
        (13, 0)
        >>> tim.from_python((13, 0))
        '13:00:00'
        >>> tim2 = tim(use_ampm=True, use_seconds=False)
        >>> tim2.from_python((13, 0))
        '1:00pm'
        >>> tim2.from_python((0, 0))
        '12:00am'
        >>> tim2.from_python((12, 0))
        '12:00pm'
    """

    use_ampm = 'optional'
    prefer_ampm = False
    use_seconds = 'optional'

    messages = {
        'noAMPM': 'You must indicate AM or PM',
        'tooManyColon': 'There are two many :\'s',
        'noSeconds': 'You may not enter seconds',
        'secondsRequired': 'You must enter seconds',
        'minutesRequired': 'You must enter minutes (after a :)',
        'badNumber': 'The %(part)s value you gave is not a number: %(number)r',
        'badHour': 'You must enter an hour in the range %(range)s',
        'badMinute': 'You must enter a minute in the range 0-59',
        'badSecond': 'You must enter a second in the range 0-59',
        }

    def _to_python(self, value, state):
        time = value.strip()
        explicit_ampm = False
        if self.use_ampm:
            last_two = time[-2:].lower()
            if last_two not in ('am', 'pm'):
                if self.use_ampm != 'optional':
                    raise Invalid(
                        self.message('noAMPM', state),
                        value, state)
                else:
                    offset = 0
            else:
                explicit_ampm = True
                if last_two == 'pm':
                    offset = 12
                else:
                    offset = 0
                time = time[:-2]
        else:
            offset = 0
        parts = time.split(':')
        if len(parts) > 3:
            raise Invalid(
                self.message('tooManyColon', state),
                value, state)
        if len(parts) == 3 and not self.use_seconds:
            raise Invalid(
                self.message('noSeconds', state),
                value, state)
        if (len(parts) == 2
            and self.use_seconds
            and self.use_seconds != 'optional'):
            raise Invalid(
                self.message('secondsRequired', state),
                value, state)
        if len(parts) == 1:
            raise Invalid(
                self.message('minutesRequired', state),
                value, state)
        try:
            hour = int(parts[0])
        except ValueError:
            raise Invalid(
                self.message('badNumber', state, number=parts[0], part='hour'),
                value, state)
        if explicit_ampm:
            if hour > 12 or hour < 1:
                raise Invalid(
                    self.message('badHour', state, number=hour, range='1-12'),
                    value, state)
            if hour == 12 and offset == 12:
                # 12pm == 12
                pass
            elif hour == 12 and offset == 0:
                # 12am == 0
                hour = 0
            else:
                hour += offset
        else:
            if hour > 23 or hour < 0:
                raise Invalid(
                    self.message('badHour', state,
                                 number=hour, range='0-23'),
                    value, state)
        try:
            minute = int(parts[1])
        except ValueError:
            raise Invalid(
                self.message('badNumber', state,
                             number=parts[1], part='minute'),
                value, state)
        if minute > 59 or minute < 0:
            raise Invalid(
                self.message('badMinute', state, number=minute),
                value, state)
        if len(parts) == 3:
            try:
                second = int(parts[2])
            except ValueError:
                raise Invalid(
                    self.message('badNumber', state,
                                 number=parts[2], part='second'))
            if second > 59 or second < 0:
                raise Invalid(
                    self.message('badSecond', state, number=second),
                    value, state)
        else:
            second = None
        if second is None:
            return (hour, minute)
        else:
            return (hour, minute, second)

    def _from_python(self, value, state):
        if isinstance(value, (str, unicode)):
            return value
        if hasattr(value, 'hour'):
            hour, minute = value.hour, value.minute
        elif len(value) == 3:
            hour, minute, second = value
        elif len(value) == 2:
            hour, minute = value
            second = 0
        ampm = ''
        if ((self.use_ampm == 'optional' and self.prefer_ampm)
            or (self.use_ampm and self.use_ampm != 'optional')):
            ampm = 'am'
            if hour > 12:
                hour -= 12
                ampm = 'pm'
            elif hour == 12:
                ampm = 'pm'
            elif hour == 0:
                hour = 12
        if self.use_seconds:
            return '%i:%02i:%02i%s' % (hour, minute, second, ampm)
        else:
            return '%i:%02i%s' % (hour, minute, ampm)
        

class PostalCode(Regex):

    """
    US Postal codes (aka Zip Codes).

    ::

        >>> PostalCode.to_python('55555')
        '55555'
        >>> PostalCode.to_python('55555-5555')
        '55555-5555'
        >>> PostalCode.to_python('5555')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a zip code (5 digits)
    """

    regex = r'^\d\d\d\d\d(?:-\d\d\d\d)?$'
    strip = True

    messages = {
        'invalid': 'Please enter a zip code (5 digits)',
        }

class StripField(FancyValidator):

    """
    Take a field from a dictionary, removing the key from the
    dictionary.

    ``name`` is the key.  The field value and a new copy of the
    dictionary with that field removed are returned.

    >>> StripField('test').to_python({'a': 1, 'test': 2})
    (2, {'a': 1})
    >>> StripField('test').to_python({})
    Traceback (most recent call last):
        ...
    Invalid: The name 'test' is missing
    
    """

    __unpackargs__ = ('name',)

    messages = {
        'missing': 'The name %(name)s is missing',
        }

    def _to_python(self, valueDict, state):
        v = valueDict.copy()
        try:
            field = v[self.name]
            del v[self.name]
        except KeyError:
            raise Invalid(self.message('missing', state,
                                       name=repr(self.name)),
                          valueDict, state)
        return field, v


class StringBool(FancyValidator):
    # Originally from TurboGears
    """
    Converts a string to a boolean.
    
    Values like 'true' and 'false' are considered True and False,
    respectively; anything in ``true_values`` is true, anything in
    ``false_values`` is false, case-insensitive).  The first item of
    those lists is considered the preferred form.

    ::

        >>> s = StringBoolean()
        >>> s.to_python('yes'), s.to_python('no')
        (True, False)
        >>> s.to_python(1), s.to_python('N')
        (True, False)
        >>> s.to_python('ye')
        Traceback (most recent call last):
            ...
        Invalid: Value should be 'true' or 'false'
    """
    
    true_values = ['true', 't', 'yes', 'y', 'on', '1']
    false_values = ['false', 'f', 'no', 'n', 'off', '0']

    messages = { "string" : "Value should be %(true)r or %(false)r" }
    
    def _to_python(self, value, state):
        if isinstance(value, (str, unicode)):
            value = value.strip().lower()
            if value in self.true_values:
                return True
            if not value or value in self.false_values:
                return False
            raise Invalid(self.message("string", state,
                                       true=self.true_values[0],
                                       false=self.false_values[0]),
                          value, state)
        return bool(value)
    
    def _from_python(self, value, state):
        if value:
            return self.true_values[0]
        else:
            return self.false_values[0]

# Should deprecate:
StringBoolean = StringBool

class SignedString(FancyValidator):

    """
    Encodes a string into a signed string, and base64 encodes both the
    signature string and a random nonce.

    It is up to you to provide a secret, and to keep the secret handy
    and consistent.
    """

    messages = {
        'malformed': 'Value does not contain a signature',
        'badsig': 'Signature is not correct',
        }

    secret = None
    nonce_length = 4

    def _to_python(self, value, state):
        global sha
        if not sha:
            import sha
        assert self.secret is not None, (
            "You must give a secret")
        parts = value.split(None, 1)
        if not parts or len(parts) == 1:
            raise Invalid(self.message('malformed', state),
                          value, state)
        sig, rest = parts
        sig = sig.decode('base64')
        rest = rest.decode('base64')
        nonce = rest[:self.nonce_length]
        rest = rest[self.nonce_length:]
        expected = sha.new(str(self.secret)+nonce+rest).digest()
        if expected != sig:
            raise Invalid(self.message('badsig', state),
                          value, state)
        return rest

    def _from_python(self, value, state):
        global sha
        if not sha:
            import sha
        nonce = self.make_nonce()
        value = str(value)
        digest = sha.new(self.secret+nonce+value).digest()
        return self.encode(digest)+' '+self.encode(nonce+value)

    def encode(self, value):
        return value.encode('base64').strip().replace('\n', '')

    def make_nonce(self):
        global random
        if not random:
            import random
        return ''.join([
            chr(random.randrange(256))
            for i in range(self.nonce_length)])

class FormValidator(FancyValidator):
    """
    A FormValidator is something that can be chained with a
    Schema.  Unlike normal chaining the FormValidator can 
    validate forms that aren't entirely valid.

    The important method is .validate(), of course.  It gets passed a
    dictionary of the (processed) values from the form.  If you have
    .validate_partial_form set to True, then it will get the incomplete
    values as well -- use .has_key() to test if the field was able to
    process any particular field.

    Anyway, .validate() should return a string or a dictionary.  If a
    string, it's an error message that applies to the whole form.  If
    not, then it should be a dictionary of fieldName: errorMessage.
    The special key "form" is the error message for the form as a whole
    (i.e., a string is equivalent to {"form": string}).

    Return None on no errors.
    """

    validate_partial_form = False

    validate_partial_python = None
    validate_partial_other = None

class RequireIfMissing(FormValidator):

    # Field that potentially is required:
    required = None
    # If this field is missing, then it is required:
    missing = None
    # If this field is present, then it is required:
    present = None
    __unpackargs__ = ('required',)

    def _to_python(self, value_dict, state):
        is_required = False
        if self.missing and not value_dict.get(self.missing):
            is_required = True
        if self.present and value_dict.get(self.present):
            is_required = True
        if is_required and not value_dict.get(self.required):
            raise Invalid('You must give a value for %s' % self.required,
                          value, state,
                          error_dict={self.required: Invalid(self.message(
                              'empty', state), value, state)})
        return value_dict

RequireIfPresent = RequireIfMissing

class FieldsMatch(FormValidator):

    """
    Tests that the given fields match, i.e., are identical.  Useful
    for password+confirmation fields.  Pass the list of field names in
    as `field_names`.

    ::

        >>> f = FieldsMatch('pass', 'conf')
        >>> f.to_python({'pass': 'xx', 'conf': 'xx'})
        {'conf': 'xx', 'pass': 'xx'}
        >>> f.to_python({'pass': 'xx', 'conf': 'yy'})
        Traceback (most recent call last):
            ...
        Invalid: conf: Fields do not match
    """

    show_match = False
    field_names = None
    validate_partial_form = True
    __unpackargs__ = ('*', 'field_names')

    messages = {
        'invalid': "Fields do not match (should be %(match)s)",
        'invalidNoMatch': "Fields do not match",
        }
    
    def validate_partial(self, field_dict, state):
        for name in self.field_names:
            if not field_dict.has_key(name):
                return
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        ref = field_dict[self.field_names[0]]
        errors = {}
        for name in self.field_names[1:]:
            if field_dict.get(name, '') != ref:
                if self.show_match:
                    errors[name] = self.message('invalid', state,
                                                match=ref)
                else:
                    errors[name] = self.message('invalidNoMatch', state)
        if errors:
            error_list = errors.items()
            error_list.sort()
            error_message = '<br>\n'.join(
                ['%s: %s' % (name, value) for name, value in error_list])
            raise Invalid(error_message,
                          field_dict, state,
                          error_dict=errors)

class CreditCardValidator(FormValidator):
    """
    Checks that credit card numbers are valid (if not real).

    You pass in the name of the field that has the credit card
    type and the field with the credit card number.  The credit
    card type should be one of "visa", "mastercard", "amex",
    "dinersclub", "discover", "jcb".

    You must check the expiration date yourself (there is no
    relation between CC number/types and expiration dates).

    ::

        >>> cc = CreditCardValidator()
        >>> cc.to_python({'ccType': 'visa', 'ccNumber': '4111111111111111'})
        {'ccNumber': '4111111111111111', 'ccType': 'visa'}
        >>> cc.to_python({'ccType': 'visa', 'ccNumber': '411111111111111'})
        Traceback (most recent call last):
            ...
        Invalid: ccNumber: You did not enter a valid number of digits
        >>> cc.to_python({'ccType': 'visa', 'ccNumber': '411111111111112'})
        Traceback (most recent call last):
            ...
        Invalid: ccNumber: You did not enter a valid number of digits
    """

    validate_partial_form = True

    cc_type_field = 'ccType'
    cc_number_field = 'ccNumber'
    __unpackargs__ = ('cc_type_field', 'cc_number_field')

    messages = {
        'notANumber': "Please enter only the number, no other characters",
        'badLength': "You did not enter a valid number of digits",
        'invalidNumber': "That number is not valid",
        }

    def validate_partial(self, field_dict, state):
        if not field_dict.get(self.cc_type_field, None) \
           or not field_dict.get(self.cc_number_field, None):
            return None
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        errors = self._validateReturn(field_dict, state)
        if errors:
            error_list = errors.items()
            error_list.sort()
            raise Invalid(
                '<br>\n'.join(["%s: %s" % (name, value)
                               for name, value in error_list]),
                field_dict, state, error_dict=errors)
        
    def _validateReturn(self, field_dict, state):
        ccType = field_dict[self.cc_type_field].lower().strip()
        number = field_dict[self.cc_number_field].strip()
        number = number.replace(' ', '')
        number = number.replace('-', '')
        try:
            long(number)
        except ValueError:
            return {self.cc_number_field: self.message('notANumber', state)}

        assert self._cardInfo.has_key(ccType), (
            "I can't validate that type of credit card")
        foundValid = False
        validLength = False
        for prefix, length in self._cardInfo[ccType]:
            if len(number) == length:
                validLength = True
            if (len(number) == length 
                and number.startswith(prefix)):
                foundValid = True
                break
        if not validLength:
            return {self.cc_number_field: self.message('badLength', state)}
        if not foundValid:
            return {self.cc_number_field: self.message('invalidNumber', state)}

        if not self._validateMod10(number):
            return {self.cc_number_field: self.message('invalidNumber', state)}
        return None

    def _validateMod10(self, s):
        """
        This code by Sean Reifschneider, of tummy.com
        """
        double = 0
        sum = 0
        for i in range(len(s) - 1, -1, -1):
            for c in str((double + 1) * int(s[i])):
                sum = sum + int(c)
            double = (double + 1) % 2
        return((sum % 10) == 0)

    _cardInfo = {
        "visa": [('4', 16),
                 ('4', 13)],
        "mastercard": [('51', 16),
                       ('52', 16),
                       ('53', 16),
                       ('54', 16),
                       ('55', 16)],
        "discover": [('6011', 16)],
        "amex": [('34', 15),
                 ('37', 15)],
        "dinersclub": [('300', 14),
                       ('301', 14),
                       ('302', 14),
                       ('303', 14),
                       ('304', 14),
                       ('305', 14),
                       ('36', 14),
                       ('38', 14)],
        "jcb": [('3', 16),
                ('2131', 15),
                ('1800', 15)],
            }

class CreditCardExpires(FormValidator):
    """
    Checks that credit card expiration date is valid relative to 
    the current date.

    You pass in the name of the field that has the credit card
    expiration month and the field with the credit card expiration 
    year.  

    ::

        >>> ed = CreditCardExpires()
        >>> ed.to_python({'ccExpiresMonth': '11', 'ccExpiresYear': '2250'})
        {'ccExpiresYear': '2250', 'ccExpiresMonth': '11'}
        >>> ed.to_python({'ccExpiresMonth': '10', 'ccExpiresYear': '2005'})
        Traceback (most recent call last):
            ...
        Invalid: ccExpiresMonth: Invalid Expiration Date<br>
        ccExpiresYear: Invalid Expiration Date
    """

    validate_partial_form = True

    cc_expires_month_field = 'ccExpiresMonth'
    cc_expires_year_field = 'ccExpiresYear'
    __unpackargs__ = ('cc_expires_month_field', 'cc_expires_year_field')

    datetime_module = None

    messages = {
        'notANumber': "Please enter numbers only for month and year",
        'invalidNumber': "Invalid Expiration Date",
        }

    def validate_partial(self, field_dict, state):
        if not field_dict.get(self.cc_expires_month_field, None) \
           or not field_dict.get(self.cc_expires_year_field, None):
            return None
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        errors = self._validateReturn(field_dict, state)
        if errors:
            error_list = errors.items()
            error_list.sort()
            raise Invalid(
                '<br>\n'.join(["%s: %s" % (name, value)
                               for name, value in error_list]),
                field_dict, state, error_dict=errors)
        
    def _validateReturn(self, field_dict, state):
        ccExpiresMonth = str(field_dict[self.cc_expires_month_field]).strip()
        ccExpiresYear = str(field_dict[self.cc_expires_year_field]).strip()

        try:
            ccExpiresMonth = int(ccExpiresMonth)
            ccExpiresYear = int(ccExpiresYear)
            dt_mod = import_datetime(self.datetime_module)
            now = datetime_now(dt_mod)
            today = datetime_makedate(dt_mod, now.year, now.month, now.day)
            next_month = (ccExpiresMonth % 12) + 1
            if next_month == 1:
                next_month_year = ccExpiresYear + 1
            else:
                next_month_year = ccExpiresYear
            expires_date = datetime_makedate(dt_mod, next_month_year, next_month, 1)
            assert expires_date > today
        except ValueError:
            return {self.cc_expires_month_field: self.message('notANumber', state),
                    self.cc_expires_year_field: self.message('notANumber', state)}
        except AssertionError:
            return {self.cc_expires_month_field: self.message('invalidNumber', state),
                    self.cc_expires_year_field: self.message('invalidNumber', state)}

class CreditCardSecurityCode(FormValidator):
    """
    Checks that credit card security code has the correct number
    of digits for the given credit card type.

    You pass in the name of the field that has the credit card
    type and the field with the credit card security code.

    ::

        >>> code = CreditCardSecurityCode()
        >>> code.to_python({'ccType': 'visa', 'ccCode': '111'})
        {'ccType': 'visa', 'ccCode': '111'}
        >>> code.to_python({'ccType': 'visa', 'ccCode': '1111'})
        Traceback (most recent call last):
            ...
        Invalid: ccCode: Invalid credit card security code length
    """

    validate_partial_form = True

    cc_type_field = 'ccType'
    cc_code_field = 'ccCode'
    __unpackargs__ = ('cc_type_field', 'cc_code_field')

    messages = {
        'notANumber': "Please enter numbers only for credit card security code",
        'badLength': "Invalid credit card security code length",
        }

    def validate_partial(self, field_dict, state):
        if not field_dict.get(self.cc_type_field, None) \
           or not field_dict.get(self.cc_code_field, None):
            return None
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        errors = self._validateReturn(field_dict, state)
        if errors:
            error_list = errors.items()
            error_list.sort()
            raise Invalid(
                '<br>\n'.join(["%s: %s" % (name, value)
                               for name, value in error_list]),
                field_dict, state, error_dict=errors)

    def _validateReturn(self, field_dict, state):
        ccType = str(field_dict[self.cc_type_field]).strip()
        ccCode = str(field_dict[self.cc_code_field]).strip()

        try:
            int(ccCode)
        except ValueError:
            return {self.cc_code_field: self.message('notANumber', state)}

        length = self._cardInfo[ccType]
        validLength = False
        if len(ccCode) == length:
            validLength = True
        if not validLength:
            return {self.cc_code_field: self.message('badLength', state)}

    # key = credit card type
    # value = length of security code
    _cardInfo = {
        "visa": 3,
        "mastercard": 3,
        "discover": 3,
        "amex": 4,
            }


__all__ = []
for name, value in globals().items():
    if isinstance(value, type) and issubclass(value, Validator):
        __all__.append(name)

