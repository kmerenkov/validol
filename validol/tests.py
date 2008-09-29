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
from __init__ import validate, AnyOf, Many


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
        x = [object]
        self.assertTrue(validate(x, [1,2,3,4]))

    def test_good_002(self):
        x = [int]
        self.assertTrue(validate(x, [1,2,3,4]))

    def test_good_003(self):
        x = []
        self.assertTrue(validate(x, []))

    def test_good_004(self):
        x = ()
        self.assertTrue(validate(x, ()))

    def test_good_005(self):
        x = (int, str, bool)
        self.assertTrue(validate(x, (10, "foo", True)))

    def test_bad_001(self):
        x = []
        self.assertFalse(validate(x, "foo"))

    def test_bad_002(self):
        x = [int]
        self.assertFalse(validate(x, ["foo", "bar"]))

    def test_bad_003(self):
        x = []
        self.assertFalse(validate(x, [1,2,3]))

    def test_bad_004(self):
        x = ()
        self.assertFalse(validate(x, (10)))

    def test_bad_005(self):
        x = (int, str, bool)
        self.assertFalse(validate(x, ("foo", 10, False)))

    def test_bad_006(self):
        x = ()
        self.assertFalse(validate(x, []))



class DictTestCase(unittest.TestCase):
    def test_good_001(self):
        x = {object: object}
        self.assertTrue(validate(x, {'foo': 'bar'}))

    def test_good_002(self):
        x = {str: int}
        self.assertTrue(validate(x, {'foo': 10}))

    def test_good_003(self):
        x = {re.compile('\d+'): str}
        self.assertTrue(validate(x, {'10': 'bar'}))

    def test_good_004(self):
        x = {Many(re.compile('\d+')): str}
        self.assertTrue(validate(x, {'10': 'foo', '20': 'bar'}))

    def test_good_005(self):
        x = {}
        self.assertTrue(validate(x, {}))

    def test_bad_001(self):
        x = {}
        self.assertFalse(validate(x, []))

    def test_bad_002(self):
        x = {str: int}
        self.assertFalse(validate(x, {'foo': 'bar'}))

    def test_bad_003(self):
        x = {re.compile('\d+'): str}
        self.assertFalse(validate(x, {'foo': 'bar'}))

    def test_bad_004(self):
        x = {}
        self.assertFalse(validate(x, {'a':'b'}))

    def test_bad_005(self):
        x = {str: str}
        self.assertFalse(validate(x, {}))

    def test_bad_006(self):
        x = {"foo": int, "bar": int}
        self.assertFalse(validate(x, {"bar": 10}))


class JobRelatedTestCase(unittest.TestCase):
    """ production-use use-cases for me """
    def test_good_001(self):
        scheme = {
            Many(re.compile('\w+')): [{"id": int,
                                       "is_full": bool,
                                       "shard_id": int,
                                       "url": str}]
            }
        data = {
            'foo': [{'id': 0, 'is_full': False, 'shard_id': 0, 'url': 'foo'},
                    {'id': 1, 'is_full': True, 'shard_id': 3, 'url': 'bar'},
                    {'id': 2, 'is_full': False, 'shard_id': 5, 'url': 'zar'},],
            'bar': [{'id': 3, 'is_full': False, 'shard_id': 7, 'url': 'foobar'},
                    {'id': 4, 'is_full': True, 'shard_id': 9, 'url': 'barfoo'},
                    {'id': 5, 'is_full': False, 'shard_id': 11, 'url': 'zarbar'},]
            }
        self.assertTrue(validate(scheme, data))


    def test_bad_001(self):
        scheme = {
            Many(re.compile('\w+')): [{"id": int,
                                       "is_full": bool,
                                       "shard_id": int,
                                       "url": str}]
            }
        data = {
            'foo': [{'id': 0, 'is_full': False, 'shard_id': 0, 'url': 'foo'},
                    {'id': 1, 'is_full': True, 'shard_id': 3, 'url': 'bar'},
                    {'id': 2, 'is_full': False, 'shard_id': 5, 'url': 'zar'},],
            'bar': [{'id': 3, 'is_full': False, 'shard_id': 7, 'url': 'foobar'},
                    {'id': 4, 'is_full': True, 'shard_id': 9, 'url': 'barfoo'},
                    {'id': 5, 'is_full': False, 'shard_id': 11, 'url': 10},]
            }
        self.assertFalse(validate(scheme, data))


class SamplesTestCase(unittest.TestCase):
    def test_integer_list_001(self):
        """ test case for integer list sample #1 """
        l = [1,2,3,4,5,6]
        scheme = [int]
        self.assertTrue(validate(scheme, l))
        l.append('bad_end')
        self.assertFalse(validate(scheme, l))

    def test_integer_list_003(self):
        """ test case for integer list sample #3 """
        l = [10, "foo", 15," bar"]
        scheme = [AnyOf([int, str])]
        self.assertTrue(validate(scheme, l))
        l.append(True)
        self.assertFalse(validate(scheme, l))

    def test_dictionary_001(self):
        """ test case for dictionary #1 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        scheme = {
            'firstName': str,
            'lastName':  str
            }
        self.assertTrue(validate(scheme, d))
        d['foo'] = 10
        self.assertFalse(validate(scheme, d))

    def test_dictionary_002(self):
        """ test case for dictionary #2 """
        d = {'firstName': 'John', 'lastName': 'Smith'}
        scheme = {
            Many(re.compile('\w+')): str
            }
        self.assertTrue(validate(scheme, d))
        d['anotherKey'] = 'look ma, still validates'
        self.assertTrue(validate(scheme, d))
        d['badKey'] = 10
        self.assertFalse(validate(scheme, d))


if __name__ == '__main__':
    unittest.main()
