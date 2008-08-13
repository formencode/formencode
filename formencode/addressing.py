import re
import string
from api import FancyValidator
from validators import Regex, Invalid, PostalCode, _

try:
    import pycountry
    has_pycountry = True
except:
    has_pycountry = False
try:
    from turbogears.i18n import format as tgformat
    has_turbogears = True
except:
    has_turbogears = False

############################################################
## country lists and functions
############################################################
country_additions = [
    ('BY', _("Belarus")),
    ('ME', _("Montenegro")),
    ('AU', _("Tasmania")),
]
fuzzy_countrynames = [
    ('US', 'U.S.A'),
    ('US', 'USA'),
    ('GB', _("Britain")),
    ('GB', _("Great Britain")),
    ('CI', _("Cote de Ivoire")),
]

if has_pycountry:
    # @@ mark: interestingly, common gettext notation does not work here
    import gettext
    gettext.bindtextdomain('iso3166', pycountry.LOCALES_DIR)
    _c = lambda t: gettext.dgettext('iso3166', t)

    def get_countries():
        c1 = set([(e.alpha2, _c(e.name)) for e in pycountry.countries])
        ret = c1.union([(e.alpha2, e.name) for e in pycountry.countries ]
                        + country_additions + fuzzy_countrynames)
        return ret

    def get_country(code):
        return _c(pycountry.countries.get(alpha2=code).name)
elif has_turbogears:
    def get_countries():
        c1 = tgformat.get_countries('en')
        c2 = tgformat.get_countries()
        if len(c1) > len(c2):
            d = dict(country_additions)
            d.update(dict(c1))
            d.update(dict(c2))
        else:
            d = country_additions.copy()
            d.update(dict(c2))
        ret = d.items() + fuzzy_countrynames
        return ret

    def get_country(code):
        return dict(get_countries())[code]
else:
    from warnings import warn
    warn('Please easy_install pycountry or validators handling country names will not work.', DeprecationWarning)
#endif

############################################################
## Postal Code validators
############################################################

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
        Invalid: Please enter a zip code (CNNNNCCC)
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
        Invalid: Please enter a zip code (CNC NCN)
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

    regex = re.compile(r'^((ASCN|BBND|BIQQ|FIQQ|PCRN|SIQQ|STHL|TDCU|TKCA) 1ZZ|BFPO (c\/o )?[1-9]{1,4}|GIR 0AA|[A-PR-UWYZ]([0-9]{1,2}|([A-HK-Y][0-9]|[A-HK-Y][0-9]([0-9]|[ABEHMNPRV-Y]))|[0-9][A-HJKS-UW]) [0-9][ABD-HJLNP-UW-Z]{2})$', re.I)
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
    """
    Will convert a country's name into its ISO-3166 abbreviation for unified
    storage in databases etc. and return a localized country name in the
    reverse step.

    @See http://www.iso.org/iso/country_codes/iso_3166_code_lists.htm

    ::

        >>> CountryValidator.to_python('Germany')
        'DE'
        >>> CountryValidator.to_python('Finland')
        'FI'
        >>> CountryValidator.to_python('UNITED STATES')
        'US'
        >>> CountryValidator.to_python('Krakovia')
        Traceback (most recent call last):
            ...
        Invalid: That country is not listed in ISO-3166
        >>> CountryValidator.from_python('DE')
        'Germany'
        >>> CountryValidator.from_python('FI')
        'Finland'
    """

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
