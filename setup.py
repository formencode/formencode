from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

setup(name="FormEncode",
      version="0.1",
      description="HTML form validation, generation, and convertion package",
      long_description="""\
FormEncode validates and converts nested structures.  It allows for
a declarative form of defining the validation, and decoupled processes
for filling and generating forms.
""",
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Ian Bicking",
      author_email="ianb@colorstudy.com",
      url="http://svn.colorstudy.com/Formencode/trunk",
      license="PSF",
      packages=["formencode", "formencode.util"],
      package_data={'formencode': ['javascript/*']},
      download_url="@@",
      extras_require={'testing': ['elementtree']},
      )

# Send announce to:
#   python-announce@python.org
#   python-list@python.org
