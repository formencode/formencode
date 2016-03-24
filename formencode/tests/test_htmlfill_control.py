from __future__ import absolute_import
from formencode import htmlfill


# ==============================================================================


def test_defaults_legacy():
    html = """
<input type="text" name="foo" value="bar" />
<input type="text" name="foo" value="biz" />
<input type="text" name="foo" value="bash" />
"""
    expected_html = """
<input type="text" name="foo" value="bang" />
<input type="text" name="foo" value="bang" />
<input type="text" name="foo" value="bang" />
"""
    rendered_html = htmlfill.render(html, defaults={"foo": "bang"},
                                    force_defaults=True)
    assert expected_html == rendered_html


def test_defaults_attr_ignore():
    html = """
<input type="text" name="foo" value="bar" data-formencode-ignore="1" />
<input type="text" name="foo" value="" />
<input type="text" name="foo" value="bash" data-formencode-ignore="1" />
<input type="text" name="foo" value="bash" data-formencode-ignore="" />
<input type="text" name="foo" value="bash" data-formencode-ignore />
"""
    expected_html = """
<input type="text" name="foo" value="bar" data-formencode-ignore="1" />
<input type="text" name="foo" value="bang" />
<input type="text" name="foo" value="bash" data-formencode-ignore="1" />
<input type="text" name="foo" value="bash" data-formencode-ignore="" />
<input type="text" name="foo" value="bash" data-formencode-ignore />
"""
    rendered_html = htmlfill.render(html, defaults={"foo": "bang"},
                                    force_defaults=True,
                                    data_formencode_ignore=True)
    assert expected_html == rendered_html


def test_defaults_attr_form():
    html = """
<input type="text" name="foo" value="bar" data-formencode-form="a" />
<input type="text" name="foo" value="" data-formencode-form="b" />
<input type="text" name="foo" value="bash" data-formencode-form="c" />
"""
    expected_html = """
<input type="text" name="foo" value="bar" data-formencode-form="a" />
<input type="text" name="foo" value="bang" data-formencode-form="b" />
<input type="text" name="foo" value="bash" data-formencode-form="c" />
"""
    rendered_html = htmlfill.render(html, defaults={"foo": "bang"},
                                    force_defaults=True,
                                    data_formencode_form="b",)
    assert expected_html == rendered_html


# ==============================================================================

def test_error_legacy():
    html = """
<input type="text" name="foo" value="bar" />
<input type="text" name="foo" value="biz" />
<input type="text" name="foo" value="bash" />
"""
    expected_html = """
<!-- for: foo -->
<span class="error-message">bang</span><br />
<input type="text" name="foo" value="" class="error" />
<input type="text" name="foo" value="" class="error" />
<input type="text" name="foo" value="" class="error" />
"""
    rendered_html = htmlfill.render(html, errors={"foo": "bang"},
                                    prefix_error=True)
    assert expected_html == rendered_html


def test_error_attr_ignore():
    html = """
<input type="text" name="foo" value="bar" data-formencode-form="a" />
<input type="text" name="foo" value="biz" data-formencode-form="b" />
<input type="text" name="foo" value="bash" data-formencode-form="c" />
"""
    expected_html = """
<input type="text" name="foo" value="bar" data-formencode-form="a" />
<!-- for: foo -->
<span class="error-message">bang</span><br />
<input type="text" name="foo" value="" data-formencode-form="b" class="error" />
<input type="text" name="foo" value="bash" data-formencode-form="c" />
"""
    rendered_html = htmlfill.render(html, errors={"foo": "bang"},
                                    force_defaults=True,
                                    data_formencode_form="b",)


def test_error_attr_form():
    html = """
<input type="text" name="foo" value="bar" data-formencode-form="a" />
<input type="text" name="foo" value="" data-formencode-form="b" />
<input type="text" name="foo" value="bash" data-formencode-form="c" />
"""
    expected_html = """
<input type="text" name="foo" value="bar" data-formencode-form="a" />
<!-- for: foo -->
<span class="error-message">bang</span><br />
<input type="text" name="foo" value="" data-formencode-form="b" class="error" />
<input type="text" name="foo" value="bash" data-formencode-form="c" />
"""
    rendered_html = htmlfill.render(html, errors={"foo": "bang"},
                                    force_defaults=True,
                                    data_formencode_form="b",)
    assert expected_html == rendered_html


def test_error_attr_form_alt():
    """note that formencode doesn't keep an indent on the replacement
        mixes concepts
        note a few things:
            1. we expect a leading "<!-- for: apple -->" block, because we are ignoring that tag
            1. we expect the leading "<!-- for: apple -->" block to not have an initial newline (\n)
    """
    html = """
<form data-formencode-form="a">
    <input type="text" name="bar" value="foo" data-formencode-form="a" />
    <input type="text" name="foo" value="bar" data-formencode-form="a" />
</form>
<form data-formencode-form="b">
    <input type="text" name="bar" value="foo" data-formencode-form="b" />
    <input type="text" name="foo" value="" data-formencode-form="b" />
</form>
<form data-formencode-form="c">
    <input type="text" name="bar" value="foo" data-formencode-form="c" />
    <input type="text" name="foo" value="bash" data-formencode-form="c" />
    <input type="text" name="apple" value="pear" data-formencode-form="c" data-formencode-ignore="1" />
</form>
"""
    expected_html = """<!-- for: apple -->
<span class="error-message">orange</span><br />

<form data-formencode-form="a">
    <input type="text" name="bar" value="foo" data-formencode-form="a" />
    <input type="text" name="foo" value="bar" data-formencode-form="a" />
</form>
<form data-formencode-form="b">
    <input type="text" name="bar" value="foo" data-formencode-form="b" />
    <input type="text" name="foo" value="" data-formencode-form="b" />
</form>
<form data-formencode-form="c">
    <input type="text" name="bar" value="bang" data-formencode-form="c" />
    <!-- for: foo -->
<span class="error-message">bang</span><br />
<input type="text" name="foo" value="" data-formencode-form="c" class="error" />
    <input type="text" name="apple" value="pear" data-formencode-form="c" data-formencode-ignore="1" />
</form>
"""
    rendered_html = htmlfill.render(html, defaults={"bar": "bang"},
                                    errors={"foo": "bang", "apple": "orange"},
                                    force_defaults=True,
                                    data_formencode_form="c",
                                    data_formencode_ignore=True,
                                    )
    assert expected_html == rendered_html


if __name__ == '__main__':
    test_defaults_legacy()
    test_defaults_attr_ignore()
    test_defaults_attr_form()

    test_error_legacy()
    test_error_attr_ignore()
    test_error_attr_form()
    test_error_attr_form_alt()
    