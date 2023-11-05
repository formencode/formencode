"""The formencode package"""

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # Python < 3.8
    from pkg_resources import get_distribution
    from pkg_resources import DistributionNotFound as PackageNotFoundError

    def version(distribution_name):
        return get_distribution(distribution_name).version

from formencode.api import (
    NoDefault, Invalid, Validator, Identity,
    FancyValidator, is_empty, is_validator)
from formencode.schema import Schema
from formencode.compound import CompoundValidator, Any, All, Pipe
from formencode.foreach import ForEach
from formencode import validators
from formencode import national
from formencode.variabledecode import NestedVariables

__all__ = [
    'NoDefault', 'Invalid', 'Validator', 'Identity', 'FancyValidator',
    'is_empty', 'is_validator',
    'Schema', 'CompoundValidator', 'Any', 'All', 'Pipe',
    'ForEach', 'validators', 'national', 'NestedVariables',
    '__version__']

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # package is not installed
    __version__ = 'local-test'
