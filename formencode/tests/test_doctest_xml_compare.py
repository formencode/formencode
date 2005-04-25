import formencode.doctest_xml_compare as dxml
from formencode.htmlgen import html
import sys

XML = dxml.et.XML
tostring = dxml.et.tostring

def test_xml_compare():
    t1 = XML('<test />')
    t2 = XML('<test/>')
    result = []
    assert dxml.xml_compare(t1, t2, sys.stdout.write)
    assert dxml.xml_compare(XML('''<hey>
    <you>!!</you>  </hey>'''), XML('<hey><you>!!</you></hey>'),
                            sys.stdout.write)
