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


class MaybeTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate one type """
        x = v.Maybe([int])
        self.assertTrue(x.validate(10))

    def test_good_002(self):
        """ must validate few types """
        x = v.Maybe([10, "bar"])
        self.assertTrue(x.validate("bar"))

    def test_bad_001(self):
        """ must invalidate wrong types """
        x = v.Maybe([int])
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

    def test_good_003(self):
        """ must validate non-empty lists """
        x = v.List("foo")
        self.assertTrue(x.validate(["foo", "foo", "foo"]))

    def test_good_004(self):
        """ must validate regexes """
        x = v.List(re.compile('\w+'))
        self.assertTrue(x.validate(['foo', 'bar', 'zar']))

    def test_good_005(self):
        """ must validate by type """
        x = v.List(int)
        self.assertTrue(x.validate([1,2,3,4,5]))

    def test_bad_001(self):
        """ must invalidate non-empty lists """
        x = v.List("foo")
        self.assertFalse(x.validate(["foo", "bar"]))

    def test_bad_002(self):
        """ must invalidate regexes """
        x = v.List(re.compile('foo'))
        self.assertFalse(x.validate(['123', '456', '789']))

    def test_bad_003(self):
        """ must invalidate by type """
        x = v.List(str)
        self.assertFalse(x.validate([1,2,3,4,5]))

    def test_validators_good_001(self):
        """ must validate all elements with the same validator if only one validator is set """
        x = v.List(10)
        self.assertTrue(x.validate([10,10,10]))

    def test_validators_good_002(self):
        """ must validate all elements with according validators if few validators were set """
        x = v.List([10, "foo"])
        self.assertTrue(x.validate([10, "foo"]))

    def test_validators_bad_001(self):
        """ must invalidate list if contains wrong type, one validator is set """
        x = v.List(10)
        self.assertFalse(x.validate([5,5,5]))

    def test_validators_bad_002(self):
        """ must invalidate list by length when few validators were set """
        x = v.List([10, "foo"])
        self.assertFalse(x.validate([10, "foo", 15]))


class DictTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate dictionaries """
        x = v.Dict()
        self.assertTrue(x.validate({}))

    def test_good_002(self):
        """ must validate by key and value """
        x = v.Dict(
            {
                "key1": 10,
             }
            )
        self.assertTrue(x.validate({'key1': 10}))

    def test_good_003(self):
        """ must validate by few keys and values """
        x = v.Dict(
            {
                "key1": 10,
                "key2": 15,
                "key0": 0,
             }
            )
        self.assertTrue(x.validate({
                    'key0': 0,
                    'key1': 10,
                    'key2': 15,
                    }))

    def test_good_004(self):
        """ must validate by few keys and values """
        x = v.Dict({
                "firstName": str,
                "lastName": str,
                })
        self.assertTrue(x.validate({
                    "lastName": "Smith",
                    "firstName": "John",
                    }))

    def test_bad_001(self):
        """ must invalidate non-hashes """
        x = v.Dict()
        self.assertFalse(x.validate("foo"))

    def test_bad_002(self):
        """ must invalidate by key and value """
        x = v.Dict(
            {
                "key1": 10,
             }
            )
        self.assertFalse(x.validate({'key0': 5}))

    def test_bad_003(self):
        """ must invalidate by few keys and values """
        x = v.Dict(
            {
                "key1": 10,
                "key2": 15,
                "key0": 0,
             }
            )
        self.assertFalse(x.validate({
                    'key0': 0,
                    'key1': 10,
                    }))

    def test_bad_004(self):
        """ must invalidate by few keys and values """
        x = v.Dict({
                "firstName": str,
                "lastName": str,
                })
        self.assertFalse(x.validate({
                    "foo": "Smith",
                    "bar": "John",
                    }))


class JobRelatedTestCase(unittest.TestCase):
    """ production-use use-cases for me """
    def test_good_001(self):
        reference_struct = v.Dict({
                re.compile('\w+'):
                    v.List(v.Dict({
                                "id": int,
                                "is_full": bool,
                                "shard_id": int,
                                "url": str
                                }))
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
                re.compile('\w+'):
                    v.List(v.Dict({
                                "id": int,
                                "is_full": bool,
                                "shard_id": int,
                                "url": str
                                }))
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
        ref_struct = v.List(int)
        self.assertTrue(ref_struct.validate(l))
        l.append('bad_end')
        self.assertFalse(ref_struct.validate(l))

    def test_integer_list_002(self):
        """ test case for integer list sample #2 """
        l = [10, "foobar", True]
        ref_struct = v.List([int, str, bool])
        self.assertTrue(ref_struct.validate(l))
        l.append('screw that list')
        self.assertFalse(ref_struct.validate(l))

    def test_integer_list_003(self):
        """ test case for integer list sample #3 """
        l = [10, "foo", 15," bar"]
        ref_struct = v.List(
                v.Maybe([int, str])
                )
        self.assertTrue(ref_struct.validate(l))
        l.append(True)
        self.assertFalse(ref_struct.validate(l))

    def test_dictionary_001(self):
        """ test case for dictionary #1 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        ref_struct = v.Dict({
                'firstName': str,
                'lastName':  str,
                })
        self.assertTrue(ref_struct.validate(d))
        d['foo'] = 10
        self.assertFalse(ref_struct.validate(d))

    def test_dictionary_002(self):
        """ test case for dictionary #2 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        ref_struct = v.Dict({
                re.compile('\w+'): str
                },
                            strict=False)
        self.assertTrue(ref_struct.validate(d))
        d['anotherKey'] = 'look ma, still validates'
        self.assertTrue(ref_struct.validate(d))
        d['badKey'] = 10
        self.assertFalse(ref_struct.validate(d))


if __name__ == '__main__':
    unittest.main()
