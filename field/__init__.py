#!/usr/bin/env python3
# 0004

from typing import Any, Callable

__all__ = [
    'field',
    'check',
]


class field:
    '''
    A property-like entity that represents a class field.
    Neither "__get__" nor "__set__" can be overridden. The assigned
    value is kept and returned "as is". The underlying attribute is
    an implementation detail. To enforce value restrictions, the "check"
    decorator is supposed to be used.
    '''

    def __init__(self, v: 'Any' = ...) -> 'None':
        '''
        * v - an initial value for the field. It does not trigger any checks.
        '''
        self._v = v
        self._name: 'str' = None
        self._attr: 'str' = None
        self._checks: 'list[check]' = []

    def __get__(self, o: 'object', t: 'type | None' = None) -> 'Any':
        '''
        * 0000: Returns a custom value prior to the first assignment.
        * 0001: Returns "..." prior to the first assignment by default.
        * 0002: Returns the value exactly as it was assigned.
        '''
        self.__once__(o)
        if not hasattr(o, self._attr):
            return self._v
        return getattr(o, self._attr)

    def __set__(self, o: 'object', v: 'Any') -> 'None':
        '''
        * 0003: Calls all associated checks.
        '''
        self.__once__(o)
        for x in self._checks:
            (x._f)(o, self._name, v)
        setattr(o, self._attr, v)

    def __once__(self, o: 'object') -> 'None':
        if not self._name:
            for k, v in o.__class__.__dict__.items():
                if self is v:
                    self._name = k
                    self._attr = f'/attr/{k}'
                    return


class check:
    '''
    A decorator entity that is used for "field" validations.
    Whenever a "field" is assigned it will call all its associated
    "check" methods.
    The decorated method must take 3 positional arguments:
    1. "self" (naturally);
    2. A name of the field that is about to be assigned.
    3. A new value that is about to be assigned.
    The method should return "None".
    The method is supposed to raise an error if the validation fails.
    '''

    def __init__(self, *attr: 'field') -> 'None':
        '''
        * attr - "field" instances that are checked via the method.
                 The method is called whenever one of them is assigned.
        '''
        self._f = None
        for x in attr:
            x._checks.append(self)

    def __call__(self, f: 'Callable[[object, str, Any], None]') -> 'None':
        self._f = f
