from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

version = '0.7.1'

setup(name="FormEncode",
      version=version,
      description="HTML form validation, generation, and conversion package",
      long_description="""\
FormEncode validates and converts nested structures.  It allows for
a declarative form of defining the validation, and decoupled processes
for filling and generating forms.
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
      packages=["formencode", "formencode.util"],
      include_package_data=True,
      extras_require={'testing': ['elementtree']},
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
