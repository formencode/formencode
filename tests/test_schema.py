from formencode import validators, foreach
from formencode.schema import Schema, merge_dicts, SimpleFormValidator
from formencode.api import *
from formencode.variabledecode import NestedVariables
import cgi


def setup_module(module):
    """Disable i18n translation
    """
    def notranslation(s): return s
    import __builtin__
    __builtin__._ = notranslation



def teardown_module(module):
    """Remove translation function
    """
    import __builtin__
    del __builtin__._


def d(**kw):
    return kw

def cgi_parse(qs):
    """
    Parses a query string and returns the usually dictionary.
    """
    d = {}
    for key, value in cgi.parse_qsl(qs, 1):
        if key in d:
            if isinstance(d[key], list):
                d[key].append(value)
            else:
                d[key] = [d[key], value]
        else:
            d[key] = value
    return d


class DecodeCase(object):

    error_expected = False

    def __init__(self, schema, input, **output):
        self.raw_input = input
        self.schema = schema
        if isinstance(input, str):
            input = cgi_parse(input)
        self.input = input
        self.output = output
        all_cases.append(self)

    def test(self):
        print 'input', repr(self.input)
        actual = self.schema.to_python(self.input)
        print 'output', repr(actual)
        assert actual == self.output


class BadCase(DecodeCase):

    error_expected = True

    def __init__(self, *args, **kw):
        DecodeCase.__init__(self, *args, **kw)
        if len(self.output) == 1 and 'text' in self.output:
            self.output = self.output['text']

    def test(self):
        print repr(self.raw_input)
        try:
            print repr(self.schema.to_python(self.input))
        except Invalid, e:
            actual = e.unpack_errors()
            assert actual == self.output
        else:
            assert False, "Exception expected"


class Name(Schema):
    fname = validators.String(not_empty=True)
    mi = validators.String(max=1, if_missing=None, if_empty=None)
    lname = validators.String(not_empty=True)


all_cases = []

DecodeCase(Name, 'fname=Ian&mi=S&lname=Bicking',
           fname='Ian', mi='S', lname='Bicking')

DecodeCase(Name, 'fname=Ian&lname=Bicking',
           fname='Ian', mi=None, lname='Bicking')

BadCase(Name, 'fname=&lname=',
        fname='Please enter a value',
        lname='Please enter a value')

BadCase(Name, 'fname=Franklin&mi=Delano&lname=Roosevelt',
        mi="Enter a value not more than 1 characters long")

BadCase(Name, '',
        fname='Missing value',
        lname='Missing value')


class AddressesForm(Schema):
    pre_validators = [NestedVariables()]
    class addresses(foreach.ForEach):
        class schema(Schema):
            name = Name()
            email = validators.Email()


DecodeCase(AddressesForm,
           'addresses-2.name.fname=Jill&addresses-1.name.fname=Bob&'
           'addresses-1.name.lname=Briscoe&'
           'addresses-1.email=bob@bobcom.com&'
           'addresses-2.name.lname=Hill&addresses-2.email=jill@hill.com&'
           'addresses-2.name.mi=J',
           addresses=[d(name=d(fname='Bob', mi=None, lname='Briscoe'),
                        email='bob@bobcom.com'),
                      d(name=d(fname='Jill', mi='J', lname='Hill'),
                        email='jill@hill.com')])

DecodeCase(AddressesForm,
           '',
           addresses=[])

BadCase(AddressesForm,
        'addresses-1.name.fname=&addresses-1.name.lname=x&'
        'addresses-1.email=x@domain.com',
        addresses=[d(name=d(fname="Please enter a value"))])

BadCase(AddressesForm,
        'whatever=nothing',
        text="The input field 'whatever' was not expected.")


def test_this():

    for case in all_cases:
        yield (case.test,)


def test_merge():
    assert (merge_dicts(dict(a='a'), dict(b='b'))
            == dict(a='a', b='b'))
    assert (merge_dicts(dict(a='a', c='c'), dict(a='a', b='b'))
            == dict(a='a\na', b='b', c='c'))
    assert (merge_dicts(dict(a=['a1', 'a2'], b=['b'], c=['c']),
                        dict(a=['aa1'],
                             b=['bb', 'bbb'],
                             c='foo'))
            == dict(a=['a1\naa1', 'a2'], b=['b\nbb', 'bbb'],
                    c=['c']))


class ChainedTest(Schema):
    a = validators.String()
    a_confirm = validators.String()

    b = validators.String()
    b_confirm = validators.String()

    chained_validators = [validators.FieldsMatch('a', 'a_confirm'),
                            validators.FieldsMatch('b', 'b_confirm')]


def test_multiple_chained_validators_errors():
    s = ChainedTest()
    try:
        s.to_python({'a':'1', 'a_confirm':'2', 'b':'3', 'b_confirm':'4'})
    except Invalid, e:
        assert 'a_confirm' in e.error_dict and 'b_confirm' in e.error_dict
    try:
        s.to_python({})
    except Invalid, e:
        pass
    else:
        assert False


def test_SimpleFormValidator_doc():
    """
    Verify SimpleFormValidator preserves the decorated function's docstring.
    """

    BOGUS_DOCSTRING = "blah blah blah"

    def f(value_dict, state, validator):
        value_dict['f'] = 99

    f.__doc__ = BOGUS_DOCSTRING
    g = SimpleFormValidator(f)

    assert f.__doc__ == g.__doc__, "Docstrings don't match!"


class TestAtLeastOneCheckboxIsChecked(object):
    """ tests to address sourceforge bug #1777245

        The reporter is trying to enforce agreement to a Terms of Service
        agreement, with failure to check the 'I agree' checkbox handled as
        a validation failure. The tests below illustrate a working approach.
    """

    def setup(self):
        self.not_empty_messages = {'missing': 'a missing value message'}
        class CheckForCheckboxSchema(Schema):
            agree = validators.StringBool(messages=self.not_empty_messages)
        self.schema = CheckForCheckboxSchema()

    def test_Schema_with_input_present(self):
        # <input type="checkbox" name="agree" value="yes" checked="checked">
        result = self.schema.to_python({'agree': 'yes'})
        assert result['agree'] is True

    def test_Schema_with_input_missing(self):
        # <input type="checkbox" name="agree" value="yes">
        try:
            self.schema.to_python({})
        except Invalid, exc:
            error_message = exc.error_dict['agree'].msg
            assert self.not_empty_messages['missing'] == error_message, \
                error_message
        else:
            assert False, 'missing input not detected'
