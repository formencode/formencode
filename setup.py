import sys
from setuptools import setup

version = '1.2.4'

if not '2.3' <= sys.version < '3.0':
    raise ImportError('Python version not supported')

tests_require = ['nose', 'pycountry', 'pyDNS']
if sys.version < '2.5':
    tests_require.append('elementtree')

setup(name="FormEncode",
      version=version,
      #requires_python=]'>=2.3,<3', # PEP345
      description="HTML form validation, generation, and conversion package",
      long_description="""\
FormEncode validates and converts nested structures.  It allows for
a declarative form of defining the validation, and decoupled processes
for filling and generating forms.

It has a `subversion repository
<http://svn.formencode.org/FormEncode/trunk#egg=FormEncode-dev>`_ that
you can install from with ``easy_install FormEncode==dev``
""",
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Ian Bicking",
      author_email="ianb@colorstudy.com",
      url="http://formencode.org",
      license="PSF",
      zip_safe=False,
      packages=["formencode", "formencode.util"],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=tests_require,
      )
