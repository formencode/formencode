from datatest import TestCase as DataTestCase
from datatest.util.dictdiff import dictcompareError
from datatest.util.htmldiff import htmlcompareError
import cgi
import re

_exceptionLeaderRE = re.compile('^[a-zA-Z][a-zA-Z0-9\_]*:')

class TestCase(DataTestCase):

    def cgi_parse(self, queryString):
        """
        Parses a query string and returns the usually dictionary.
        """
        d = {}
        for key, value in cgi.parse_qsl(queryString, 1):
            if d.has_key(key):
                if isinstance(d[key], list):
                    d[key].append(value)
                else:
                    d[key] = [d[key], value]
            else:
                d[key] = value
        return d

    def assert_dict_equal(self, d1, d2):
        v = dictcompareError(d1, d2)
        assert not v, '\n' + v

    def assert_html_equal(self, h1, h2):
        v = htmlcompareError(h1, h2)
        assert not v, '\n' + v

    def assertRaises(self, exception, func, *args, **kw):
        try:
            func(*args, **kw)
        except Exception, e:
            if exception is None:
                return
            elif isinstance(exception, str):
                match = _exceptionLeaderRE.search(exception)
                if match:
                    clsMatch = match.group(0)[:-1]
                    exception = exception[match.end()+1:].strip()
                    if not clsMatch == e.__class__.__name__:
                        raise
                exception = re.escape(exception).replace('\\*', '.*?')
                regex = re.compile('^%s$' % exception, re.I)
                if not regex.search(str(e)):
                    raise
            else:
                if not isinstance(e, exception):
                    raise
        else:
            assert False, "Exception %s expected" % exception

