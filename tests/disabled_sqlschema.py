from datetime import date

import sqlobject

from formencode.sqlschema import *
from formencode import validators


def _notranslation(s):
    return s


def setup_module(module):
    """Disable i18n translation"""
    import __builtin__
    __builtin__._ = _notranslation


def teardown_module(module):
    """Remove translation function"""
    import __builtin__
    del __builtin__._


sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(
    'sqlite:/:memory:')


class EventObject(sqlobject.SQLObject):

    name = sqlobject.StringCol(alternateID=True)
    date = sqlobject.DateCol(notNull=True)
    description = sqlobject.StringCol()

EventObject.createTable()


class EventObjectSchema(sqlobject.SQLSchema):

    wrap = EventObject
    # All other columns are inherited...
    description = validators.String(strip=True, max=1024, if_empty=None)
    date = validators.DateConverter(if_empty=None)


def get_error(inp, schema):
    try:
        result = schema.to_python(inp)
        assert False, (
            "Got %r from %r instead of an Invalid exception"
            % (result, inp))
    except validators.Invalid, e:
        return e


def test_validate():
    inp = dict(name='test1', date='11/10/2010')
    res = get_error(inp, EventObjectSchema())
    assert str(res) == 'description: Missing value'
    inp['description'] = '  test  '
    obj = EventObjectSchema().to_python(inp)
    assert isinstance(obj, EventObject)
    assert obj.name == 'test1'
    assert obj.date == date(2010, 11, 10)
    assert obj.description == 'test'


def test_update():
    obj = EventObject(name='foobar', date=date(2020, 10, 1),
                      description=None)
    inp = dict(id=obj.id, date=None)
    objschema = EventObjectSchema(wrap=obj)
    assert str(get_error(inp, objschema)
        ) == 'date: You may not provide None for that value'
    inp = dict(id=obj.id, name='test2')
    print str(objschema.to_python(inp))
    assert objschema.to_python(inp) is obj
    assert obj.name == 'test2'


def test_defaults():
    res = EventObjectSchema().from_python(None)
    assert res == dict(date=None, description='')
    obj = EventObject(name='foobar2', date=date(2020, 10, 1),
                      description=None)
    res = EventObjectSchema(wrap=obj).from_python(None)
    assert res == dict(id=obj.id, date='10/01/2020',
                       name='foobar2', description='')
    obj2 = EventObject(name='bar', date=date(2002, 10, 1),
                       description='foobarish')
    # @@: Should this give an error?
    res = EventObjectSchema(wrap=obj).from_python(obj2)
    assert res == dict(id=obj2.id, date='10/01/2002',
                       name='bar', description='foobarish')
    res2 = EventObjectSchema().from_python(obj2)
    assert res2 == res


def test_sign():
    obj = EventObject(name='signer', date=date(2020, 10, 1),
                      description=None)
    s = EventObjectSchema(sign_id=True, secret='bar')
    res = s.from_python(obj)
    assert res['id'] != str(obj)
    res['name'] = 'signer_updated'
    obj_up = s.to_python(res)
    assert obj_up is obj
    assert obj_up.name == 'signer_updated'
    res2 = s.from_python(obj)
    assert res['id'] != res2['id']
    # Futz up the signature:
    res2['id'] = res2['id'][:2] + 'XXX' + res2['id'][5:]
    try:
        s.to_python(res2)
    except validators.Invalid, e:
        assert str(e) == 'Signature is not correct'
    else:
        assert False
