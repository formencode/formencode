from testcase import TestCase
import validators
import foreach
from schema import Schema
from api import *
from variabledecode import NestedVariables

def d(**kw): return kw

class SchemaTest(TestCase):

    def testGood(self, description, schema, input, output):
        if isinstance(input, str):
            input = self.cgi_parse(input)
        real = to_python(schema, input)
        if isinstance(real, dict):
            self.assert_dict_equal(real, output)
        else:
            self.assertEqual(real, output)

    params_testGood = []

    def testBad(self, description, schema, input, errors):
        if isinstance(input, str):
            input = self.cgi_parse(input)
        try:
            to_python(schema, input)
        except Invalid, e:
            out = makeComparable(e, errors)
            if isinstance(out, dict) and isinstance(errors, dict):
                self.assert_dict_equal(out, errors or {})
            else:
                self.assertEqual(str(e), errors)
        else:
            assert 0, "Exception expected"

    params_testBad = []

def makeComparable(exc, error):
    if exc is None:
        return None
    if isinstance(error, str):
        return str(exc)
    elif isinstance(error, list) or not error and exc.error_list:
        if not exc.error_list:
            return []
        result = []
        if error:
            for i in range(len(error)):
                try:
                    excItem = exc.error_list[i]
                except IndexError:
                    excItem = None
                result.append(makeComparable(excItem, error[i]))
        else:
            for v in exc.error_list:
                result.append(makeComparable(v, None))
        return result
    elif isinstance(error, dict) or not error and exc.error_dict:
        if not exc.error_dict:
            return {}
        result = {}
        if error:
            for name in error.keys():
                result[name] = makeComparable(exc.error_dict.get(name),
                                              error[name])
            for name in exc.error_dict.keys():
                if result.has_key(name):
                    continue
                result[name] = makeComparable(exc.error_dict[name],
                                              None)
        else:
            for name, value in exc.error_dict.items():
                result[name] = makeComparable(value, None)
        return result
    else:
        return str(exc)

def addGood(schema, input, output):
    if isinstance(schema, type):
        name = schema.__name__
    else:
        name = schema.__class__.__name__
    SchemaTest.params_testGood.append((name, schema, input, output))

def addBad(schema, input, errors):
    if isinstance(schema, type):
        name = schema.__name__
    else:
        name = schema.__class__.__name__
    SchemaTest.params_testBad.append((name, schema, input, errors))

class Name(Schema):
    fname = validators.String(not_empty=True)
    mi = validators.String(max=1, if_missing=None, if_empty=None)
    lname = validators.String(not_empty=True)

addGood(Name, 'fname=Ian&mi=S&lname=Bicking',
        d(fname='Ian', mi='S', lname='Bicking'))

addGood(Name, 'fname=Ian&lname=Bicking',
        d(fname='Ian', mi=None, lname='Bicking'))

addBad(Name, 'fname=&lname=',
       d(fname='Please enter a value',
         lname='Please enter a value'))

addBad(Name, 'fname=Franklin&mi=Delano&lname=Roosevelt',
       d(mi="Enter a value less than 1 characters long"))

addBad(Name, '',
       d(fname='Missing value',
         lname='Missing value'))

class AddressesForm(Schema):
    pre_validators=[NestedVariables()]
    class addresses(foreach.ForEach):
        class schema(Schema):
            name = Name()
            email = validators.Email()

addGood(AddressesForm,
        'addresses-2.name.fname=Jill&addresses-1.name.fname=Bob&addresses-1.name.lname=Briscoe&addresses-1.email=bob@bobcom.com&addresses-2.name.lname=Hill&addresses-2.email=jill@hill.com&addresses-2.name.mi=J',
        d(addresses=[d(name=d(fname='Bob', mi=None, lname='Briscoe'),
                       email='bob@bobcom.com'),
                     d(name=d(fname='Jill', mi='J', lname='Hill'),
                       email='jill@hill.com')]))

addGood(AddressesForm,
        '',
        d(addresses=[]))

addBad(AddressesForm,
       'addresses-1.name.fname=&addresses-1.name.lname=x&addresses-1.email=x@x.com',
       d(addresses=[d(name=d(fname="Please enter a value"))]))
        
addBad(AddressesForm,
       'whatever=nothing',
       "The input field 'whatever' was not expected.")

