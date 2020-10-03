from __future__ import absolute_import
# formencode package
from pkg_resources import get_distribution, DistributionNotFound

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
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
     # package is not installed
    __version__ = 'local-test'
