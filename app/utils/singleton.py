import abc


class Singleton(abc.ABCMeta, type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        key = (cls, args, frozenset(kwargs.items()))
        if key not in cls._instances:
            cls._instances[key] = super().__call__(*args, **kwargs)
        return cls._instances[key]
