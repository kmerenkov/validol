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
from __init__ import validate, AnyOf, Many, Optional, Scheme, BaseValidator


class LoadTestCase(unittest.TestCase):
    def test_hash_good_001(self):
        x = dict(map(lambda x: (str(x), x), xrange(1000)))
        s = dict(map(lambda x: (str(x), int), xrange(1000)))
        self.assertTrue(validate(s, x))

    def test_hash_bad_001(self):
        x = dict(map(lambda x: (str(x), x), xrange(1000)))
        s = dict(map(lambda x: (str(x), int), xrange(1000)))
        s['999'] = str
        self.assertFalse(validate(s, x))

    def test_hash_good_002(self):
        x = dict(map(lambda x: (str(x), x), xrange(1000)))
        s = dict(map(lambda x: (Optional(str(x)), int), xrange(1000)))
        self.assertTrue(validate(s, x))

    def test_hash_bad_002(self):
        x = dict(map(lambda x: (str(x), x), xrange(1000)))
        s = dict(map(lambda x: (Optional(str(x)), int), xrange(1000)))
        s['999'] = str
        self.assertFalse(validate(s, x))


if __name__ == '__main__':
    unittest.main()
