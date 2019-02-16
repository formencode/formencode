from __future__ import absolute_import
import os
import sys
import doctest

from formencode import compound
from formencode import htmlfill
from formencode import htmlgen
from formencode import national
from formencode import schema
from formencode import validators
import six


"""Modules that will have their doctests tested."""
modules = [compound, htmlfill, htmlgen, national, schema, validators]


"""Text files that will have their doctests tested."""
text_files = [
    'docs/htmlfill.txt',
    'docs/Validator.txt',
    'formencode/tests/non_empty.txt',
    ]


"""Used to resolve text files to absolute paths."""
base = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


if six.text_type is str:  # Python 3

    OutputChecker = doctest.OutputChecker

    class OutputChecker3(OutputChecker):

        def check_output(self, want, got, optionflags):
            if want.startswith("u'"):
                want = want[1:]
            elif want.startswith('set(['):
                want = want[3:].replace(
                    '([', '{').replace('])', '}').replace('{}', 'set()')
            return OutputChecker.check_output(self, want, got, optionflags)

    doctest.OutputChecker = OutputChecker3


def doctest_file(document, verbose, raise_error):
    failure_count, test_count = doctest.testfile(document,
            module_relative=False,
            optionflags=doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL,
            verbose=verbose)
    if raise_error:
        assert test_count > 0
        assert failure_count == 0


def doctest_module(document, verbose, raise_error):
    failure_count, test_count = doctest.testmod(document,
            optionflags=doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL,
            verbose=verbose)
    if raise_error:
        assert test_count > 0
        assert failure_count == 0


def test_doctests():
    """Generate each doctest."""
    for suite in suites():
        for test in suite._tests:
            yield test


def suites():
    prefix_len = len(os.path.dirname(base)) + 1
    for document in text_files + modules:
        if isinstance(document, str):
            if not document.startswith(os.sep):
                document = os.path.join(base, document)
            suite = doctest.DocFileSuite(
                document,
                module_relative=False,
                optionflags=doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL,
            )
            filename = document[prefix_len:]
            for test in suite._tests:
                dt_test = test._dt_test
                test.description = 'doctest.file:%s:%s (%d example%s)' % (
                    filename, dt_test.lineno, len(dt_test.examples),
                    's' if len(dt_test.examples) > 0 else ''
                )
        else:
            suite = doctest.DocTestSuite(
                document,
                optionflags=doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL,
            )
            filename = document.__file__[prefix_len:]
            for test in suite._tests:
                dt_test = test._dt_test
                test.description = 'doctest.module:%s %s:%s (%d example%s)' % (
                    dt_test.name,
                    filename, dt_test.lineno, len(dt_test.examples),
                    's' if len(dt_test.examples) > 0 else ''
                )

        yield suite


if __name__ == '__main__':
    # Call this file directly if you want to test doctests.
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
