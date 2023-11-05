import os
import sys
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Make sure messages are not translated when running the tests
# (setting the environment variable here may be too late already,
# in this case you must set it manually before running the tests).
os.environ['LANGUAGE'] = 'C'

# Enable deprecation warnings (which are disabled by default)
warnings.simplefilter('default')

try:
    try:
        import importlib.metadata as metadata
        try:
            metadata.distribution("FormEncode")
        except metadata.PackageNotFoundError as error:
            raise ImportError from error
    except ImportError:  # Python < 3.8
        import pkg_resources
        pkg_resources.require('FormEncode')
except ImportError as error:
    raise ImportError("Install FormEncode before running the tests") from error
