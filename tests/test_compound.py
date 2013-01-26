# -*- coding: utf-8 -*-

import unittest

from formencode import compound, Invalid
from formencode.validators import DictConverter


class TestAllCompoundValidator(unittest.TestCase):

    def setUp(self):
        self.validator = compound.All(
            validators=[DictConverter({2: 1}), DictConverter({3: 2})])

    def test_to_python(self):
        self.assertEqual(self.validator.to_python(3), 1)

    def test_from_python(self):
        self.assertEqual(self.validator.from_python(1), 3)


class TestAnyCompoundValidator(unittest.TestCase):

    def setUp(self):
        self.validator = compound.Any(
            validators=[DictConverter({2: 'c'}), DictConverter({2: 'b'}),
                DictConverter({1: 'b'})])

    def test_to_python(self):
        # Should stop before 'c' coming from the right.
        self.assertEqual(self.validator.to_python(2), 'b')

    def test_from_python(self):
        # Should stop before 1 coming from the left.
        self.assertEqual(self.validator.from_python('b'), 2)

    def test_to_python_error(self):
        try:
            self.validator.to_python(3)
        except Invalid, e:
            self.failUnless('Enter a value from: 2' in str(e))
        else:
            self.fail('Invalid should be raised when no validator succeeds.')


class TestPipeCompoundValidator(unittest.TestCase):

    def setUp(self):
        self.validator = compound.Pipe(
            validators=[DictConverter({1: 2}), DictConverter({2: 3})])

    def test_to_python(self):
        self.assertEqual(self.validator.to_python(1), 3)

    def test_from_python(self):
        self.assertEqual(self.validator.from_python(3), 1)
