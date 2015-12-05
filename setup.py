"""FormEncode validates and converts nested structures.

It allows for a declarative form of defining the validation,
and decoupled processes for filling and generating forms.

The official repo is at GitHub: https://github.com/formencode/formencode
"""

import sys
from setuptools import setup, find_packages

version = '1.3.0'

if not '2.6' <= sys.version < '3.0' and not '3.2' <= sys.version:
    raise ImportError('Python version not supported')

tests_require = ['nose', 'pycountry',
    'dnspython' if sys.version < '3.0' else 'dnspython3']

doctests = ['docs/htmlfill.txt', 'docs/Validator.txt',
    'formencode/tests/non_empty.txt']

setup(name='FormEncode',
      version=version,
      # requires_python='>=2.6,!=3.0,!=3.1', # PEP345
      description="HTML form validation, generation, and conversion package",
      long_description=__doc__,
      classifiers=[
          "Development Status :: 4 - Beta",
           "Intended Audience :: Developers",
           "License :: OSI Approved :: MIT",
           "Programming Language :: Python",
           "Programming Language :: Python :: 2",
           "Programming Language :: Python :: 3",
           "Topic :: Software Development :: Libraries :: Python Modules",
           ],
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://formencode.org',
      license='PSF',
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      package_data={'formencode': ['../docs/*.txt']},
      test_suite='formencode.tests',
      tests_require=tests_require,
      extras_require={'testing': tests_require},
      use_2to3=True,
      convert_2to3_doctests=doctests,
    )
