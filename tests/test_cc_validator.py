from formencode.validators import CreditCardValidator, Invalid

cc = CreditCardValidator()

def validate(cctype, ccnumber):
    try:
        cc.validate_python({'ccNumber': ccnumber,
                            'ccType': cctype}, None)
    except Invalid, e:
        return e.unpack_errors()['ccNumber']

messages = CreditCardValidator._messages

def test_cc():
    assert validate('visa', '4'+('1'*15)) is None
    assert validate('visa', '5'+('1'*12)) == messages['invalidNumber']
    assert validate('visa', '4'+('1'*11) + '2') == messages['invalidNumber']
    assert validate('visa', 'test') == messages['notANumber']
    assert validate('visa', '4'+('1'*10)) == messages['badLength']
