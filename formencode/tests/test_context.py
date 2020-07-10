from __future__ import absolute_import
import unittest

from formencode.context import Context, ContextRestoreError

c1 = Context(default=None)
c2 = Context()

class TestContext(unittest.TestCase):

    def change_state(self, context, func, *args, **change):
        state = context.set(**change)
        try:
            return func(*args)
        finally:
            state.restore()

    def assert_is(self, ob, attr, value):
        assert getattr(ob, attr) == value


    def test_fail(self):
        c3 = Context()
        res1 = c3.set(a=1)
        res2 = c3.set(b=2)
        with self.assertRaises(ContextRestoreError):
            res1.restore()
        assert c3.b == 2
        assert c3.a == 1
        res2.restore()
        res1.restore()

    def test_default(self):
        con = Context()
        res = con.set(a=2)
        con.set_default(a=4, b=1)
        assert con.b == 1
        assert con.a == 2
        res.restore()
        assert con.a == 4

    def test_one(self):
        state = c1.set(foo=1)
        self.assert_is(c1, 'foo', 1)
        state.restore()
        self.assert_is(c1, 'foo', None)
        state = c1.set(foo=2)
        state2 = c2.set(foo='test')
        self.assert_is(c1, 'foo', 2)
        self.assert_is(c2, 'foo', 'test')
        self.change_state(c1, self.assert_is, c1, 'foo', 3, foo=3)
        self.assert_is(c1, 'foo', 2)
        state.restore()
        state2.restore()

