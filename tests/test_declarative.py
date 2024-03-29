
import unittest
import re

from formencode import declarative


class TestDeclarative(unittest.TestCase):

    def test_init(self):
        D = declarative.Declarative
        obj = D()
        self.assertEqual(getattr(obj, 'foo', 'none'), 'none')
        obj = D(foo='bar')
        self.assertEqual(obj.foo, 'bar')
        self.assertEqual(getattr(obj, 'foobar', 'none'), 'none')
        obj = D(foo='bar', woo='par')
        self.assertEqual(obj.foo, 'bar')
        self.assertEqual(obj.woo, 'par')

    def test_call(self):
        D = declarative.Declarative
        obj_bar = D(foo='bar', woo='par')
        obj_baz = obj_bar(foo='baz')
        self.assertIs(type(obj_bar), type(obj_baz))
        self.assertIsNot(obj_bar, obj_baz)
        self.assertEqual(obj_baz.foo, 'baz')
        self.assertEqual(obj_baz.woo, 'par')

    def test_repr(self):
        D = declarative.Declarative
        obj_bar = D(foo='bar')
        obj_baz = D(foo='baz')
        obj = D(bar=obj_bar, baz=obj_baz)
        self.assertTrue(re.match(r"<Declarative object \d+"
            r" bar=<Declarative object \d+ foo='bar'>"
            r" baz=<Declarative object \d+ foo='baz'>>", repr(obj)))

    def test_repr_recursive(self):
        D = declarative.Declarative
        obj = D(foo='bar')
        obj.bar = obj
        self.assertTrue(re.match(r"<Declarative object \d+"
            r" bar=self foo='bar'>", repr(obj)))
