import sys
import os
import re

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
from validator import htmlfill
from validator.doctest_xml_compare import xml_compare
from elementtree import ElementTree as et
from xml.parsers.expat import ExpatError
from validator import htmlfill_schemabuilder

def test_inputoutput():
    data_dir = os.path.join(os.path.dirname(__file__), 'htmlfill_data')
    for fn in os.listdir(data_dir):
        if fn.startswith('data-'):
            fn = os.path.join(data_dir, fn)
            yield run_filename, fn

def run_filename(filename):
    f = open(filename)
    content = f.read()
    f.close()
    parts = re.split(r'---*', content)
    template = parts[0]
    expected = parts[1]
    if len(parts) == 3:
        data_content = parts[2].strip()
    elif len(parts) > 3:
        print parts[3:]
        assert 0, "Too many sections"
    else:
        data_content = ''
    namespace = {}
    if data_content:
        exec data_content in namespace
    data = namespace.copy()
    data['defaults'] = data.get('defaults', {})
    if data.has_key('check'):
        checker = data['check']
        del data['check']
    else:
        def checker(p, s):
            pass
    for name in data.keys():
        if name.startswith('_') or hasattr(__builtins__, name):
            del data[name]
    listener = htmlfill_schemabuilder.SchemaBuilder()
    p = htmlfill.FillingParser(listener=listener, **data)
    p.feed(template)
    p.close()
    output = p.text()
    def reporter(v):
        print v
    try:
        output_xml = et.XML(output)
        expected_xml = et.XML(expected)
    except ExpatError:
        comp = output.strip() == expected.strip()
    else:
        comp = xml_compare(output_xml, expected_xml, reporter)
    if not comp:
        print '---- Output:   ----'
        print output
        print '---- Expected: ----'
        print expected
        assert 0
    checker(p, listener.schema())
