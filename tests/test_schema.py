from formencode import validators, foreach
from formencode.schema import Schema, merge_dicts
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


def d(**kw): return kw

def cgi_parse(qs):
    """
    Parses a query string and returns the usually dictionary.
    """
    d = {}
    for key, value in cgi.parse_qsl(qs, 1):
        if d.has_key(key):
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
        if len(self.output) == 1 and self.output.has_key('text'):
            self.output = self.output['text']

    def test(self):
        print repr(self.raw_input)
        try:
            print repr(self.schema.to_python(self.input))
        except Invalid, e:
            actual = e.unpack_errors()
            assert actual == self.output
        else:
            assert 0, "Exception expected"

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
        mi="Enter a value less than 1 characters long")

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
        'addresses-1.email=x@x.com',
        addresses=[d(name=d(fname="Please enter a value"))])
        
BadCase(AddressesForm,
        'whatever=nothing',
        text="The input field 'whatever' was not expected.")

def test_this():

    for case in all_cases:
        yield case.test


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
    try:
        s = ChainedTest()
        s.to_python({'a':'1', 'a_confirm':'2', 'b':'3', 'b_confirm':'4'})
    except Invalid, e:
        assert(e.error_dict.has_key('a_confirm') and e.error_dict.has_key('b_confirm'))
