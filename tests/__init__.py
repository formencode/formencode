import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ['LANGUAGE']= 'C'
import pkg_resources
pkg_resources.require('FormEncode')
