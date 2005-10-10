# @@: Note, this is an experimental (TDD) test
from sqlobject import *
from formencode.formgen import makeform
from formencode.fields import Context
from formencode.doctest_xml_compare import xml_compare, make_xml
from formencode import sqlformgen

sqlhub.processConnection = connectionForURI('sqlite:/:memory:')

CONTEXT = Context()

def printer(s):
    print s

def xcmp(a, b):
    try:
        a = '<xml>%s</xml>' % a
        xml_a = make_xml(a)
    except:
        print prxml(a)
        raise
    try:
        b = '<xml>%s</xml>' % b
        xml_b = make_xml(b)
    except:
        print prxml(b)
        raise
    prxml(a)
    prxml(b)
    assert xml_compare(xml_a, xml_b, reporter=printer)

def prxml(xml):
    for lineno, line in enumerate(xml.splitlines()):
        print '%2i %s' % (lineno+1, line)

class SimpleForm(SQLObject):

    name = StringCol()
    address = StringCol()
    city = StringCol()

SimpleForm.createTable()

def test_simple():
    f, v = makeform(SimpleForm, CONTEXT)
    yield (xcmp, f(requires_label=True).render(CONTEXT), """
    name: <input type="text" name="name" /> <br />
    address: <input type="text" name="address" /> <br />
    city: <input type="text" name="city" /> <br />
    """)
    
    f.name = 'simp'

    yield (xcmp, f(requires_label=True).render(CONTEXT), """
    name: <input type="text" name="simp.name" /> <br />
    address: <input type="text" name="simp.address" /> <br />
    city: <input type="text" name="simp.city" /> <br />
    """)

    s = SimpleForm(name='Tom', address='123', city='Chicago')
    f, v = makeform(SimpleForm, CONTEXT)
    yield (xcmp, f(requires_label=True).render(CONTEXT), """
    name: <input type="text" name="name" value="Tom" /> <br />
    address: <input type="text" name="address" value="123" /> <br />
    city: <input type="text" name="city" value="Chicago" /> <br />
    """)
    
