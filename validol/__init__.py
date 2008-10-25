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


class BaseValidator(object):
    def validate(self, data):
        raise NotImplementedError("Inherit this class and override this method.")

    def __repr__(self):
        return str(self)


def kind_of(obj):
    # why don't I use isinstance - it saves us big time
    if type(obj) == dict:
        return TYPE_DICTIONARY
    elif type(obj) == list:
        return TYPE_LIST
    elif type(obj) == tuple:
        return TYPE_TUPLE
    elif obj in [str,unicode,int,bool,dict,float]:
        return TYPE_TYPE
    elif obj == object:
        return TYPE_OBJECT
    elif getattr(obj, "__class__", False) and issubclass(obj.__class__, BaseValidator):
        return TYPE_VALIDATOR
    # this f##king SRE_Pattern, why can't I f##king kill it
    elif getattr(obj, "match", False) and getattr(obj, "search", False):
        return TYPE_REGEX
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
        if type(data) == validator:
            return True
    return False

def validate_tuple(validator, data):
    if type(data) != tuple:
        return False
    if len(validator) != len(data):
        return False
    for v,d in zip(validator, data):
        if not validate_common(v, d):
            return False
    return True

def validate_list(validator, data):
    if type(data) != list:
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
    if type(data) != dict:
        return False
    if validator == data == {}:
        return True
    if validator == {} and data != {}:
        return False
    optional_validators = {}
    many_validators = {}
    for v_key, v_val in validator.iteritems():
        if type(v_key) == Optional:
            optional_validators[v_key] = v_val
        else:
            many_validators[v_key] = v_val
    if optional_validators:
        ret_with_optional, passed_optional_data_keys = validate_hash_with_optional(optional_validators, data)
    else:
        ret_with_optional = True # we don't have optional keys, that's okay

    if optional_validators and passed_optional_data_keys != {}:
        new_data = {}
        for data_key, data_value in data.iteritems():
            if not passed_optional_data_keys.has_key(data_key):
                new_data[data_key] = data_value
    else:
        new_data = data
    if many_validators:
        ret_with_many = validate_hash_with_many(many_validators, new_data)
    else:
        ret_with_many = True
    return ret_with_many and ret_with_optional

def validate_hash_with_optional(validator, data):
    valid_data_keys = {} # speed again
    for validator_key, validator_value in validator.iteritems():
        for data_key, data_value in data.iteritems():
            is_valid_key = validate_common(validator_key, data_key)
            if is_valid_key:
                is_valid_value = validate_common(validator_value, data_value)
                if is_valid_value:
                    valid_data_keys[data_key] = None
                else:
                    return (False, {})
    return (True, valid_data_keys)

def validate_hash_with_many(validator, data):
    if validator != {} and data == {}:
        return False
    used_validators = {} # great speed in comparison with lists
    valid_data_count = 0
    used_many_validators = 0
    for data_key, data_value in data.iteritems():
        data_valid = False
        for validator_key, validator_value in validator.iteritems():
            if used_validators.has_key(validator_key):
                continue
            is_valid_key = validate_common(validator_key, data_key)
            if is_valid_key:
                is_valid_value = validate_common(validator_value, data_value)
                if is_valid_value:
                    valid_data_count += 1
                    if type(validator_key) == Many:
                        used_many_validators += 1
                    else:
                        used_validators[validator_key] = None
                    data_valid = True
                    break
        if not data_valid:
            return False
    declared_many_validator_count = 0
    unused_notmany_validator_count = 0
    for validator in validator.keys():
        if type(validator) == Many:
            declared_many_validator_count += 1
        if not used_validators.has_key(validator):
            unused_notmany_validator_count += 1
    return unused_notmany_validator_count == declared_many_validator_count


class AnyOf(BaseValidator):
    """
    Validates if data matches at least one scheme passed to AnyOf constructor.
    """
    def __init__(self, *validators):
        self.validators = validators

    def validate(self, data):
        for validator in self.validators:
            if validate_common(validator, data):
                return True
        return False

    def __str__(self):
        return "<AnyOf: '%s'>" % str(self.validators)


class Many(BaseValidator):
    """
    Validates if one or more occurences of data match scheme.
    """
    def __init__(self, data):
        self.data = data

    def validate(self, data):
        return validate_common(self.data, data)

    def __str__(self):
        return "<Many: '%s'>" % str(self.data)


class Optional(BaseValidator):
    """
    When used as a key for hash, validates data if data matches scheme or if key is absent from hash.
    When used anywehre else, validates data if data is None or if data is valid.
    """
    def __init__(self, data):
        self.data = data

    def validate(self, data):
        return data is None or validate_common(self.data, data)

    def __str__(self):
        return "<Optional: '%s'>" % str(self.data)


class Scheme(AnyOf):
    """
    This class exist to make raw structure have type (type of Scheme).
    """
    def __str__(self):
        return "<Scheme: '%s'>" % str(self.validators)
