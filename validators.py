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


class Int(object):
    """ Validates integers """
    def __init__(self, exact=None, range=None):
        """
        By default validates any integer value.
        - 'exact': when specified, this in only this integer will be validated,
        other will be invalid.
        - 'range': range is a tuple, first element is min, second is max, both
        elements may be integer or None, thus you can set only max boundary, or
        only min, or both. Ignored when 'exact' is specified.
        """
        # validate range
        if range is not None:
            rmin,rmax = range
            if rmin is not None and rmax is not None:
                if range[1] < range[0]:
                    raise AttributeError("You cannot specify range where max is less than min bound")
        self.range = range
        self.exact = exact

    def __check_range(self, range, data):
        """ Validates range, this function is used internally, you don't really
        want to use it """
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
        """
        Validates data according to specified information on initializing this object.
        Returns True if data is valid, False otherwise.
        """
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
    """ Validates strings """
    def __init__(self, exact=None, regex=None):
        """
        By default, validates any string.
        - 'exact': when specified, this and only this string will be validated,
        others will be invalid.
        - 'regex': can be one of the following:
                   - string (then regex is compiled automagically),
                   - None (default, don't perform regex searching),
                   - compiled regex.
          Used for regex validation.
        """
        if regex is not None and type(regex) == type(""):
            regex = re.compile(regex)
        self.regex = regex
        self.exact = exact

    def validate(self, data):
        """
        Validates data according to specified information on initializing this object.
        Returns True if data is valid, False otherwise.
        """
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
    """
    Maybe is a magic type of data, it validates
    if one of its children' validators validate
    your data. Think of it as of "OR"
    """
    def __init__(self, validators=[]):
        """
        By default doesn't validate anything, you have to
        set at least one validator.
        - 'validators': list of other validators, such as
                        Int, String, Bool, or anything else.
                        If at least one of specified validators
                        can validate your data - then validation
                        will be successful.
        """
        self.validators = validators

    def validate(self, data):
        """
        Validates data according to specified information on initializing this object.
        Returns True if data is valid, False otherwise.
        """
        for validator in self.validators:
            if validator.validate(data):
                return True
        return False

    def __str__(self):
        return "Maybe: validators: %s" % str(self.validators)


class List(object):
    """ Validates lists """
    def __init__(self, validators=[]):
        """
        By default validates any list at all.
        - 'validators': validators to validate list items.
             If validator is passed there - then all list items
           are supposed to be validated by this validator
             If many validators were specified, then
           strict validation is performed, i.e.
           list must have strict length and strict order
           of elements.
        """
        self.__one_validator = False
        if getattr(validators, "validate", False):
            self.__one_validator = True
            self.validators = [validators]
        else:
            self.validators = validators

    def validate(self, data):
        """
        Validates data according to specified information on initializing this object.
        Returns True if data is valid, False otherwise.
        """
        if type(data) != type([]):
            return False
        if self.__one_validator:
            # validate all elements with only one validator
            for element in data:
                if not self.validators[0].validate(element):
                    return False
        elif not self.__one_validator and len(self.validators) > 0:
            # strict validation
            if len(self.validators) != len(data):
                return False
            for element,validator in zip(data, self.validators):
                if not validator.validate(element):
                    return False
        # if we don't have any validators set, just check types
        return True

    def __str__(self):
        return "List: validators: %s" % str(self.validators)


class Bool(object):
    """ Validates bool """
    def __init__(self, exact=None):
        """
        By default validates every bool.
        - 'exact': if exact is specified, then only specified
                   bool value will be validated.
        """
        self.exact = exact

    def validate(self, data):
        """
        Validates data according to specified information on initializing this object.
        Returns True if data is valid, False otherwise.
        """
        if type(data) != type(True):
            return False
        if self.exact is not None:
            return self.exact == data
        return True

    def __str__(self):
        return "Bool: exact: %s" % str(self.exact)


class Dict(object):
    """ Validates dictionaries """
    def __init__(self, validators={}, strict=True):
        """
        By default validates any dictionary.
        - 'validators': validators is a dictionary
                        where each key and value are
                        validators themself.
        - 'strict': bool, True by default. When True,
                    strict validation is performed, i.e.
                    data must have the same quantity of keys
                    as 'validators' specified previously,
                    plus only one validator is used per key.
                    When False, louse validation is performed,
                    i.e. one validator can validate as many keys
                    as possible.
        """
        self.validators = validators
        self.strict = strict

    def validate(self, data):
        """
        Validates data according to specified information on initializing this object.
        Returns True if data is valid, False otherwise.
        """
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
                is_valid_key = validator_key.validate(data_key)
                is_valid_value = validator_value.validate(data_value)
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
