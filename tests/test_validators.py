from formencode.validators import String, UnicodeString, Invalid, Int

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



