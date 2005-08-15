import os, sys
from py.compat import doctest
import pkg_resources
pkg_resources.require('FormEncode[testing]')

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'formencode'))

def test_doctests():
    for fn in os.listdir(os.path.dirname(__file__)):
        if fn.endswith('.txt'):
            yield do_doctest, fn

def do_doctest(fn):
    return doctest.testfile(
        fn,
        optionflags=doctest.ELLIPSIS|doctest.REPORT_ONLY_FIRST_FAILURE)
