from formencode.validators import String, Invalid

def validate(validator, value):
    try:
        validator.to_python(value)
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

