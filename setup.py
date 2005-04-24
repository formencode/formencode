from distutils.core import setup
import warnings
warnings.filterwarnings("ignore", "Unknown distribution option")

import sys
# patch distutils if it can't cope with the "classifiers" keyword
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(name="Validator",
      version="0.1",
      description="Validation and Convertion package",
      long_description="""\
Validator validates and converts nested structures.  It allows for
a declarative form of defining the validation, and hooks for all
aspects.
""",
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Ian Bicking",
      author_email="ianb@colorstudy.com",
      url="http://colorstudy.com/svn/trunk/Validators/",
      license="PSF",
      packages=["validator"],
      download_url="@@",
      )

# Send announce to:
#   python-announce@python.org
#   python-list@python.org
