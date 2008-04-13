"""
Experimental extensible form generation
"""

# @@: This is experimental
import warnings
warnings.warn("formencode.formgen is deprecated with no replacement; "
              "if you are using it please maintain your own copy of this "
              "file", DeprecationWarning, 2)

import fields

dispatch = None
try:
    import pkg_resources
    pkg_resources.require('RuleDispatch')
    import dispatch
except (ImportError, pkg_resources.DistributionNotFound):
    pass

if dispatch:
    #@dispatch.generic()
    def makeform(obj, context):
        """
        Return ``(field_obj, Schema)``.

        Return a field or field container used to edit ``obj`` given the
        context.  Also return a Schema object (or None for no Schema) that
        will be applied before other validation.
        """
        raise NotImplementedError

    makeform = dispatch.generic()(makeform)

