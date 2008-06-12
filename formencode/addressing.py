import re
import string
from api import FancyValidator, _
from validators import Regex, Invalid, PostalCode

# @todo     utilize pycountry
from dbmanager.util.i18n import get_country, get_countries

class GermanPostalCode(Regex):

    """
    German Postal codes (aka Zip Codes).

    ::

        >>> GermanPostalCode.to_python('55555')
        '55555'
        >>> GermanPostalCode.to_python('5555')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a zip code (5 digits)
    """

    regex = r'^\d\d\d\d\d$'
    strip = True

    messages = {
        'invalid': _("Please enter a zip code (%s)") % _("5 digits"),
        }

class FourDigitsPostalCode(Regex):

    """
    Postal codes consisting of 4 digits.

    ::

        >>> FourDigitsPostalCode.to_python('5555')
        '5555'
        >>> FourDigitsPostalCode.to_python('56655')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a zip code (4 digits)
    """

    regex = r'^\d\d\d\d$'
    strip = True

    messages = {
        'invalid': _("Please enter a zip code (%s)") % _("4 digits"),
        }

class PolishPostalCode(Regex):

    """
    Polish Postal codes (aka Zip Codes).

    ::

        >>> PolishPostalCode.to_python('55555')
        '55-555'
        >>> PolishPostalCode.to_python('55-555')
        '55-555'
        >>> PolishPostalCode.to_python('5555')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a zip code (5 digits)
    """

    regex = re.compile(r'^(\d\d)\-?(\d\d\d)$')
    strip = True

    messages = {
        'invalid': _("Please enter a zip code (%s)") % _("5 digits"),
        }

    def _to_python(self, value, state):
        self.assert_string(value, state)
        match = self.regex.search(value)
        if not match:
            raise Invalid(
                self.message('invalid', state),
                value, state)
        return '%s-%s' % (match.group(1), match.group(2))

class ArgentinianPostalCode(Regex):

    """
    Argentinian Postal codes.

    ::

        >>> ArgentinianPostalCode.to_python('C1070AAM')
        'C1070AAM'
        >>> ArgentinianPostalCode.to_python('c 1070 aam')
        'C1070AAM'
        >>> ArgentinianPostalCode.to_python('5555')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a valid postal code (CNNNNCCC)
    """

    regex = re.compile(r'^([a-zA-Z]{1})\s*(\d{4})\s*([a-zA-Z]{3})$')
    strip = True

    messages = {
        'invalid': _("Please enter a zip code (%s)") % _("CNNNNCCC"),
        }

    def _to_python(self, value, state):
        self.assert_string(value, state)
        match = self.regex.search(value)
        if not match:
            raise Invalid(
                self.message('invalid', state),
                value, state)
        return '%s%s%s' % (match.group(1).upper(),
                           match.group(2),
                           match.group(3).upper())

class CanadianPostalCode(Regex):

    """
    Canadian Postal codes.

    ::

        >>> CanadianPostalCode.to_python('V3H 1Z7')
        'V3H 1Z7'
        >>> CanadianPostalCode.to_python('v3h1z7')
        'V3H 1Z7'
        >>> CanadianPostalCode.to_python('5555')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a valid postal code (CNC NCN)
    """

    regex = re.compile(r'^([a-zA-Z]\d[a-zA-Z])\s?(\d[a-zA-Z]\d)$')
    strip = True

    messages = {
        'invalid': _("Please enter a zip code (%s)") % _("CNC NCN"),
        }

    def _to_python(self, value, state):
        self.assert_string(value, state)
        match = self.regex.search(value)
        if not match:
            raise Invalid(
                self.message('invalid', state),
                value, state)
        return '%s %s' % (match.group(1).upper(), match.group(2).upper())

class UKPostalCode(Regex):

    """
    UK Postal codes. Please see BS 7666.

    ::

        >>> UKPostalCode.to_python('BFPO 3')
        'BFPO 3'
        >>> UKPostalCode.to_python('LE11 3GR')
        'LE11 3GR'
        >>> UKPostalCode.to_python('l1a 3gr')
        'L1A 3GR'
        >>> UKPostalCode.to_python('5555')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a valid postal code (for format see BS 7666)
    """

    regex = re.compile(r'^((ASCN|BBND|BIQQ|FIQQ|PCRN|SIQQ|STHL|TDCU|TKCA) 1ZZ|BFPO (c\/o )?[1-9]{1,4}|GIR 0AA|[A-PR-UWYZ]([0-9]{1,2}|([A-HK-Y][0-9]|[A-HK-Y][0-9]([0-9]|[ABEHMNPRV-Y]))|[0-9][A-HJKS-UW]) [0-9][ABD-HJLNP-UW-Z]{2})$')
    strip = True

    messages = {
        'invalid': _("Please enter a valid postal code (for format see BS 7666)"),
        }

    def _to_python(self, value, state):
        self.assert_string(value, state)
        match = self.regex.search(value)
        if not match:
            raise Invalid(
                self.message('invalid', state),
                value, state)
        return match.group(1).upper()

class CountryValidator(FancyValidator):

    key_ok = True

    messages = {
        'valueNotFound': _("That country is not listed in ISO-3166"),
        }

    def _to_python(self, value, state):
        upval = value.upper()
        if self.key_ok:
            try:
                c = get_country(upval)
                return upval
            except:
                pass
        for k, v in get_countries():
            if v.upper() == upval:
                return k
        raise Invalid(self.message('valueNotFound', state), value, state)

    def _from_python(self, value, state):
        try:
            return get_country(value.upper())
        except KeyError:
            return value

class PostalCodeInCountryFormat(FancyValidator):
    """
    Makes sure the postal code is in the country's format.
    """

    messages = {
        'badFormat': _("Given postal code does not match the country's format."),
        }
    _vd = {
        'DE': GermanPostalCode,
        'AT': FourDigitsPostalCode,
        'BE': FourDigitsPostalCode,
        'DK': FourDigitsPostalCode,
        'PL': PolishPostalCode,
        'US': PostalCode,
        'CA': CanadianPostalCode,
        'AR': ArgentinianPostalCode,
        'GB': UKPostalCode,
    }

    def validate_python(self, fields_dict, state):
        if fields_dict['country'] in self._vd:
            try:
                fields_dict['zip'] = self._vd[fields_dict['country']].to_python(fields_dict['zip'])
            except Invalid, e:
                message = self.message('badFormat', state)
                raise Invalid(message, fields_dict, state,
                              error_dict = {'zip' : e.message,
                                            'country': message})
