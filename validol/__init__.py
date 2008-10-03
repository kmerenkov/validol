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
TYPE_LIST = 2
TYPE_REGEX = 3
TYPE_TYPE = 4
TYPE_DICTIONARY = 5
TYPE_OBJECT = 6
TYPE_TUPLE = 7


def kind_of(obj):
    if getattr(obj, "validate", False):
        return TYPE_VALIDATOR
    elif isinstance(obj, dict):
        return TYPE_DICTIONARY
    elif isinstance(obj, list):
        return TYPE_LIST
    elif isinstance(obj, tuple):
        return TYPE_TUPLE
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
    elif kind == TYPE_LIST:
        return validate_list(validator, data)
    elif kind == TYPE_TUPLE:
        return validate_tuple(validator, data)
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


def validate_tuple(validator, data):
    if not isinstance(data, tuple):
        return False
    if len(validator) != len(data):
        return False
    for v,d in zip(validator, data):
        if not validate_common(v, d):
            return False
    return True

def validate_list(validator, data):
    if not isinstance(data, list):
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
    if validator == data == {}: # empty data hash corresponds to empty scheme hash
        return True
    if validator == {} and data != {}:
        return False
    if validator != {} and data == {}:
        return False
    used_validators = []
    valid_data_count = 0
    used_many_validators = 0
    for data_key, data_value in data.iteritems():
        data_valid = False
        for validator_key, validator_value in validator.iteritems():
            if validator_key in used_validators:
                continue
            is_valid_key = validate_common(validator_key, data_key)
            is_valid_value = validate_common(validator_value, data_value)
            if is_valid_key and is_valid_value:
                valid_data_count += 1
                if not isinstance(validator_key, Many):
                    used_validators.append(validator_key)
                else:
                    used_many_validators += 1
                data_valid = True
                break
        if not data_valid:
            return False
    declared_many_validator_count = len(filter(lambda x: isinstance(x, Many), validator.keys()))
    unused_notmany_validator_count = len(filter(lambda x: x not in used_validators, validator.keys()))
    return unused_notmany_validator_count == declared_many_validator_count


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
