from __future__ import absolute_import
# formencode package

from formencode.api import (
    NoDefault, Invalid, Validator, Identity,
    FancyValidator, is_empty, is_validator)
from formencode.schema import Schema
from formencode.compound import CompoundValidator, Any, All, Pipe
from formencode.foreach import ForEach
from formencode import validators
from formencode import national
from formencode.variabledecode import NestedVariables

VERSION = (2, 0, '0a1')


def get_version():
    """Return the VERSION as a string e.g: 2.0.0a1"""
    return '.'.join(map(str, VERSION))


__version__ = get_version()
