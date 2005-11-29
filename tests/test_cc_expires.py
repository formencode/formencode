from formencode.validators import CreditCardExpires, Invalid

ed = CreditCardExpires()

def validate(month, year):
    try:
        ed.validate_python({'ccExpiresMonth': month,
                            'ccExpiresYear': year}, None)
    except Invalid, e:
        return e.unpack_errors()['ccExpiresMonth']

messages = CreditCardExpires._messages

def test_ed():
    assert validate('11', '2250') is None
    assert validate('11', 'test') == messages['notANumber']
    assert validate('test', '2250') == messages['notANumber']
    assert validate('10', '2005') == messages['invalidNumber']
    assert validate('10', '05') == messages['invalidNumber']
