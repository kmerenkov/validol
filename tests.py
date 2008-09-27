#!/usr/bin/env python

# "THE BEER-WARE LICENSE" (Revision 42):
# <kmerenkov@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return

import unittest
import re
from validators import Int, String, Maybe, List, Bool, Dict


class IntTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate integers """
        x = Int()
        self.assertTrue(x.validate(10))

    def test_range_good_001(self):
        """ must validate integers within specified range """
        x = Int(range=(0, 10))
        self.assertTrue(x.validate(5))

    def test_range_good_002(self):
        """ must validate integers within specified range when only max bound is set """
        x = Int(range=(None,15))
        self.assertTrue(x.validate(5))

    def test_range_good_003(self):
        """ must validate integers within specified range when only min bound is set """
        x = Int(range=(5,None))
        self.assertTrue(x.validate(10))

    def test_range_good_004(self):
        """ must validate any int if min and max bounds of range are None """
        x = Int(range=(None,None))
        self.assertTrue(x.validate(10))

    def test_exact_good_001(self):
        """ must validate integer equal to 'exact' argument value """
        x = Int(exact=10)
        self.assertTrue(x.validate(10))

    def test_bad_001(self):
        """ must invalidate non-integers """
        x = Int()
        self.assertFalse(x.validate("foo"))

    def test_range_bad_001(self):
        """ must invalidate integers outside specified range """
        x = Int(range=(0, 10))
        self.assertFalse(x.validate(15))

    def test_range_bad_002(self):
        """ must invalidate int ouside range when only max bound is set """
        x = Int(range=(None,10))
        self.assertFalse(x.validate(15))

    def test_range_bad_003(self):
        """ must invalidate int outside range when only min bound is set """
        x = Int(range=(5,None))
        self.assertFalse(x.validate(1))

    def test_range_bad_004(self):
        """ must throw attribute error when max < min """
        self.assertRaises(AttributeError, lambda: Int(range=(15,10)))

    def test_exact_bad_001(self):
        """ must invalidate integers != to 'exact' argument value """
        x = Int(exact=10)
        self.assertFalse(x.validate(15))


class StringTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate string """
        x = String()
        self.assertTrue(x.validate(""))

    def test_exact_good_001(self):
        """ must validate exact string """
        x = String("foo")
        self.assertTrue(x.validate("foo"))

    def test_re_good_001(self):
        """ must validate str regex """
        x = String(regex=".+foo.+")
        self.assertTrue(x.validate("barfoobar"))

    def test_re_good_002(self):
        """ must validate re regex """
        x = String(regex=re.compile(".+foo.+"))
        self.assertTrue(x.validate("barfoobar"))

    def test_exact_bad_002(self):
        """ must invalidate exact string """
        x = String("foo")
        self.assertFalse(x.validate("bar"))

    def test_re_bad_001(self):
        """ must invalidate regex """
        x = String(regex=".+foo.+")
        self.assertFalse(x.validate("foo"))


class MaybeTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate one type """
        x = Maybe([Int()])
        self.assertTrue(x.validate(10))

    def test_good_002(self):
        """ must validate few types """
        x = Maybe([Int(10), String("bar")])
        self.assertTrue(x.validate("bar"))

    def test_bad_001(self):
        """ must invalidate wrong types """
        x = Maybe([Int()])
        self.assertFalse(x.validate("foo"))


class ListTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate empty lists """
        x = List()
        self.assertTrue(x.validate([]))

    def test_good_002(self):
        """ must validate non-empty lists """
        x = List()
        self.assertTrue(x.validate([1,2,3]))

    def test_validators_good_001(self):
        """ must validate all elements with the same validator if only one validator is set """
        x = List([Int(10)])
        self.assertTrue(x.validate([10,10,10]))

    def test_validators_good_002(self):
        """ must validate all elements with according validators if few validators were set """
        x = List([Int(10), String("foo")])
        self.assertTrue(x.validate([10, "foo"]))

    def test_validators_bad_001(self):
        """ must invalidate list if contains wrong type, one validator is set """
        x = List([Int(10)])
        self.assertFalse(x.validate([5,5,5]))

    def test_validators_bad_002(self):
        """ must invalidate list by length when few validators were set """
        x = List([Int(10), String("foo")])
        self.assertFalse(x.validate([10, "foo", 15]))


class BoolTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate True """
        x = Bool()
        self.assertTrue(x.validate(True))

    def test_good_002(self):
        """ must validate False """
        x = Bool()
        self.assertTrue(x.validate(False))

    def test_bad_001(self):
        """ must invalidate non-bools """
        x = Bool()
        self.assertFalse(x.validate("foo"))

    def test_exact_good_001(self):
        """ must validate exact True """
        x = Bool(True)
        self.assertTrue(x.validate(True))

    def test_exact_good_002(self):
        """ must validate False """
        x = Bool(False)
        self.assertTrue(x.validate(False))


class DictTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate dictionaries """
        x = Dict()
        self.assertTrue(x.validate({}))

    def test_good_002(self):
        """ must validate by key and value """
        x = Dict(
            {
                String("key1"): Int(10),
             }
            )
        self.assertTrue(x.validate({'key1': 10}))

    def test_good_003(self):
        """ must validate by few keys and values """
        x = Dict(
            {
                String("key1"): Int(10),
                String("key2"): Int(15),
                String("key0"): Int(0),
             }
            )
        self.assertTrue(x.validate({
                    'key0': 0,
                    'key1': 10,
                    'key2': 15,
                    }))

    def test_bad_001(self):
        """ must invalidate non-hashes """
        x = Dict()
        self.assertFalse(x.validate("foo"))

    def test_bad_002(self):
        """ must invalidate by key and value """
        x = Dict(
            {
                String("key1"): Int(10),
             }
            )
        self.assertFalse(x.validate({'key0': 5}))

    def test_bad_003(self):
        """ must invalidate by few keys and values """
        x = Dict(
            {
                String("key1"): Int(10),
                String("key2"): Int(15),
                String("key0"): Int(0),
             }
            )
        self.assertFalse(x.validate({
                    'key0': 0,
                    'key1': 10,
                    }))


class JobRelatedTestCase(unittest.TestCase):
    """ production-use use-cases for me """
    def test_good_001(self):
        reference_struct = Dict({
                String(regex='\w+'):
                    List([Dict({
                                String("id"): Int(),
                                String("is_full"): Bool(),
                                String("shard_id"): Int(),
                                String("url"): String()
                                })])
                }, strict=False)
        actual_struct = {
            'foo': [{'id': 0, 'is_full': False, 'shard_id': 0, 'url': 'foo'},
                    {'id': 1, 'is_full': True, 'shard_id': 3, 'url': 'bar'},
                    {'id': 2, 'is_full': False, 'shard_id': 5, 'url': 'zar'},],
            'bar': [{'id': 3, 'is_full': False, 'shard_id': 7, 'url': 'foobar'},
                    {'id': 4, 'is_full': True, 'shard_id': 9, 'url': 'barfoo'},
                    {'id': 5, 'is_full': False, 'shard_id': 11, 'url': 'zarbar'},]
            }
        self.assertTrue(reference_struct.validate(actual_struct))


    def test_bad_001(self):
        reference_struct = Dict({
                String(regex='\w+'):
                    List([Dict({
                                String("id"): Int(),
                                String("is_full"): Bool(),
                                String("shard_id"): Int(),
                                String("url"): String()
                                })])
                }, strict=False)
        actual_struct = {
            'foo': [{'id': 0, 'is_full': False, 'shard_id': 0, 'url': 'foo'},
                    {'id': 1, 'is_full': True, 'shard_id': 3, 'url': 'bar'},
                    {'id': 2, 'is_full': False, 'shard_id': 5, 'url': 'zar'},],
            'bar': [{'id': 3, 'is_full': False, 'shard_id': 7, 'url': 'foobar'},
                    {'id': 4, 'is_full': True, 'shard_id': 9, 'url': 'barfoo'},
                    {'id': 5, 'is_full': False, 'shard_id': 11, 'url': 10},]
            }
        self.assertFalse(reference_struct.validate(actual_struct))


if __name__ == '__main__':
    unittest.main()
