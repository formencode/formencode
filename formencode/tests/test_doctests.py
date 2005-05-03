import os, sys

if __name__ == '__main__':
    base = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(base)
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

from formencode import validators
modules = [validators]

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if not args:
        args = text_files + modules
    for fn in args:
        if isinstance(fn, str):
            fn = os.path.join(base, 
                              'docs', fn)
            doctest.testfile(fn, module_relative=False)
        else:
            doctest.testmod(fn)


