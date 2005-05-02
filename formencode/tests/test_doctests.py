import os, sys
try:
    import formencode
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(
        os.path.dirname(__file__))))
try:
    import doctest
    doctest.OutputChecker
except AttributeError:
    import formencode.util.doctest24 as doctest

from formencode import doctest_xml_compare

doctest_xml_compare.install()

text_files = [
    'htmlfill.txt',
    'Validator.txt',
    ]

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if not args:
        args = text_files
    for fn in args:
        fn = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                          'docs', fn)
        doctest.testfile(fn, module_relative=False)

