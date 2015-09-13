FormEncode
==========

.. image:: https://secure.travis-ci.org/formencode/formencode.png?branch=master
   :target: https://travis-ci.org/formencode/formencode
   :alt: Travis CI continuous integration status


Introduction
------------

FormEncode is a validation and form generation package.  The
validation can be used separately from the form generation.  The
validation works on compound data structures, with all parts being
nestable.  It is separate from HTTP or any other input mechanism.


Documentation
-------------

The latest documentation is available at http://www.formencode.org/


Testing
-------

Use `python setup.py nosetests` to run the test suite.
Use `tox` to run the test suite for all supported Python versions.


Changes
-------

Added a validator that can require one or more fields based on the value of another field.

A German howto can be found here: http://techblog.auf-nach-mallorca.info/2014/08/19/dynamische_formulare_validieren_mit_formencode/

Courtesy of the developers of http://www.auf-nach-mallorca.info
