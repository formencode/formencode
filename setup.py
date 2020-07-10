"""FormEncode validates and converts nested structures.

It allows for a declarative form of defining the validation,
and decoupled processes for filling and generating forms.

The official repo is at GitHub: https://github.com/formencode/formencode
"""
from __future__ import absolute_import

import sys
from setuptools import setup, find_packages

version = '2.0.0a1'

if not '2.6' <= sys.version < '3.0' and not '3.2' < sys.version:
    raise ImportError('Python version not supported')

tests_require = ['pycountry',
    'dnspython' if sys.version < '3.0' else 'dnspython3']

doctests = ['docs/htmlfill.txt', 'docs/Validator.txt',
    'formencode/tests/non_empty.txt']

setup(name='FormEncode',
      version=version,
      # requires_python='>=2.6,!=3.0,!=3.1',!=3.2, # PEP345
      description="HTML form validation, generation, and conversion package",
      long_description=__doc__,
      classifiers=[
          "Development Status :: 4 - Beta",
           "Intended Audience :: Developers",
           "License :: OSI Approved :: MIT License",
           "Programming Language :: Python",
           "Programming Language :: Python :: 2",
           "Programming Language :: Python :: 2.6",
           "Programming Language :: Python :: 2.7",
           "Programming Language :: Python :: 3",
           "Programming Language :: Python :: 3.3",
           "Programming Language :: Python :: 3.4",
           "Programming Language :: Python :: 3.5",
           "Topic :: Software Development :: Libraries :: Python Modules",
           ],
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://formencode.org',
      license='MIT',
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      package_data={'formencode': ['../docs/*.txt']},
      test_suite='formencode.tests',
      install_requires=['six'],
      tests_require=tests_require,
      extras_require={'testing': tests_require},
      convert_2to3_doctests=doctests,
    )
