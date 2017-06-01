from __future__ import absolute_import, division, print_function

import ctypes
import unittest

from java import *


class TestArray(unittest.TestCase):

    def test_basic(self):
        array_C = jarray(jchar)("hello")
        self.assertEqual(5, len(array_C))
        self.assertEqual(repr(array_C).replace("u'", "'"),
                         "jarray('C')(['h', 'e', 'l', 'l', 'o'])")

    def test_output_arg(self):
        String = jclass('java.lang.String')
        string = String(u'\u1156\u2278\u3390\u44AB')
        for btarray in ([0] * 4,
                        (0,) * 4,
                        jarray(jbyte)([0] * 4)):
            # This version of getBytes returns the 8 low-order of each Unicode character.
            string.getBytes(0, 4, btarray, 0)
            if not isinstance(btarray, tuple):
                self.assertEquals(btarray, [ctypes.c_int8(x).value for x in [0x56, 0x78, 0x90, 0xAB]])

    def test_multiple_dimensions(self):
        Arrays = jclass('com.chaquo.python.TestArray')
        matrix = [[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9]]
        self.assertEquals(Arrays.methodParamsMatrixI(matrix), True)
        self.assertEquals(Arrays.methodReturnMatrixI(), matrix)

    # Most of the positive tests are in test_conversion, but here are some error tests.
    def test_modify(self):
        array_Z = jarray(jboolean)([True, False])
        with self.assertRaisesRegexp(TypeError, "Cannot convert"):
            array_Z[0] = 1

        Object = jclass("java.lang.Object")
        Boolean = jclass("java.lang.Boolean")
        array_Boolean = jarray(Boolean)([True, False])
        with self.assertRaisesRegexp(TypeError, "Cannot convert"):
            array_Boolean[0] = 1
        with self.assertRaisesRegexp(JavaException, "ArrayStoreException"):
            cast(jarray(Object), array_Boolean)[0] = 1

        array_Object = jarray(Object)([True, False])
        array_Object[0] = 1
        self.assertEqual([1, False], array_Object)

    def test_str_repr(self):
        for func in [str, repr]:
            self.assertEqual("cast('[Z', None)", func(jarray(jboolean)(None)))
            self.assertEqual("jarray('Z')([])", func(jarray(jboolean)([])))
            self.assertEqual("jarray('Z')([True])", func(jarray(jboolean)([True])))
            self.assertEqual("jarray('Z')([True])", func(jarray(jboolean)((True,))))
            self.assertEqual("jarray('Z')([True, False])", func(jarray(jboolean)([True, False])))
            self.assertEqual("jarray('[Z')([[True], [False, True]])",
                             func(jarray(jarray(jboolean))([[True], [False, True]])))

    def test_eq(self):
        tf = jarray(jboolean)([True, False])
        self.verify_equal(tf, tf)
        self.verify_equal(tf, jarray(jboolean)([True, False]))
        self.verify_equal(tf, [True, False])
        self.verify_equal(tf, [1, 0])

        self.verify_not_equal(tf, [True, True])
        self.verify_not_equal(tf, [True, False, True])

        single = jarray(jboolean)([True])
        self.verify_not_equal(single, True)

        empty = jarray(jboolean)([])
        self.verify_equal(empty, empty)
        self.verify_equal(empty, [])
        self.verify_not_equal(empty, single)
        self.verify_not_equal(empty, False)

    def verify_equal(self, a, b):
        self.assertEqual(a, b)
        self.assertEqual(b, a)
        self.assertFalse(a != b)
        self.assertFalse(b != a)

    def verify_not_equal(self, a, b):
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)

    def test_hash(self):
        with self.assertRaisesRegexp(TypeError, "unhashable type"):
            hash(jarray(jboolean)([]))

    def test_add(self):
        tf = jarray(jboolean)([True, False])
        self.assertEqual(tf, tf + [])
        self.assertEqual(tf, [] + tf)
        self.assertEqual(tf, tf + jarray(jboolean)([]))
        self.assertEqual([True, False, True], tf + [True])
        with self.assertRaises(TypeError):
            tf + True
        with self.assertRaises(TypeError):
            tf + None

        String = jclass("java.lang.String")
        hw = jarray(String)(["hello", "world"])
        self.assertEqual([True, False, "hello", "world"], tf + hw)