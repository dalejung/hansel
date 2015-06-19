from six import iteritems, with_metaclass
import inspect
import uuid
import inspect
import datetime

class TraitError(Exception):
    pass

class KeyTypeError(TraitError):
    pass

def _get_name(trait, obj):
    classdict = obj.__class__.__dict__
    for k,v in iteritems(classdict):
        if v is trait:
            return k
    raise Exception("Could not find name")

class Trait:
    def __init__(self, **kwargs):
        self.value = None
        self.name = None

    def __get__(self, obj, cls=None):
        name = self.get_name(obj)
        return obj.__dict__.get(name, None)

    def __set__(self, obj, value):
        new_value = self._validate(obj, value)
        name = self.get_name(obj)
        obj.__dict__[name] = new_value

    def get_name(self, obj):
        if self.name is None:
            self.name = _get_name(self, obj)
        return self.name

    def _validate(self, obj, value):
        value = self.validate(obj, value)
        return value

    def validate(self, obj, value):
        return value

    def error(self, obj, value):
        class_name = type(self).__name__
        value_name = type(value).__name__
        msg = "TraitError: Required {class_name}. Got {value_name}".format(**locals())
        raise TraitError(msg)

class Unicode(Trait):
    pass

class Int(Trait):
    def __init__(self, min=None, max=None, **kwargs):
        self.min = min
        self.max = max
        super().__init__(**kwargs)

    def check_min(self, value):
        if self.min is None:
            return True
        return self.min <= value

    def check_max(self, value):
        if self.max is None:
            return True
        return self.max >= value

    def validate(self, obj, value):
        if isinstance(value, int) and self.check_min(value)\
            and self.check_max(value):
            return value
        self.error(obj, value)

class UUID(Trait):
    def validate(self, obj, value):
        if isinstance(value, uuid.UUID):
            return value
        self.error(obj, value)

class Datetime(Trait):
    def validate(self, obj, value):
        if isinstance(value, datetime.datetime):
            return value
        self.error(obj, value)

class Type(Trait):
    def __init__(self, _class, **kwargs):
        self.check_class = _class
        super().__init__(**kwargs)

    def validate(self, obj, value):
        if isinstance(value, self.check_class):
            return value
        self.error(obj, value)

def grab_class_reference(obj, class_name):
    """ Grab class ref from the module that object is defined in """
    modname = obj.__class__.__module__
    import sys
    mod = sys.modules[modname]
    check_class = getattr(mod, class_name, None)
    return check_class

class Collection(Trait):

    # TODO replace list with a type checking list
    container_class = list

    def __init__(self, _class, **kwargs):
        self._class = _class
        self.check_class = None
        if inspect.isclass(_class):
            self.check_class = _class
        super().__init__(**kwargs)

    def _check_container_class(self, value):
        if not isinstance(value, self.container_class):
            raise TraitError("Must be a {container_class}".format(
                container_class=str(self.container_class)
            ))

    def _check_collection_values(self, values):
        check_class = self.check_class
        for v in values:
            if not isinstance(v, check_class):
                raise TraitError("Collection can only contain {type}")

    def values(self, obj):
        return obj

    def validate(self, obj, value):
        if self.check_class is None:
            self.check_class = grab_class_reference(obj, self._class)

        self._check_container_class(value)
        self._check_collection_values(self.values(value))

        return value

class List(Collection):
    container_class = list

class Dict(Collection):
    container_class = dict

    def __init__(self, _class, **kwargs):
        self.key_class = kwargs.pop('key_class', None)
        super().__init__(_class, **kwargs)

    def values(self, obj):
        return obj.values()

    def _validate_keys(self, value):
        if self.key_class is None:
            return
        for k in value:
            if not isinstance(k, self.key_class):
                raise KeyTypeError("Keys must be {type} type".format(
                    type=str(self.key_class)
                ))

    def validate(self, obj, value):
        value = super().validate(obj, value)
        self._validate_keys(value)
        return value
