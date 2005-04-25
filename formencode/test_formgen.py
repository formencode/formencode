try:
    import doctest
    doctest.OutputChecker
except AttributeError:
    import util.doctest24 as doctest
import formgen
import doctest_xml_compare

doctest_xml_compare.install()

if __name__ == '__main__':
    doctest.testmod(formgen)

