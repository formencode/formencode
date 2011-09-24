from unittest import TestCase
from nose.tools import assert_equal
from formencode.validators import Email, Invalid


def _validate(validator, *args):
    try:
        return validator.to_python(*args)
    except Invalid, e:
        return str(e)


def test_invalid_email_addresses():
    invalid_usernames = [
            # (email, message_name),
            ('foo\tbar', 'formencode.org', 'badUsername'),
            ('foo\nbar', 'formencode.org', 'badUsername'),
            ('test', '', 'noAt'),
            ('test', 'foobar', 'badDomain'),
            ('test', 'foobar.5', 'badDomain'),
            ('test', 'foo..bar.com', 'badDomain'),
            ('test', '.foo.bar.com', 'badDomain'),
            ('foo,bar', 'formencode.org', 'badUsername'),
    ]

    def expected_message(validator, message_name, username, domain):
        email = '@'.join((username, domain))
        return validator.message(message_name, email, username=username, domain=domain)

    validator = Email()

    for username, domain, message_name in invalid_usernames:
        email = '@'.join(el for el in (username, domain) if el)
        error = _validate(validator, email)
        expected = expected_message(validator, message_name, username, domain)
        yield assert_equal, error, expected


def test_valid_email_addresses():
    valid_email_addresses = [
            # (email address, expected email address),
            (' test@foo.com ', 'test@foo.com'),
            ('nobody@xn--m7r7ml7t24h.com', 'nobody@xn--m7r7ml7t24h.com'),
            ('o*reilly@test.com', 'o*reilly@test.com'),
            ('foo+bar@example.com', 'foo+bar@example.com'),
            ('foo.bar@example.com', 'foo.bar@example.com'),
            ('foo!bar@example.com', 'foo!bar@example.com'),
            ('foo{bar}@example.com', 'foo{bar}@example.com'),

            # examples from RFC 3696
            #   punting on the difficult and extremely uncommon ones
            #('"Abc\@def"@example.com', '"Abc\@def"@example.com'),
            #('"Fred Bloggs"@example.com', '"Fred Bloggs"@example.com'),
            #('"Joe\\Blow"@example.com', '"Joe\\Blow"@example.com'),
            #('"Abc@def"@example.com', '"Abc@def"@example.com'),
            ('customer/department=shipping@example.com',
                'customer/department=shipping@example.com'),
            ('$A12345@example.com', '$A12345@example.com'),
            ('!def!xyz%abc@example.com', '!def!xyz%abc@example.com'),
            ('_somename@example.com', '_somename@example.com'),
    ]

    def expected_message(validator, message_name, username, domain):
        email = '@'.join((username, domain))
        return validator.message(message_name, email, username=username, domain=domain)

    validator = Email()

    for email, expected in valid_email_addresses:
        yield assert_equal, _validate(validator, email), expected
