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

import re


TYPE_OBJ = 0
TYPE_VALIDATOR = 1
TYPE_ITERABLE = 2



def kind_of(obj):
    if getattr(obj, "validate", False):
        return TYPE_VALIDATOR
    elif getattr(obj, "__iter__", False):
        return TYPE_ITERABLE
    else:
        return TYPE_OBJ


class Anything(object):
    def validate(self, data):
        return True


class Int(object):
    def __init__(self, exact=None, range=None):
        # validate range
        if range is not None:
            rmin,rmax = range
            if rmin is not None and rmax is not None:
                if range[1] < range[0]:
                    raise AttributeError("You cannot specify range where max is less than min bound")
        self.range = range
        self.exact = exact

    def __check_range(self, range, data):
        if range is not None:
            rmin, rmax = range
            if rmin is not None:
                if rmin > data:
                    return False
            if rmax is not None:
                if rmax < data:
                    return False
        return True

    def validate(self, data):
        if type(data) != type(0):
            return False
        if self.exact is not None:
            if data != self.exact:
                return False
        else:
            if not self.__check_range(self.range, data):
                return False
        return True

    def __str__(self):
        return "Int: exact: %s, range: %s" % (str(self.exact), str(self.range))


class String(object):
    def __init__(self, exact=None, regex=None):
        if regex is not None and type(regex) == type(""):
            regex = re.compile(regex)
        self.regex = regex
        self.exact = exact

    def validate(self, data):
        if type(data) != type(""):
            return False
        if self.exact is not None:
            if data != self.exact:
                return False
        else:
            if self.regex is not None:
                m = self.regex.match(data)
                if not m:
                    return False
        return True

    def __str__(self):
        return "String: exact: \"%s\", regex: %s" % (str(self.exact), str(self.regex))


class Maybe(object):
    def __init__(self, validators=[]):
        self.validators = validators

    def validate(self, data):
        for validator in self.validators:
            kind = kind_of(validator)
            if kind == TYPE_VALIDATOR:
                if validator.validate(data):
                    return True
            elif kind == TYPE_OBJ:
                if validator == data:
                    return True
        return False

    def __str__(self):
        return "Maybe: validators: %s" % str(self.validators)


class List(object):
    def __init__(self, validators=Anything()):
        self.validators = validators

    def validate(self, data):
        if type(data) != type([]):
            return False
        kind = kind_of(self.validators)
        if kind == TYPE_VALIDATOR:
            # validate all elements with only one validator
            for element in data:
                if not self.validators.validate(element):
                    return False
        elif kind == TYPE_ITERABLE:
            # strict validation
            if len(self.validators) != len(data):
                return False
            for element,validator in zip(data, self.validators):
                if not validator.validate(element):
                    return False
        else:
            for element in data:
                if element != self.validators:
                    return False
        # if we don't have any validators set, just check types
        return True

    def __str__(self):
        return "List: validators: %s" % str(self.validators)


class Bool(object):
    def __init__(self, exact=None):
        self.exact = exact

    def validate(self, data):
        if type(data) != type(True):
            return False
        if self.exact is not None:
            return self.exact == data
        return True

    def __str__(self):
        return "Bool: exact: %s" % str(self.exact)


class Dict(object):
    def __init__(self, validators={}, strict=True):
        self.validators = validators
        self.strict = strict

    def validate(self, data):
        if type(data) != type({}):
            return False
        used_validators = []
        for data_key,data_value in data.iteritems():
            data_valid = False
            # try to validate data_key with any of our validator key
            for validator_key,validator_value in self.validators.iteritems():
                if self.strict:
                    # we already used this validator, skip
                    if validator_key in used_validators:
                        continue
                kind = kind_of(validator_key)
                if kind == TYPE_VALIDATOR:
                    is_valid_key = validator_key.validate(data_key)
                else:
                    is_valid_key = validator_key == data_key

                kind = kind_of(validator_value)
                if kind == TYPE_VALIDATOR:
                    is_valid_value = validator_value.validate(data_value)
                else:
                    is_valid_value = validator_value == data_value
                if is_valid_key and is_valid_value:
                    if self.strict:
                        used_validators.append(validator_key)
                    data_valid = True
                    break
            if not data_valid:
                return False
        if self.strict and len(self.validators.keys()) != len(used_validators):
            return False
        return True
