# -*- coding: utf-8 -*-

import datetime
import unittest
from nose.plugins.skip import SkipTest

from formencode import validators
from formencode.validators import Invalid
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


class TestValidators(unittest.TestCase):

    def testHelp(self):
        from pydoc import text, plain
        s = plain(text.document(validators))
        self.assert_('Validator/Converters for use with FormEncode.' in s)
        self.assert_('class Bool' in s)
        self.assert_('Always Valid, returns True or False' in s)
        self.assert_('class Email' in s)
        self.assert_('Validate an email address.' in s)
        self.assert_('class FieldsMatch' in s)
        self.assert_('Tests that the given fields match' in s)


class TestStringValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.String()
        self.messages = self.validator.message

    def test_sv_min(self):
        sv = self.validator(min=2, accept_python=False)
        self.assertEqual(sv.to_python("foo"), "foo")
        self.assertEqual(validate(sv, "x"),
            self.messages('tooShort', None, min=2))
        self.assertEqual(validate(sv, None), self.messages('empty', None))
        # should be completely invalid?
        self.assertEqual(validate(sv, []), self.messages('empty', None, min=2))
        self.assertEqual(sv.from_python(['x', 'y']), 'x, y')

    def test_sv_not_empty(self):
        sv = self.validator(not_empty=True)
        self.assertEqual(validate(sv, ""), self.messages('empty', None))
        self.assertEqual(validate(sv, None), self.messages('empty', None))
        # should be completely invalid?
        self.assertEqual(validate(sv, []), self.messages('empty', None))
        self.assertEqual(validate(sv, {}), self.messages('empty', None))

    def test_sv_string_conversion(self):
        sv = self.validator(not_empty=False)
        self.assertEqual(sv.from_python(2), "2")
        self.assertEqual(sv.from_python([]), "")


class TestUnicodeStringValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.UnicodeString

    def test_unicode(self):
        un = self.validator()
        self.assertEqual(un.to_python(12), u'12')
        self.failUnless(type(un.to_python(12)) is unicode)
        self.assertEqual(un.from_python(12), '12')
        self.failUnless(type(un.from_python(12)) is str)

    def test_unicode_encoding(self):
        uv = self.validator()
        us = u'käse'
        u7s, u8s = us.encode('utf-7'), us.encode('utf-8')
        self.assertEqual(uv.to_python(u8s), us)
        self.failUnless(type(uv.to_python(u8s)) is unicode)
        self.assertEqual(uv.from_python(us), u8s)
        self.failUnless(type(uv.from_python(us)) is str)
        uv = self.validator(encoding='utf-7')
        self.assertEqual(uv.to_python(u7s), us)
        self.failUnless(type(uv.to_python(u7s)) is unicode)
        self.assertEqual(uv.from_python(us), u7s)
        self.failUnless(type(uv.from_python(us)) is str)
        uv = self.validator(inputEncoding='utf-7')
        self.assertEqual(uv.to_python(u7s), us)
        self.failUnless(type(uv.to_python(u7s)) is unicode)
        uv = self.validator(outputEncoding='utf-7')
        self.assertEqual(uv.from_python(us), u7s)
        self.failUnless(type(uv.from_python(us)) is str)
        uv = self.validator(inputEncoding=None)
        self.assertEqual(uv.to_python(us), us)
        self.failUnless(type(uv.to_python(us)) is unicode)
        self.assertEqual(uv.from_python(us), u8s)
        self.failUnless(type(uv.from_python(us)) is str)
        uv = self.validator(outputEncoding=None)
        self.assertEqual(uv.to_python(u8s), us)
        self.failUnless(type(uv.to_python(u8s)) is unicode)
        self.assertEqual(uv.from_python(us), us)
        self.failUnless(type(uv.from_python(us)) is unicode)

        def test_unicode_empty(self):
            iv = self.validator()
            for value in [None, "", u""]:
                result = iv.to_python(value)
                self.assertEqual(result, u"")
                self.failUnless(isinstance(result, unicode))


class TestIntValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.Int
        self.messages = self.validator.message

    def test_int_min(self):
        iv = self.validator(min=5)
        self.assertEqual(iv.to_python("5"), 5)
        self.assertEqual(validate(iv, "1"),
            self.messages('tooLow', None, min=5))

    def test_int_max(self):
        iv = self.validator(max=10)
        self.assertEqual(iv.to_python("10"), 10)
        self.assertEqual(validate(iv, "15"),
            self.messages('tooHigh', None, max=10))

    def test_int_minmax_optional(self):
        iv = self.validator(min=5, max=10, if_empty=None)
        self.failUnless(iv.to_python("") is None)
        self.failUnless(iv.to_python(None) is None)
        self.assertEqual(iv.to_python('7'), 7)
        self.assertEqual(validate(iv, "1"),
            self.messages('tooLow', None, min=5))
        self.assertEqual(validate(iv, "15"),
            self.messages('tooHigh', None, max=10))

    def test_int_minmax_mandatory(self):
        iv = validators.Int(min=5, max=10, not_empty=True)
        self.assertEqual(validate(iv, None),
            self.messages('empty', None))
        self.assertEqual(validate(iv, "1"),
            self.messages('tooLow', None, min=5))
        self.assertEqual(validate(iv, "15"),
            self.messages('tooHigh', None, max=10))


class TestNumberValidator(unittest.TestCase):
    def setUp(self):
        self.validator = validators.Number

    def test_inf(self):
        """Validate infinity if system supports it."""
        # Ability to convert to infinity depends on your C
        # Float library as well as the python version.
        try:
            inf = float('infinity')
        except ValueError:
            raise SkipTest
        self.assertEqual(self.validator.to_python('infinity'), inf)


class TestDateConverterValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.DateConverter

    def test_bad_dates(self):
        dc = self.validator(month_style='dd/mm/yyyy')
        try:
            dc.to_python('20/12/150')
        except Invalid, e:
            self.failUnless(
                'Please enter a four-digit year after 1899' in str(e))
        else:
            self.fail('Date should be invalid')
        try:
            dc.to_python('oh/happy/day')
        except Invalid, e:
            self.failUnless(
                'Please enter the date in the form dd/mm/yyyy' in str(e))
        else:
            self.fail('Date should be invalid')

    def test_month_style(self):
        d = datetime.date(2007, 12, 20)
        dc = self.validator()
        self.assertEqual(dc.month_style, 'mm/dd/yyyy')
        self.assertEqual(dc.to_python('12/20/2007'), d)
        self.assertEqual(dc.from_python(d), '12/20/2007')
        self.assertEqual(dc.to_python('Dec/20/2007'), d)
        self.assertEqual(dc.to_python('December/20/2007'), d)
        try:
            self.assertEqual(dc.to_python('20/12/2007'), d)
        except Invalid, e:
            self.failUnless('Please enter a month from 1 to 12' in str(e))
        else:
            self.fail('Date should be invalid')
        try:
            self.assertEqual(dc.to_python('12/Dec/2007'), d)
        except Invalid, e:
            self.failUnless(
                'Please enter the date in the form mm/dd/yyyy' in str(e))
        else:
            self.fail('Date should be invalid')
        dc = self.validator(month_style='dd/mm/yyyy')
        self.assertEqual(dc.month_style, 'dd/mm/yyyy')
        self.assertEqual(dc.to_python('20/12/2007'), d)
        self.assertEqual(dc.from_python(d), '20/12/2007')
        self.assertEqual(dc.to_python('20/Dec/2007'), d)
        self.assertEqual(dc.to_python('20/December/2007'), d)
        try:
            self.assertEqual(dc.to_python('12/20/2007'), d)
        except Invalid, e:
            self.failUnless('Please enter a month from 1 to 12' in str(e))
        else:
            self.fail('Date should be invalid')
        try:
            self.assertEqual(dc.to_python('Dec/12/2007'), d)
        except Invalid, e:
            self.failUnless(
                'Please enter the date in the form dd/mm/yyyy' in str(e))
        else:
            self.fail('Date should be invalid')


class TestTimeConverterValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.TimeConverter

    def test_time(self):
        tc = self.validator()
        self.assertEqual(tc.to_python('20:30:15'), (20, 30, 15))
        try:
            tc.to_python('25:30:15')
        except Invalid, e:
            self.failUnless(
                'You must enter an hour in the range 0-23' in str(e))
        else:
            self.fail('Time should be invalid')
        try:
            tc.to_python('20:75:15')
        except Invalid, e:
            self.failUnless(
                'You must enter a minute in the range 0-59' in str(e))
        else:
            self.fail('Time should be invalid')
        try:
            tc.to_python('20:30:75')
        except Invalid, e:
            self.failUnless(
                'You must enter a second in the range 0-59' in str(e))
        else:
            self.fail('Time should be invalid')
        try:
            tc.to_python('20:30:zx')
        except Invalid, e:
            self.failUnless(
                'The second value you gave is not a number' in str(e))
            self.failUnless('zx' in str(e))
        else:
            self.fail('Time should be invalid')


class TestForEachValidator(unittest.TestCase):

    def test_foreach_if_missing(self):

        class SubSchema(Schema):
            age = validators.Int()
            name = validators.String(not_empty=True)

        class MySchema(Schema):
            pre_validators = [NestedVariables()]
            people = ForEach(SubSchema(), if_missing=NoDefault,
                messages={'missing': 'Please add a person'})

        validator = MySchema()

        self.failIf(validator.fields['people'].not_empty)

        class State:
            pass

        start_values = {}
        state = State()

        try:
            values = validator.to_python(start_values, state)
        except Invalid, e:
            self.assertEqual(e.unpack_errors(),
                {'people': u'Please add a person'})
        else:
            raise Exception("Shouldn't be valid data", values, start_values)


class TestXRIValidator(unittest.TestCase):
    """Generic tests for the XRI validator"""

    def setUp(self):
        self.validator = validators.XRI

    def test_creation_valid_params(self):
        """The creation of an XRI validator with valid parameters must
        succeed"""
        self.validator()
        self.validator(True, "i-name")
        self.validator(True, "i-number")
        self.validator(False, "i-name")
        self.validator(False, "i-number")

    def test_creation_invalid_xri(self):
        """Only "i-name" and "i-number" are valid XRIs"""
        self.assertRaises(AssertionError, self.validator, True, 'i-something')

    def test_valid_simple_individual_iname_without_type(self):
        """XRIs must start with either an equals sign or an at sign"""
        validator = self.validator(True, "i-name")
        self.assertRaises(Invalid, validator.validate_python, 'Gustavo')

    def test_valid_iname_with_schema(self):
        """XRIs may have their schema in the beggining"""
        validator = self.validator()
        self.assertEqual(validator.to_python('xri://=Gustavo'),
                         'xri://=Gustavo')

    def test_schema_is_added_if_asked(self):
        """The schema must be added to an XRI if explicitly asked"""
        validator = self.validator(True)
        self.assertEqual(validator.to_python('=Gustavo'),
                         'xri://=Gustavo')

    def test_schema_not_added_if_not_asked(self):
        """The schema must not be added to an XRI unless explicitly asked"""
        validator = self.validator()
        self.assertEqual(validator.to_python('=Gustavo'), '=Gustavo')

    def test_spaces_are_trimmed(self):
        """Spaces at the beggining or end of the XRI are removed"""
        validator = self.validator()
        self.assertEqual(validator.to_python('    =Gustavo  '), '=Gustavo')


class TestINameValidator(unittest.TestCase):
    """Tests for the XRI i-names validator"""

    def setUp(self):
        self.validator = validators.XRI(xri_type="i-name")

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
        self.validator = validators.XRI(xri_type="i-number")

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
        self.validator = validators.OpenId(add_schema=False)

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
        validator = validators.OpenId(add_schema=True)
        self.assertEqual(validator.to_python("example.org"),
                         "http://example.org")
        self.assertEqual(validator.to_python("=Gustavo"),
                         "xri://=Gustavo")
        self.assertEqual(validator.to_python("!!1000"),
                         "xri://!!1000")


class TestOneOfValidator(unittest.TestCase):

    def test_unicode_list(self):
        o = validators.OneOf([u'ö', u'a'])
        self.assertRaises(Invalid, o.to_python, u"ä")

    def test_ascii_list(self):
        o = validators.OneOf(['a', 'b'])
        self.assertRaises(Invalid, o.to_python, 'c')

    def test_int_list_list(self):

        class foo(Schema):
            bar = validators.OneOf((1, 2, 3), testValueList=True)

        expected = {'bar': (1, 2, 3)}
        value = foo.to_python(expected)

        self.assertEqual(expected, value)


class TestIPAddressValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.IPAddress

    def test_valid_address(self):
        self.validator().validate_python('127.0.0.1')

    def test_address_is_none(self):
        self.assertRaises(Invalid, self.validator().validate_python, None)

    def test_invalid_address(self):
        validate = self.validator().validate_python
        self.assertRaises(Invalid, validate, '127.0.1')
        self.assertRaises(Invalid, validate, '271.0.0.1')
        self.assertRaises(Invalid, validate, '127.0.0.0.1')

    def test_leading_zeros(self):
        validate = self.validator().validate_python
        try:
            validate('1.2.3.037')
        except Invalid, e:
            self.failUnless('The octets must not have leading zeros' in str(e))
        else:
            self.fail('IP address octets with leading zeros should be invalid')
        try:
            validate('1.2.3.0377')
        except Invalid, e:
            self.failUnless('The octets must not have leading zeros' in str(e))
        else:
            self.fail('IP octets with leading zeros should be invalid')

    def test_leading_zeros_allowed(self):
        validate = self.validator(leading_zeros=True).validate_python
        try:
            validate('1.2.3.037')
        except Invalid, e:
            self.fail('IP address octets with leading zeros should be valid')
        try:
            validate('1.2.3.0377')
        except Invalid, e:
            self.failUnless("The octets must be within the range of 0-255"
                " (not '377')" in str(e))
        else:
            self.fail(
                'IP address octets should not be interpreted as octal numbers')


class TestURLValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.URL()

    def test_cojp(self):
        self.assertEqual(self.validator.to_python('http://domain.co.jp'),
                         'http://domain.co.jp')

    def test_1char_thirdlevel(self):
        self.assertEqual(self.validator.to_python(
            'http://c.somewhere.pl/wi16677/5050f81b001f9e5f45902c1b/'),
            'http://c.somewhere.pl/wi16677/5050f81b001f9e5f45902c1b/')

    def test_ip_validator(self):
        self.assertEqual(validators.URL(require_tld=False).to_python(
            "http://65.18.195.155/cgi-ordoro/bo/start.cgi"),
            "http://65.18.195.155/cgi-ordoro/bo/start.cgi")


class TestRequireIfMissingValidator(unittest.TestCase):

    def setUp(self):
        self.validator = validators.RequireIfMissing

    def test_missing(self):
        v = self.validator('phone_type', missing='mail')
        self.assertEqual(
            validate(v, dict(phone_type='')),
            dict(phone_type=u'Please enter a value'))
        self.assertEqual(
            validate(v, dict(phone_type='', mail='foo@bar.org')),
            dict(phone_type='', mail='foo@bar.org'))

    def test_present(self):
        v = self.validator('phone_type', present='phone')
        self.assertEqual(
            validate(v, dict(phone_type='', phone='510 420  4577')),
            dict(phone_type=u'Please enter a value'))
        self.assertEqual(
            validate(v, dict(phone='')), dict(phone=''))

    def test_zero(self):
        v = self.validator('operator', present='operand')
        self.assertEqual(
            validate(v, dict(operator='', operand=0)),
            dict(operator=u'Please enter a value'))
