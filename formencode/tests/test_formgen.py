try:
    import doctest
    doctest.OutputChecker
except AttributeError:
    import formencode.util.doctest24 as doctest
from formencode import formgen
from formencode import doctest_xml_compare

doctest_xml_compare.install()

if __name__ == '__main__':
    doctest.testmod(formgen)

