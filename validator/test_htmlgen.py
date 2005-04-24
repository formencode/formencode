from htmlgen import html
import doctest

# A test value that can't be encoded as ascii:
uni_value = u'\xff'

def test_basic():
    output = '<a href="test">hey there</a>'
    assert str(html.a(href='test')('hey there')) == output
    assert str(html.a('hey there')(href='test')) == output
    assert str(html.a(href='test', c='hey there')) == output
    assert str(html.a('hey there', href='test')) == output
    assert str(html.a(href='test')('hey ', 'there')) == output
    assert str(html.a(href='test')(['hey ', 'there'])) == output

def test_compound():
    output = '<b>Hey <i>you</i>!</b>'
    assert str(html.b('Hey ', html.i('you'), '!')) == output
    assert str(html.b()('Hey ')(html.i()('you'))('!')) == output
    inner = html('Hey ', html.i('you'), '!')
    assert html.str(inner) == 'Hey <i>you</i>!'
    assert str(inner) == 'Hey <i>you</i>!'
    assert (repr(inner)
            == "ElementList(['Hey ', <Element '<i>you</i>'>, "
            "'!'])")
    assert str(html.b(inner)) == output

def test_unicode():
    try:
        uni_value.encode('ascii')
    except ValueError:
        pass
    else:
        assert 0, (
            "We need something that can't be ASCII-encoded: %r (%r)"
            % (uni_value, uni_value.encode('ascii')))
    assert (str(html.b(uni_value))
            == ('<b>%s</b>' % uni_value).encode('utf-8'))

def test_quote():
    assert html.quote('<hey>!') == '&lt;hey&gt;!'
    assert html.quote(uni_value) == uni_value.encode('utf-8')
    assert html.quote(None) == ''
    assert html.str(None) == ''
    assert str(html.b('<hey>')) == '<b>&lt;hey&gt;</b>'

def test_comment():
    assert str(html.comment('test')) == '<!-- test -->'
    assert (str(html.comment(uni_value))
            == '<!-- %s -->' % uni_value.encode('utf-8'))
    assert str(html.comment('test')('this')) == '<!-- testthis -->'

def test_none():
    assert html.str(None) == ''
    assert str(html.b(class_=None)('hey')) == '<b>hey</b>'
    assert str(html.b(class_=' ')(None)) == '<b class=" " />'

def test_namespace():
    output = '<b tal:content="options/whatever" />'
    assert str(html.b(**{'tal:content': 'options/whatever'})) == output
    assert str(html.b(tal__content='options/whatever')) == output
    
if __name__ == '__main__':
    # It's like a super-mini py.test...
    for name, value in globals().items():
        if name.startswith('test'):
            print name
            value()
    import htmlgen
    doctest.testmod(htmlgen)
    print 'doctest'
