# -*- coding: utf-8 -*-

import datetime
import unittest

from formencode.validators import DateConverter, Int, Invalid, OpenId, \
    String, TimeConverter, UnicodeString, XRI, URL
from formencode.variabledecode import NestedVariables
from formencode.schema import Schema
from formencode.foreach import ForEach
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
    assert un.from_python(12) == '12'
    assert type(un.from_python(12)) is str


def test_unicode_encoding():
    uv = UnicodeString()
    us = u'käse'
    u7s, u8s = us.encode('utf-7'), us.encode('utf-8')
    assert uv.to_python(u8s) == us
    assert type(uv.to_python(u8s)) is unicode
    assert uv.from_python(us) == u8s
    assert type(uv.from_python(us)) is str
    uv = UnicodeString(encoding='utf-7')
    assert uv.to_python(u7s) == us
    assert type(uv.to_python(u7s)) is unicode
    assert uv.from_python(us) == u7s
    assert type(uv.from_python(us)) is str
    uv = UnicodeString(inputEncoding='utf-7')
    assert uv.to_python(u7s) == us
    assert type(uv.to_python(u7s)) is unicode
    uv = UnicodeString(outputEncoding='utf-7')
    assert uv.from_python(us) == u7s
    assert type(uv.from_python(us)) is str
    uv = UnicodeString(inputEncoding=None)
    assert uv.to_python(us) == us
    assert type(uv.to_python(us)) is unicode
    assert uv.from_python(us) == u8s
    assert type(uv.from_python(us)) is str
    uv = UnicodeString(outputEncoding=None)
    assert uv.to_python(u8s) == us
    assert type(uv.to_python(u8s)) is unicode
    assert uv.from_python(us) == us
    assert type(uv.from_python(us)) is unicode


def test_unicode_empty():
    iv = UnicodeString()
    for value in [None, "", u""]:
        result = iv.to_python(value)
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


def test_int_minmax_mandatory():
    messages = Int().message
    iv = Int(min=5, max=10, not_empty=True)
    assert validate(iv, None) == messages('empty', None)
    assert validate(iv, "1") == messages('tooLow', None, min=5)
    assert validate(iv, "15") == messages('tooHigh', None, max=10)


def test_month_style():
    dc = DateConverter(month_style='dd/mm/yyyy')
    d = datetime.date(2007,12,20)
    assert dc.to_python('20/12/2007') == d
    assert dc.from_python(d) == '20/12/2007'
    assert dc.to_python('20/December/2007') == d


def test_date():
    dc = DateConverter(month_style='dd/mm/yyyy')
    try:
        dc.to_python('20/12/150')
    except Invalid, e:
        assert 'Please enter a four-digit year after 1899' in str(e)
    else:
        assert False, 'Date should be invalid'
    try:
        dc.to_python('oh/happy/day')
    except Invalid, e:
        assert 'Please enter the date in the form dd/mm/yyyy' in str(e)
    else:
        assert False, 'Date should be invalid'


def test_time():
    tc = TimeConverter()
    assert tc.to_python('20:30:15') == (20, 30, 15)
    try:
        tc.to_python('25:30:15')
    except Invalid, e:
        assert 'You must enter an hour in the range 0-23' in str(e)
    else:
        assert False, 'Time should be invalid'
    try:
        tc.to_python('20:75:15')
    except Invalid, e:
        assert 'You must enter a minute in the range 0-59' in str(e)
    else:
        assert False, 'Time should be invalid'
    try:
        tc.to_python('20:30:75')
    except Invalid, e:
        assert 'You must enter a second in the range 0-59' in str(e)
    else:
        assert False, 'Time should be invalid'
    try:
        tc.to_python('20:30:zx')
    except Invalid, e:
        assert 'The second value you gave is not a number' in str(e)
        assert 'zx' in str(e)
    else:
        assert False, 'Time should be invalid'


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


class TestXRIValidator(unittest.TestCase):
    """Generic tests for the XRI validator"""

    def test_creation_valid_params(self):
        """The creation of an XRI validator with valid parameters must
        succeed"""
        XRI()
        XRI(True, "i-name")
        XRI(True, "i-number")
        XRI(False, "i-name")
        XRI(False, "i-number")

    def test_creation_invalid_xri(self):
        """Only "i-name" and "i-number" are valid XRIs"""
        self.assertRaises(AssertionError, XRI, True, 'i-something')

    def test_valid_simple_individual_iname_without_type(self):
        """XRIs must start with either an equals sign or an at sign"""
        validator = XRI(True, "i-name")
        self.assertRaises(Invalid, validator.validate_python, 'Gustavo')

    def test_valid_iname_with_schema(self):
        """XRIs may have their schema in the beggining"""
        validator = XRI()
        self.assertEqual(validator.to_python('xri://=Gustavo'),
                         'xri://=Gustavo')

    def test_schema_is_added_if_asked(self):
        """The schema must be added to an XRI if explicitly asked"""
        validator = XRI(True)
        self.assertEqual(validator.to_python('=Gustavo'),
                         'xri://=Gustavo')

    def test_schema_not_added_if_not_asked(self):
        """The schema must not be added to an XRI unless explicitly asked"""
        validator = XRI()
        self.assertEqual(validator.to_python('=Gustavo'), '=Gustavo')

    def test_spaces_are_trimmed(self):
        """Spaces at the beggining or end of the XRI are removed"""
        validator = XRI()
        self.assertEqual(validator.to_python('    =Gustavo  '), '=Gustavo')


class TestINameValidator(unittest.TestCase):
    """Tests for the XRI i-names validator"""

    def setUp(self):
        self.validator = XRI(xri_type="i-name")

    def test_valid_global_individual_iname(self):
        """Global & valid individual i-names must pass validation"""
        self.validator.validate_python('=Gustavo')

    def test_valid_global_organizational_iname(self):
        """Global & valid organizational i-names must pass validation"""
        self.validator.validate_python('@Canonical')

    def test_invalid_iname(self):
        """Non-string i-names are rejected"""
        self.assertRaises(Invalid, self.validator.validate_python, None)

    def test_exclamation_in_inames(self):
        """Exclamation marks at the beggining of XRIs is something specific
        to i-numbers and must be rejected in i-names"""
        self.assertRaises(Invalid, self.validator.validate_python,
                          "!!1000!de21.4536.2cb2.8074")

    def test_repeated_characters(self):
        """Dots and dashes must not be consecutively repeated in i-names"""
        self.assertRaises(Invalid, self.validator.validate_python,
                          "=Gustavo--Narea")
        self.assertRaises(Invalid, self.validator.validate_python,
                          "=Gustavo..Narea")

    def test_punctuation_marks_at_beggining(self):
        """Punctuation marks at the beggining of i-names are forbidden"""
        self.assertRaises(Invalid, self.validator.validate_python,
                          "=.Gustavo")
        self.assertRaises(Invalid, self.validator.validate_python,
                          "=-Gustavo.Narea")

    def test_numerals_at_beggining(self):
        """Numerals at the beggining of i-names are forbidden"""
        self.assertRaises(Invalid, self.validator.validate_python,
                          "=1Gustavo")

    def test_non_english_inames(self):
        """i-names with non-English characters are valid"""
        self.validator.validate_python(u'=Gustavo.Narea.García')
        self.validator.validate_python(u'@名前.例')

    def test_inames_plus_paths(self):
        """i-names with paths are valid but not supported"""
        self.assertRaises(Invalid, self.validator.validate_python,
                          "=Gustavo/(+email)")

    def test_communities(self):
        """i-names may have so-called 'communities'"""
        self.validator.validate_python(u'=María*Yolanda*Liliana*Gustavo')
        self.validator.validate_python(u'=Gustavo*Andreina')
        self.validator.validate_python(u'@IBM*Lenovo')


class TestINumberValidator(unittest.TestCase):
    """Tests for the XRI i-number validator"""

    def setUp(self):
        self.validator = XRI(xri_type="i-number")

    def test_valid_global_personal_inumber(self):
        """Global & valid personal i-numbers must pass validation"""
        self.validator.validate_python('=!1000.a1b2.93d2.8c73')

    def test_valid_global_organizational_inumber(self):
        """Global & valid organizational i-numbers must pass validation"""
        self.validator.validate_python('@!1000.a1b2.93d2.8c73')

    def test_valid_global_network_inumber(self):
        """Global & valid network i-numbers must pass validation"""
        self.validator.validate_python('!!1000')

    def test_valid_community_personal_inumbers(self):
        """Community & valid personal i-numbers must pass validation"""
        self.validator.validate_python('=!1000.a1b2.93d2.8c73!3ae2!1490')

    def test_valid_community_organizational_inumber(self):
        """Community & valid organizational i-numbers must pass validation"""
        self.validator.validate_python('@!1000.9554.fabd.129c!2847.df3c')

    def test_valid_community_network_inumber(self):
        """Community & valid network i-numbers must pass validation"""
        self.validator.validate_python('!!1000!de21.4536.2cb2.8074')


class TestOpenIdValidator(unittest.TestCase):
    """Tests for the OpenId validator"""

    def setUp(self):
        self.validator = OpenId(add_schema=False)

    def test_url(self):
        self.assertEqual(self.validator.to_python('http://example.org'),
                         'http://example.org')

    def test_iname(self):
        self.assertEqual(self.validator.to_python('=Gustavo'), '=Gustavo')

    def test_inumber(self):
        self.assertEqual(self.validator.to_python('!!1000'), '!!1000')

    def test_email(self):
        """Email addresses are not valid OpenIds!"""
        self.assertRaises(Invalid, self.validator.to_python,
                          "wait@busstop.com")

    def test_prepending_schema(self):
        validator = OpenId(add_schema=True)
        self.assertEqual(validator.to_python("example.org"),
                         "http://example.org")
        self.assertEqual(validator.to_python("=Gustavo"),
                         "xri://=Gustavo")
        self.assertEqual(validator.to_python("!!1000"),
                         "xri://!!1000")

class TestURLValidator(unittest.TestCase):

    def setUp(self):
        self.validator = URL()

    def test_cojp(self):
        self.assertEqual(self.validator.to_python('http://domain.co.jp'), 'http://domain.co.jp')

    def test_1char_thirdlevel(self):
        self.assertEqual(self.validator.to_python('http://c.somewhere.pl/wi16677/5050f81b001f9e5f45902c1b/'),
                                                  'http://c.somewhere.pl/wi16677/5050f81b001f9e5f45902c1b/')

