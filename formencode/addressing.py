import re
import string
from gettext import gettext as _
from formencode.api import FancyValidator
from formencode.validators import Regex, Invalid
from turbogears import identity

from dbmanager.util.i18n import *
from dbmanager.util.hurrikane import *

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

class LanguageValidator(FancyValidator):

    key_ok = True

    messages = {
        'valueNotFound': _("That language is not listed in ISO-639-2"),
        }

    def _to_python(self, value, state):
        upval = value.upper()
        if self.key_ok:
            try:
                c = get_language(value)
                return value
            except:
                pass
        for k, v in get_languages():
            if v.upper() == upval:
                return k
        raise Invalid(self.message('valueNotFound', state), value, state)

    def _from_python(self, value, state):
        try:
            return get_language(value.lower())
        except KeyError:
            return value

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
    from formencode.validators import PostalCode

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

class HsysRegionCompletor(FancyValidator):
    """
    Will add missing region information if possible.
    Does utilize services of Hurrikane Systems GIS.
    """

    def validate_python(self, fields_dict, state):
        try:
            queryable_countries = geo_countries_for_zip_info()
        except (ValueError, HurrikaneException):
            return
        if fields_dict['country'] in queryable_countries \
           and fields_dict['zip'] \
           and not fields_dict['region']:
            try:
                result = geo_get_zip_info(fields_dict['country'], fields_dict['zip'])
                fields_dict['region'] = result['Administrative_Name']
            except HurrikaneException, e:
                try:
                    fields_dict['region'] = geo_estimate_region(fields_dict['country'], fields_dict['zip'])
                except HurrikaneException, e:
                    pass
            except:
                # log warning
                pass

class PhoneNumber(FancyValidator):

    """
    Validates, and converts phone numbers to +##-###-#######.
    Adapted from RFC 3966

    ::

        >>> p = PhoneNumber()
        >>> p.to_python('333-3333')
        Traceback (most recent call last):
            ...
        Invalid: Please enter a number, with area code, in the form +##-###-####...
        >>> p.to_python('0555/4860-300')
        '+49-555-4860-300'
        >>> p.to_python('0555-49924-51')
        '+49-555-49924-51'
        >>> p.to_python('0555 / 8114100')
        '+49-555-8114100'
        >>> p.to_python('0555/8114100')
        '+49-555-8114100'
        >>> p.to_python('0555 8114100')
        '+49-555-8114100'
        >>> p.to_python(' +49 (0)555 350 60 0')
        '+49-555-35060-0'
        >>> p.to_python('+49 555 350600')
        '+49-555-350600'
        >>> p.to_python('0049/ 555/ 871 82 96')
        '+49-555-87182-96'
        >>> p.to_python('0555-2 50-30')
        '+49-555-250-30'
        >>> p.to_python('0555 43-1200')
        '+49-555-43-1200'
        >>> p.to_python('(05 55)4 94 33 47')
        '+49-555-49433-47'
        >>> p.to_python('(00 48-555)2 31 72 41')
        '+48-555-23172-41'
        >>> p.to_python('+973-555431')
        '+973-555431'
        >>> p.to_python('1-393-555-3939')
        '+1-393-555-3939'
        >>> p.to_python('+43 (1) 55528/0')
        '+43-1-55528-0'
        >>> p.to_python('+43 5555 429 62-0')
        '+43-5555-42962-0'
        >>> p.to_python('00 218 55 33 50 317 321')
        '+218-55-3350317-321'
        >>> p.to_python('+218 (0)55-3636639/38')
        '+218-55-3636639-38'
        >>> p.to_python('032 555555 367')
        '+49-32-555555-367'
        >>> p.to_python('(+86) 555 3876693')
        '+86-555-3876693'
        >>> p.to_python('(0 81 52)93 11 22')
        '+49-8152-9311-22'
    """

    strip = True
    # Use if there's a default country code you want to use:
    default_cc = 49
    _mark_chars_re = re.compile(r"[_.!~*'/?]")
    _preTransformations = [
        (re.compile(r'^(\(?)(?:00\s*)(.+)$'), '%s+%s'),
        (re.compile(r'^\(\s*(\+?\d+)\s*(\d+)\s*\)(.+)$'), '(%s%s)%s'),
        (re.compile(r'^\((\+?[-\d]+)\)\s?(\d.+)$'), '%s-%s'),
        (re.compile(r'^(?:1-)(\d+.+)$'), '+1-%s'),
        (re.compile(r'^(\+\d+)\s+\(0\)\s*(\d+.+)$'), '%s-%s'),
        (re.compile(r'^([0+]\d+)[-\s](\d+)$'), '%s-%s'),
        (re.compile(r'^([0+]\d+)[-\s](\d+)[-\s](\d+)$'), '%s-%s-%s'),
        ]
    _ccIncluder = [
        (re.compile(r'^\(?0([1-9]\d*)[-)](\d.*)$'), '+%d-%s-%s'),
        ]
    _postTransformations = [
        (re.compile(r'^(\+\d+)[-\s]\(?(\d+)\)?[-\s](\d+.+)$'), '%s-%s-%s'),
        (re.compile(r'^(.+)\s(\d+)$'), '%s-%s'),
        ]
    _phoneIsSane = re.compile(r'^(\+[1-9]\d*)-([\d\-]+)$')

    messages = {
        'phoneFormat': _("Please enter a number, with area code, in the form %s") % '+##-###-####...',
        }

    def _perform_rex_transformation(self, value, transformations):
        for rex, trf in transformations:
            match = rex.search(value)
            if match:
                value = trf % match.groups()
        return value

    def _prepend_country_code(self, value, transformations, country_code):
        for rex, trf in transformations:
            match = rex.search(value)
            if match:
                return trf % ((country_code,)+match.groups())
        return value

    def _to_python(self, value, state):
        self.assert_string(value, state)
        try:
            value = value.encode('ascii', 'replace')
        except:
            raise Invalid(self.message('phoneFormat', state), value, state)
        value = self._mark_chars_re.sub('-', value)
        for f, t in [('  ', ' '), ('--', '-'), (' - ', '-'), ('- ', '-'), (' -', '-')]:
            value = value.replace(f, t)
        value = self._perform_rex_transformation(value, self._preTransformations)
        try:
            value = self._prepend_country_code(value, self._ccIncluder, identity.current.user.phone_cc)
        except:
            value = self._prepend_country_code(value, self._ccIncluder, self.default_cc)
        value = self._perform_rex_transformation(value, self._postTransformations)
        value = value.replace(' ', '')
        # did we successfully transform that phone number? Thus, is it valid?
        if not self._phoneIsSane.search(value):
            raise Invalid(self.message('phoneFormat', state), value, state)
        return value
