# @@: This is experimental

import fields
import pkg_resources
pkg_resources.require('RuleDispatch')
import dispatch

@dispatch.generic()
def makeform(obj, context):
    """
    Return ``(field_obj, Schema)``.
    
    Return a field or field container used to edit ``obj`` given the
    context.  Also return a Schema object (or None for no Schema) that
    will be applied before other validation.
    """
    raise NotImplementedError

