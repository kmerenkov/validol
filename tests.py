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
from validators import validate, AnyOf


class AnyOfTestCase(unittest.TestCase):
    def test_good_001(self):
        """ must validate one type """
        x = AnyOf([int])
        self.assertTrue(x.validate(10))

    def test_good_002(self):
        """ must validate few types """
        x = AnyOf([10, "bar"])
        self.assertTrue(x.validate("bar"))

    def test_bad_001(self):
        """ must invalidate wrong types """
        x = AnyOf([int])
        self.assertFalse(x.validate("foo"))


class ListTestCase(unittest.TestCase):
    def test_good_001(self):
        x = []
        self.assertTrue(validate(x, [1,2,3,4]))

    def test_good_002(self):
        x = [int]
        self.assertTrue(validate(x, [1,2,3,4]))

    def test_bad_001(self):
        x = []
        self.assertFalse(validate(x, "foo"))

    def test_bad_002(self):
        x = [int]
        self.assertFalse(validate(x, ["foo", "bar"]))


class DictTestCase(unittest.TestCase):
    def test_good_001(self):
        x = {}
        self.assertTrue(validate(x, {'foo': 'bar'}))

    def test_good_002(self):
        x = {str: int}
        self.assertTrue(validate(x, {'foo': 10}))

    def test_good_003(self):
        x = {re.compile('\d+'): str}
        self.assertTrue(validate(x, {'10': 'bar'}))

    def test_good_004(self):
        x = {re.compile('\d+'): str}
        self.assertTrue(validate(x, {'10': 'foo', '20': 'bar'}))

    def test_bad_001(self):
        x = {}
        self.assertFalse(validate(x, []))

    def test_bad_002(self):
        x = {str: int}
        self.assertFalse(validate(x, {'foo': 'bar'}))

    def test_bad_003(self):
        x = {re.compile('\d+'): str}
        self.assertFalse(validate(x, {'foo': 'bar'}))


class JobRelatedTestCase(unittest.TestCase):
    """ production-use use-cases for me """
    def test_good_001(self):
        reference_struct = {
            re.compile('\w+'): [{"id": int,
                                 "is_full": bool,
                                 "shard_id": int,
                                 "url": str}]
            }
        actual_struct = {
            'foo': [{'id': 0, 'is_full': False, 'shard_id': 0, 'url': 'foo'},
                    {'id': 1, 'is_full': True, 'shard_id': 3, 'url': 'bar'},
                    {'id': 2, 'is_full': False, 'shard_id': 5, 'url': 'zar'},],
            'bar': [{'id': 3, 'is_full': False, 'shard_id': 7, 'url': 'foobar'},
                    {'id': 4, 'is_full': True, 'shard_id': 9, 'url': 'barfoo'},
                    {'id': 5, 'is_full': False, 'shard_id': 11, 'url': 'zarbar'},]
            }
        self.assertTrue(validate(reference_struct, actual_struct))


    def test_bad_001(self):
        reference_struct = {
            re.compile('\w+'): [{"id": int,
                                 "is_full": bool,
                                 "shard_id": int,
                                 "url": str}]
            }
        actual_struct = {
            'foo': [{'id': 0, 'is_full': False, 'shard_id': 0, 'url': 'foo'},
                    {'id': 1, 'is_full': True, 'shard_id': 3, 'url': 'bar'},
                    {'id': 2, 'is_full': False, 'shard_id': 5, 'url': 'zar'},],
            'bar': [{'id': 3, 'is_full': False, 'shard_id': 7, 'url': 'foobar'},
                    {'id': 4, 'is_full': True, 'shard_id': 9, 'url': 'barfoo'},
                    {'id': 5, 'is_full': False, 'shard_id': 11, 'url': 10},]
            }
        self.assertFalse(validate(reference_struct, actual_struct))


class SamplesTestCase(unittest.TestCase):
    def test_integer_list_001(self):
        """ test case for integer list sample #1 """
        l = [1,2,3,4,5,6]
        ref_struct = [int]
        self.assertTrue(validate(ref_struct, l))
        l.append('bad_end')
        self.assertFalse(validate(ref_struct, l))

    def test_integer_list_003(self):
        """ test case for integer list sample #3 """
        l = [10, "foo", 15," bar"]
        ref_struct = [AnyOf([int, str])]
        self.assertTrue(validate(ref_struct, l))
        l.append(True)
        self.assertFalse(validate(ref_struct, l))

    def test_dictionary_001(self):
        """ test case for dictionary #1 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        ref_struct = {
            'firstName': str,
            'lastName':  str
            }
        self.assertTrue(validate(ref_struct, d))
        d['foo'] = 10
        self.assertFalse(validate(ref_struct, d))

    def test_dictionary_002(self):
        """ test case for dictionary #2 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        ref_struct = {re.compile('\w+'): str}
        self.assertTrue(validate(ref_struct, d))
        d['anotherKey'] = 'look ma, still validates'
        self.assertTrue(validate(ref_struct, d))
        d['badKey'] = 10
        self.assertFalse(validate(ref_struct, d))


if __name__ == '__main__':
    unittest.main()
