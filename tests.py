#!/usr/bin/env python

#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2008 Konstantin Merenkov <kmerenkov@gmail.com>
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.


import unittest
import re
import validators as v


class IntTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate integers """
        x = v.Int()
        self.assertTrue(x.validate(10))

    def test_range_good_001(self):
        """ must validate integers within specified range """
        x = v.Int(range=(0, 10))
        self.assertTrue(x.validate(5))

    def test_range_good_002(self):
        """ must validate integers within specified range when only max bound is set """
        x = v.Int(range=(None,15))
        self.assertTrue(x.validate(5))

    def test_range_good_003(self):
        """ must validate integers within specified range when only min bound is set """
        x = v.Int(range=(5,None))
        self.assertTrue(x.validate(10))

    def test_range_good_004(self):
        """ must validate any int if min and max bounds of range are None """
        x = v.Int(range=(None,None))
        self.assertTrue(x.validate(10))

    def test_exact_good_001(self):
        """ must validate integer equal to 'exact' argument value """
        x = v.Int(exact=10)
        self.assertTrue(x.validate(10))

    def test_bad_001(self):
        """ must invalidate non-integers """
        x = v.Int()
        self.assertFalse(x.validate("foo"))

    def test_range_bad_001(self):
        """ must invalidate integers outside specified range """
        x = v.Int(range=(0, 10))
        self.assertFalse(x.validate(15))

    def test_range_bad_002(self):
        """ must invalidate int ouside range when only max bound is set """
        x = v.Int(range=(None,10))
        self.assertFalse(x.validate(15))

    def test_range_bad_003(self):
        """ must invalidate int outside range when only min bound is set """
        x = v.Int(range=(5,None))
        self.assertFalse(x.validate(1))

    def test_range_bad_004(self):
        """ must throw attribute error when max < min """
        self.assertRaises(AttributeError, lambda: v.Int(range=(15,10)))

    def test_exact_bad_001(self):
        """ must invalidate integers != to 'exact' argument value """
        x = v.Int(exact=10)
        self.assertFalse(x.validate(15))


class StringTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate string """
        x = v.String()
        self.assertTrue(x.validate(""))

    def test_exact_good_001(self):
        """ must validate exact string """
        x = v.String("foo")
        self.assertTrue(x.validate("foo"))

    def test_re_good_001(self):
        """ must validate str regex """
        x = v.String(regex=".+foo.+")
        self.assertTrue(x.validate("barfoobar"))

    def test_re_good_002(self):
        """ must validate re regex """
        x = v.String(regex=re.compile(".+foo.+"))
        self.assertTrue(x.validate("barfoobar"))

    def test_exact_bad_002(self):
        """ must invalidate exact string """
        x = v.String("foo")
        self.assertFalse(x.validate("bar"))

    def test_re_bad_001(self):
        """ must invalidate regex """
        x = v.String(regex=".+foo.+")
        self.assertFalse(x.validate("foo"))


class MaybeTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate one type """
        x = v.Maybe([v.Int()])
        self.assertTrue(x.validate(10))

    def test_good_002(self):
        """ must validate few types """
        x = v.Maybe([v.Int(10), v.String("bar")])
        self.assertTrue(x.validate("bar"))

    def test_bad_001(self):
        """ must invalidate wrong types """
        x = v.Maybe([v.Int()])
        self.assertFalse(x.validate("foo"))


class ListTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate empty lists """
        x = v.List()
        self.assertTrue(x.validate([]))

    def test_good_002(self):
        """ must validate non-empty lists """
        x = v.List()
        self.assertTrue(x.validate([1,2,3]))

    def test_validators_good_001(self):
        """ must validate all elements with the same validator if only one validator is set """
        x = v.List([v.Int(10)])
        self.assertTrue(x.validate([10,10,10]))

    def test_validators_good_002(self):
        """ must validate all elements with according validators if few validators were set """
        x = v.List([v.Int(10), v.String("foo")])
        self.assertTrue(x.validate([10, "foo"]))

    def test_validators_bad_001(self):
        """ must invalidate list if contains wrong type, one validator is set """
        x = v.List([v.Int(10)])
        self.assertFalse(x.validate([5,5,5]))

    def test_validators_bad_002(self):
        """ must invalidate list by length when few validators were set """
        x = v.List([v.Int(10), v.String("foo")])
        self.assertFalse(x.validate([10, "foo", 15]))


class BoolTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate True """
        x = v.Bool()
        self.assertTrue(x.validate(True))

    def test_good_002(self):
        """ must validate False """
        x = v.Bool()
        self.assertTrue(x.validate(False))

    def test_bad_001(self):
        """ must invalidate non-bools """
        x = v.Bool()
        self.assertFalse(x.validate("foo"))

    def test_exact_good_001(self):
        """ must validate exact True """
        x = v.Bool(True)
        self.assertTrue(x.validate(True))

    def test_exact_good_002(self):
        """ must validate False """
        x = v.Bool(False)
        self.assertTrue(x.validate(False))


class DictTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate dictionaries """
        x = v.Dict()
        self.assertTrue(x.validate({}))

    def test_good_002(self):
        """ must validate by key and value """
        x = v.Dict(
            {
                v.String("key1"): v.Int(10),
             }
            )
        self.assertTrue(x.validate({'key1': 10}))

    def test_good_003(self):
        """ must validate by few keys and values """
        x = v.Dict(
            {
                v.String("key1"): v.Int(10),
                v.String("key2"): v.Int(15),
                v.String("key0"): v.Int(0),
             }
            )
        self.assertTrue(x.validate({
                    'key0': 0,
                    'key1': 10,
                    'key2': 15,
                    }))

    def test_bad_001(self):
        """ must invalidate non-hashes """
        x = v.Dict()
        self.assertFalse(x.validate("foo"))

    def test_bad_002(self):
        """ must invalidate by key and value """
        x = v.Dict(
            {
                v.String("key1"): v.Int(10),
             }
            )
        self.assertFalse(x.validate({'key0': 5}))

    def test_bad_003(self):
        """ must invalidate by few keys and values """
        x = v.Dict(
            {
                v.String("key1"): v.Int(10),
                v.String("key2"): v.Int(15),
                v.String("key0"): v.Int(0),
             }
            )
        self.assertFalse(x.validate({
                    'key0': 0,
                    'key1': 10,
                    }))


class JobRelatedTestCase(unittest.TestCase):
    """ production-use use-cases for me """
    def test_good_001(self):
        reference_struct = v.Dict({
                v.String(regex='\w+'):
                    v.List([v.Dict({
                                v.String("id"): v.Int(),
                                v.String("is_full"): v.Bool(),
                                v.String("shard_id"): v.Int(),
                                v.String("url"): v.String()
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
        reference_struct = v.Dict({
                v.String(regex='\w+'):
                    v.List([v.Dict({
                                v.String("id"): v.Int(),
                                v.String("is_full"): v.Bool(),
                                v.String("shard_id"): v.Int(),
                                v.String("url"): v.String()
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


class SamplesTestCase(unittest.TestCase):
    def test_integer_list_001(self):
        """ test case for integer list sample #1 """
        l = [1,2,3,4,5,6]
        ref_struct = v.List([v.Int()])
        self.assertTrue(ref_struct.validate(l))
        l.append('bad_end')
        self.assertFalse(ref_struct.validate(l))

    def test_integer_list_002(self):
        """ test case for integer list sample #2 """
        l = [10, "foobar", True]
        ref_struct = v.List([
                v.Int(),
                v.String(),
                v.Bool()
                ])
        self.assertTrue(ref_struct.validate(l))
        l.append('screw that list')
        self.assertFalse(ref_struct.validate(l))

    def test_integer_list_003(self):
        """ test case for integer list sample #3 """
        l = [10, "foo", 15," bar"]
        ref_struct = v.List([
                v.Maybe([
                        v.Int(),
                        v.String()
                        ])
                ])
        self.assertTrue(ref_struct.validate(l))
        l.append(True)
        self.assertFalse(ref_struct.validate(l))

    def test_dictionary_001(self):
        """ test case for dictionary #1 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        ref_struct = v.Dict({
                v.String('firstName'): v.String(),
                v.String('lastName'):  v.String(),
                })
        self.assertTrue(ref_struct.validate(d))
        d['foo'] = 10
        self.assertFalse(ref_struct.validate(d))

    def test_dictionary_002(self):
        """ test case for dictionary #2 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        ref_struct = v.Dict({
                v.String(regex='\w+'): v.String()
                },
                            strict=False)
        self.assertTrue(ref_struct.validate(d))
        d['anotherKey'] = 'look ma, still validates'
        self.assertTrue(ref_struct.validate(d))
        d['badKey'] = 10
        self.assertFalse(ref_struct.validate(d))


if __name__ == '__main__':
    unittest.main()
