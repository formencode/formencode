import sys
from setuptools import setup

version = '1.2.2'

tests_require = ['nose']
if sys.version < '2.5':
    tests_require.append('elementtree')

setup(name="FormEncode",
      version=version,
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
      tests_require=tests_require
      )

# Send announce to:
#   python-announce@python.org
#   web-sig@python.org
#   formencode-discuss@lists.sf.net
#   turbogears@googlegroups.com
#   subway-devel@googlegroups.com

# Announcement template:
"""

What is it?
-----------

FormEncode is a package for form validation and conversion.  It also includes modules for parsing, filling, and extracting metadata from HTML forms.  It features robust conversion both of incoming and outgoing data, attention paid to helpful error messages, and a wide variety of pre-build validators.  It also supports composition of validators, and validating structured data, including nested and repeating form elements.

FormEncode is being used in several projects, including Subway, TurboGears, and SQLObject.

Where is it?
------------

Website and docs:
  http://formencode.org
Download:
  http://cheeseshop.python.org/pypi/FormEncode

"""
