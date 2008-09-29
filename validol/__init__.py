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


TYPE_UNKNOWN = 0
TYPE_VALIDATOR = 1
TYPE_ITERABLE = 2
TYPE_REGEX = 3
TYPE_TYPE = 4
TYPE_DICTIONARY = 5
TYPE_OBJECT = 6


def kind_of(obj):
    if getattr(obj, "validate", False):
        return TYPE_VALIDATOR
    elif isinstance(obj, dict):
        return TYPE_DICTIONARY
    elif isinstance(obj, (tuple, list)):
        return TYPE_ITERABLE
    elif getattr(obj, "match", False) and getattr(obj, "search", False):
        return TYPE_REGEX
    elif obj in [str,unicode,int,bool,dict,float]:
        return TYPE_TYPE
    elif obj == object:
        return TYPE_OBJECT
    else:
        return TYPE_UNKNOWN

def validate(scheme, data):
    return validate_common(scheme, data)

def validate_common(validator, data):
    kind = kind_of(validator)
    if kind == TYPE_VALIDATOR:
        if validator.validate(data):
            return True
    elif kind == TYPE_REGEX:
        if validator.match(data):
            return True
    elif kind == TYPE_DICTIONARY:
        return validate_hash(validator, data)
    elif kind == TYPE_ITERABLE:
        return validate_list(validator, data)
    elif kind == TYPE_UNKNOWN:
        if data == validator:
            return True
    elif kind == TYPE_OBJECT:
        return True
    elif kind == TYPE_TYPE:
        # workaround for bool, because bool is a subclass of int
        if type(data) == bool:
            if type(data) == validator:
                return True
        elif isinstance(data, validator):
            return True
    return False

def validate_list(validator, data):
    if not isinstance(data, (tuple, list)):
        return False
    if len(validator) == 0:
        return len(data) == 0
    if len(validator) == 1:
        for item in data:
            if not validate_common(validator[0], item):
                return False
    elif len(validator) > 1:
        raise NotImplementedError, "You cannot specify more than one validator for list at the moment."
    return True

def validate_hash(validator, data):
    if not isinstance(data, dict):
        return False
    if validator == {} and data == {}:
        return True
    used_validators = []
    for data_key, data_value in data.iteritems():
        data_valid = False
        for validator_key, validator_value in validator.iteritems():
            if validator_key in used_validators:
                continue
            is_valid_key = validate_common(validator_key, data_key)
            is_valid_value = validate_common(validator_value, data_value)
            if is_valid_key and is_valid_value:
                if not isinstance(validator_key, Many):
                    used_validators.append(validator_key)
                data_valid = True
        if not data_valid:
            return False
    return True


class AnyOf(object):
    def __init__(self, validators=[]):
        self.validators = validators

    def validate(self, data):
        for validator in self.validators:
            ret = validate_common(validator, data)
            if ret:
                return True
        return False

    def __str__(self):
        return "AnyOf: validators: %s" % str(self.validators)


class Many(object):
    def __init__(self, data):
        self.data = data

    def validate(self, data):
        return validate_common(self.data, data)
