import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pkg_resources
try:
    import elementtree
except ImportError:
    pkg_resources.require('FormEncode[testing]')
