from __future__ import absolute_import
# formencode package
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from pkg_resources import get_distribution
    from pkg_resources import DistributionNotFound as PackageNotFoundError
    def version(pkg):
        return get_distribution(__name__).version

from formencode.api import (
    NoDefault, Invalid, Validator, Identity,
    FancyValidator, is_empty, is_validator)
from formencode.schema import Schema
from formencode.compound import CompoundValidator, Any, All, Pipe
from formencode.foreach import ForEach
from formencode import validators
from formencode import national
from formencode.variabledecode import NestedVariables

try:
    __version__ = version(__name__)
except DistributionNotFound:
     # package is not installed
    __version__ = 'local-test'
