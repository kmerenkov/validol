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


__version__ = "0.2" # XXX Not always updated :\
__author__  = "Konstantin Merenkov <kmerenkov@gmail.com>"


from itertools import imap


TYPE_UNKNOWN = 0
TYPE_VALIDATOR = 1
TYPE_LIST = 2
TYPE_REGEX = 3
TYPE_TYPE = 4
TYPE_DICTIONARY = 5
TYPE_OBJECT = 6
TYPE_TUPLE = 7
TYPE_FUNCTION = 8

ATOMIC_TYPES = set([str, unicode, int, bool, float])


class BaseValidator(object):
    """
    All other validators inherit this baseclass. You want to use this class
    only if you write your own validator, otherwise you should not care
    about it.

    Call to validate method results in NotImplementedError exception.

    >>> BaseValidator().validate("foo")
    Traceback (most recent call last):
    ...
    NotImplementedError: Inherit this class and override this method.
    """

    def validate(self, data):
        """
        For all validators this function validates data and returns True if data
        is found to be valid, False otherwise.
        For this base class this function throws NotImplementedError.
        """
        raise NotImplementedError("Inherit this class and override this method.")

    def __repr__(self):
        return str(self)


def kind_of(obj):
    """
    Finds out what kind of object we have on hands.
    For example, dicts, lists, and tuples have complex validation,
    while str, int, float, and bool have simple validation, that looks like (!):

    if (type(data) is some_type_mentioned_above):
        return True

    Be careful with objects, because in validol object means "I don't care"
    and matches anything at all.

    >>> kind_of({'a': 'b'}) == TYPE_DICTIONARY
    True
    >>> kind_of([1,2,3]) == TYPE_LIST
    True
    >>> kind_of((1,2)) == TYPE_TUPLE
    True
    >>> kind_of(int) == TYPE_TYPE
    True
    >>> kind_of(object) == TYPE_OBJECT
    True
    >>> import re
    >>> kind_of(re.compile('foo')) == TYPE_REGEX
    True
    >>> kind_of(BaseValidator()) == TYPE_VALIDATOR
    True
    >>> kind_of(42) == TYPE_UNKNOWN
    True
    >>> kind_of(lambda x: "123") == TYPE_FUNCTION
    True
    """
    # why don't I use isinstance - it saves us big time

    # dict, list, and tuple are differianted from str, unicode, int, bool, and float
    # because they have special treatment and simple `==` or `is` is not enough to
    # prove them valid.
    obj_type = type(obj)
    if obj_type is dict:
        return TYPE_DICTIONARY
    elif obj_type is list:
        return TYPE_LIST
    elif obj_type is tuple:
        return TYPE_TUPLE
    elif obj in ATOMIC_TYPES:
        return TYPE_TYPE
    elif obj is object:
        return TYPE_OBJECT
    elif getattr(obj, "__class__", False) and issubclass(obj.__class__, BaseValidator):
        return TYPE_VALIDATOR
    elif callable(obj):
        return TYPE_FUNCTION
    # this f##king SRE_Pattern, why can't I f##king kill it
    elif getattr(obj, "match", False) and getattr(obj, "search", False):
        return TYPE_REGEX
    else:
        return TYPE_UNKNOWN

def validate(scheme, data):
    """
    Validates data against scheme. Returns True if data
    found to be valid, False otherwise.

    >>> validate(1, 1) # validate simple data
    True
    >>> validate('foo', 'bar') # two different strings are not equal
    False
    >>> validate({'a': int, 'b': int}, {'a': 10, 'b': 20}) # more difficult example
    True
    >>> validate(lambda x: x > 10, 5)
    False
    >>> validate(lambda x: x > 10, 20)
    True
    """
    return validate_common(scheme, data)

def validate_common(validator, data):
    kind = kind_of(validator)
    if kind == TYPE_VALIDATOR:
        if validator.validate(data):
            return True
    elif kind == TYPE_FUNCTION:
        try:
            if validator(data):
                return True
        except:
            return False
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
        return data == validator
    elif kind == TYPE_OBJECT:
        # NOTE In validol 'object' means anything,
        # so it is always valid. It is like specifying .* in re
        return True
    elif kind == TYPE_TYPE:
        return type(data) == validator
    return False

def validate_tuple(validator, data):
    """
    >>> validate_tuple((int, int), (1, 2))
    True
    >>> validate_tuple((int, str), (1, 2))
    False
    >>> validate_tuple((int,), 'foo')
    False
    """
    if type(data) is not tuple:
        return False
    if len(validator) != len(data):
        return False
    # all elements must be valid
    return all(imap(validate_common, validator, data))

def validate_list(validators, data):
    """
    >>> validate_list([int], range(10))
    True
    >>> validate_list([int], 'foo')
    False
    >>> validate_list([str], 'foo')
    False
    >>> validate_list([str], ['foo'])
    True
    >>> validate_list([str, str], ['foo'])
    Traceback (most recent call last):
    ...
    NotImplementedError: You cannot specify more than one validator for list at the moment.
    """
    if type(data) is not list:
        return False
    n_validators = len(validators)
    if n_validators == 0:
        return len(data) == 0
    elif n_validators == 1:
        validator = validators[0]
        return all(imap(lambda item: validate_common(validator, item), data))
    elif n_validators > 1:
        raise NotImplementedError("You cannot specify more than one validator for list at the moment.")

def validate_hash(validator, data):
    if type(data) is not dict:
        return False
    if validator == data == {}:
        return True
    if validator == {} and data != {}:
        return False
    optional_validators = {}
    many_validators = {}
    for v_key, v_val in validator.iteritems():
        if type(v_key) is Optional:
            optional_validators[v_key] = v_val
        else:
            many_validators[v_key] = v_val
    if optional_validators:
        ret_with_optional, passed_optional_data_keys = validate_hash_with_optional(optional_validators,
                                                                                   data)
        if not ret_with_optional: # optional validation has failed
            return False
    else:
        ret_with_optional = True # we don't have optional keys, that's okay

    new_data = {}
    if optional_validators and passed_optional_data_keys != set():
        new_data = dict(filter(lambda item: item[0] not in passed_optional_data_keys,
                               data.iteritems()))
    else:
        new_data = data
    ret_with_many = validate_hash_with_many(many_validators, new_data)
    return ret_with_many and ret_with_optional

def validate_hash_with_optional(validator, data):
    validator = dict(validator) # copy validator because later we modify it (pop keys out)
    valid_data_keys = set()
    validator_count = len(validator)
    used_validators_count = 0
    for data_key, data_value in data.iteritems():
        for validator_key, validator_value in validator.iteritems():
            if validate_common(validator_key, data_key):
                if validate_common(validator_value, data_value):
                    valid_data_keys.add(data_key)
                    validator.pop(validator_key) # we don't need this validator in future
                    used_validators_count += 1
                    # exhausted all optional validators, good sign
                    if used_validators_count == validator_count:
                        return (True, valid_data_keys)
                    break
                else:
                    return (False, {})
    return (True, valid_data_keys)

def validate_hash_with_many(validator, data):
    if validator != {} and data == {}:
        return False
    orig_validator = validator
    copy_validator = dict(validator)
    for data_key, data_value in data.iteritems():
        data_valid = False
        for validator_key, validator_value in copy_validator.iteritems():
            if validate_common(validator_key, data_key) and \
                    validate_common(validator_value, data_value):
                if type(validator_key) is not Many:
                    copy_validator.pop(validator_key)
                data_valid = True
                break
        if not data_valid:
            return False
    # count Many validators
    declared_many_validator_count = len(filter(lambda v: type(v) is Many,
                                               orig_validator.keys()))
    # count "unused" validators (Many validators aren't marked as used)
    unused_notmany_validator_count = len(filter(lambda v: v in copy_validator,
                                                orig_validator.keys()))
    # their quantity must be equal for data to be proven valid
    return unused_notmany_validator_count == declared_many_validator_count


class AnyOf(BaseValidator):
    """
    Validates if data matches at least one of specified schemes.

    >>> AnyOf(1, 2, 3).validate(1) # 1 or 2 or 3
    True
    >>> AnyOf(1, 2, 3).validate(2)
    True
    >>> AnyOf(1, 2, 3).validate(10)
    False
    """
    def __init__(self, *validators):
        self.validators = validators

    def validate(self, data):
        """ returns True if data is valid for at least one validator. """
        return any(imap(lambda validator: validate_common(validator, data), self.validators))

    def __str__(self):
        return "<AnyOf: '%s'>" % str(self.validators)


class Many(BaseValidator):
    """
    BIG FAT WARNING: Useful only for dict validation. In fact all it does is simple
    1-to-1 comparison, i.e. same as validate(X, X)  where X is some exact value.

    Validates if one or more occurences of data match specified scheme.

    >>> Many('foo').validate('foo')
    True
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
    When used anywhere else, validates data if data is None or if data is valid.

    >>> Optional('foo').validate(None)
    True
    >>> Optional('foo').validate('foo')
    True
    >>> Optional('foo').validate('bar')
    False
    """
    def __init__(self, data):
        self.data = data

    def validate(self, data):
        return data is None or validate_common(self.data, data)

    def __str__(self):
        return "<Optional: '%s'>" % str(self.data)


class Text(BaseValidator):
    """
    Passes on any textual data (be it str or unicode).
    """
    def __init__(self):
        pass

    def validate(self, data):
        # I could do isinstance(data, basestring) but I remember it to be slow.
        # Not sure if the code below is any faster :)
        return AnyOf(str, unicode).validate(data)


class Scheme(AnyOf):
    """
    This class exist to make raw structure have type (type of Scheme).
    Often it is useful, often it is not - depends on your needs.
    Behaves exactly as AnyOf, except has different str and repr methods.
    """
    def __str__(self):
        return "<Scheme: '%s'>" % str(self.validators)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
