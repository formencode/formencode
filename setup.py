"""FormEncode validates and converts nested structures.

It allows for a declarative form of defining the validation,
and decoupled processes for filling and generating forms.

The official repo is at GitHub: https://github.com/formencode/formencode
"""
from __future__ import absolute_import

import sys
from setuptools import setup, find_packages
import platform

if not (2,7) <= sys.version_info[:2] < (3,0) and not (3,6) <= sys.version_info[:2]:
    raise ImportError('Python version not supported')

tests_require = [
    'pytest<4.7' if sys.version_info[:2] < (3,0) else 'pytest',
    'dnspython==1.16.0' if sys.version_info[:2] < (3,0) else 'dnspython>=2.0.0',
    'pycountry<19' if sys.version_info < (3,0) else 'pycountry']

setup_requires = [
    'setuptools_scm<6.0' if sys.version_info[:2] < (3,0) else 'setuptools_scm',
    'setuptools_scm_git_archive',
]

doctests = ['docs/htmlfill.txt', 'docs/Validator.txt',
    'formencode/tests/non_empty.txt']

setup(name='FormEncode',
      # requires_python='>=2.7,!=3.0,!=3.1,!=3.2,!=3.3,!=3.4,!=3.5' # PEP345
      description="HTML form validation, generation, and conversion package",
      long_description=__doc__,
      classifiers=[
          "Development Status :: 4 - Beta",
           "Intended Audience :: Developers",
           "License :: OSI Approved :: MIT License",
           "Programming Language :: Python",
           "Programming Language :: Python :: 2",
           "Programming Language :: Python :: 2.7",
           "Programming Language :: Python :: 3",
           "Programming Language :: Python :: 3.6",
           "Programming Language :: Python :: 3.7",
           "Programming Language :: Python :: 3.8",
           "Programming Language :: Python :: 3.9",
           "Topic :: Software Development :: Libraries :: Python Modules",
           ],
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://formencode.org',
      license='MIT',
      data_files = [("", ["LICENSE.txt"])],
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      package_data={'formencode': ['../docs/*.txt']},
      test_suite='formencode.tests',
      install_requires=['six'],
      tests_require=tests_require,
      use_scm_version=True,
      setup_requires=setup_requires,

      extras_require={'testing': tests_require},
    )
