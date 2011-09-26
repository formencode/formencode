import os
import sys

from formencode import validators
from formencode import schema
from formencode import compound
from formencode import doctest_xml_compare


modules = [validators, schema, compound]
" Modules that will have their doctests tested. "


text_files = [
    'docs/htmlfill.txt',
    'docs/Validator.txt',
    'tests/non_empty.txt',
    ]
" Text files that will have their doctests tested. "


base = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
" Used to resolve text files to absolute paths. """


try:
    import doctest
    doctest.OutputChecker
except (AttributeError, ImportError): # Python < 2.4
    import util.doctest24 as doctest


#
#TODO Put this in setup/teardown.
# Or better yet, find a way to do this with the newer doctest API.
# Patches doctest.OutputChecker with our own OutputChecker.
#
#doctest_xml_compare.install()


def doctest_file(document, verbose, raise_error):
    (failure_count, test_count) = doctest.testfile(document,
            module_relative=False, optionflags=doctest.ELLIPSIS,
            verbose=verbose)
    if raise_error:
        assert failure_count == 0


def doctest_module(document, verbose, raise_error):
    (failure_count, test_count) = doctest.testmod(document,
            optionflags=doctest.ELLIPSIS, verbose=verbose)
    if raise_error:
        assert failure_count == 0


def set_func_description(fn, description):
    """ Wrap function and set description attr for nosetests to display. """
    def _wrapper(*a_test_args):
        fn(*a_test_args)
    _wrapper.description = description
    return _wrapper


def test_doctests():
    """ Generate each doctest. """
    #TODO Can we resolve this from nose?
    verbose = False
    raise_error = True
    for document in text_files + modules:
        if isinstance(document, str):
            name = "Doctests for %s" % (document,)
            if not document.startswith(os.sep):
                document = os.path.join(base, document)
            yield set_func_description(doctest_file, name), document, \
                     verbose, raise_error
        else:
            name = "Doctests for %s" % (document.__name__,)
            yield set_func_description(doctest_module, name), document, \
                    verbose, raise_error


if __name__ == '__main__':
    # Call this file directly if you want to test doctests with the xml_compare
    # monkey patch.
    args = sys.argv[1:]
    verbose = False
    if '-v' in args:
        args.remove('-v')
        verbose = True
    if not args:
        args = text_files + modules
    raise_error = False
    for fn in args:
        if isinstance(fn, str):
            fn = os.path.join(base, fn)
            doctest_file(fn, verbose, raise_error)
        else:
            doctest_module(fn, verbose, raise_error)
