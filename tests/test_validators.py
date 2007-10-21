from formencode.validators import String, UnicodeString, Invalid, Int
from formencode.validators import DateConverter
from formencode.variabledecode import NestedVariables
from formencode.schema import Schema
from formencode.foreach import ForEach
import datetime
from formencode.api import NoDefault

def validate(validator, value):
    try:
        return validator.to_python(value)
        return None
    except Invalid, e:
        return e.unpack_errors()

def validate_from(validator, value):
    try:
        validator.from_python(value)
        return None
    except Invalid, e:
        return e.unpack_errors()

messages = String().message

def test_sv_min():
    sv = String(min=2, accept_python=False)
    assert sv.to_python("foo") == "foo"
    assert validate(sv, "x") == messages('tooShort', None, min=2)
    assert validate(sv, None) == messages('empty', None)
    # should be completely invalid?
    assert validate(sv, []) == messages('empty', None, min=2)
    assert sv.from_python(['x', 'y']) == 'x, y'

def test_sv_not_empty():
    sv = String(not_empty=True)
    assert validate(sv, "") == messages('empty', None)
    assert validate(sv, None) == messages('empty', None)
    # should be completely invalid?
    assert validate(sv, []) == messages('empty', None)
    assert validate(sv, {}) == messages('empty', None)

def test_sv_string_conversion():
    sv = String(not_empty=False)
    assert sv.from_python(2) == "2"
    assert sv.from_python([]) == ""


def test_unicode():
    un = UnicodeString()
    assert un.to_python(12) == u'12'
    assert type(un.to_python(12)) is unicode

def test_unicode_empty():
    iv = UnicodeString()
    for input in [None, "", u""]:
        result = iv.to_python(input)
        assert u"" == result, result
        assert isinstance(result, unicode)


def test_int_min():
    messages = Int().message
    iv = Int(min=5)
    assert iv.to_python("5") == 5
    assert validate(iv, "1") == messages('tooLow', None, min=5)

def test_int_max():
    messages = Int().message
    iv = Int(max=10)
    assert iv.to_python("10") == 10
    assert validate(iv, "15") == messages('tooHigh', None, max=10)

def test_int_minmax_optional():
    messages = Int().message
    iv = Int(min=5, max=10, if_empty=None)
    assert iv.to_python("") == None
    assert iv.to_python(None) == None
    assert iv.to_python('7') == 7
    assert validate(iv, "1") == messages('tooLow', None, min=5)
    assert validate(iv, "15") == messages('tooHigh', None, max=10)

def test_int_minmax_optional():
    messages = Int().message
    iv = Int(min=5, max=10, not_empty=True)
    assert validate(iv, None) == messages('empty', None)
    assert validate(iv, "1") == messages('tooLow', None, min=5)
    assert validate(iv, "15") == messages('tooHigh', None, max=10)

def test_month_style():
    date = DateConverter(month_style='dd/mm/yyy')
    d = datetime.date(2007,12,20)
    assert date.to_python('20/12/2007') == d
    assert date.from_python(d) == '20/12/2007'

def test_date():
    date = DateConverter(month_style='dd/mm/yyy')
    try:
        date.to_python('20/12/150')
    except Invalid, e:
        assert 'Please enter a four-digit year after 1899' in str(e)


def test_foreach_if_missing():

    class SubSchema(Schema):
        age = Int()
        name = String(not_empty=True)

    class MySchema(Schema):
        pre_validators = [NestedVariables()]
        people = ForEach(SubSchema(), if_missing=NoDefault, messages={'missing':'Please add a person'})

    start_values = {}

    class State:
        pass

    validator = MySchema()
    assert validator.fields['people'].not_empty == False

    state = State()

    try:
        values = validator.to_python(start_values, state)
    except Invalid, e:
        assert e.unpack_errors() == {'people': u'Please add a person'}
    else:
        raise Exception("Shouldn't be valid data", values, start_values)

