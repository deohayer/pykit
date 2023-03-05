#!/usr/bin/env python3

from typing import Any
from pytest import raises

from . import *


class MyClass:
    a: int = field()
    b: int = field(0)

    @check(a, b)
    def validate(self, n: 'str', v: 'Any') -> 'None':
        a = v if n == 'a' else self.a
        b = v if n == 'b' else self.b
        if a == b:
            raise ValueError('a must not be equal to b!')


def test_0000():
    o = MyClass()
    assert o.b == 0


def test_0001():
    o = MyClass()
    assert o.a == ...


def test_0002():
    o = MyClass()
    o.a = 4
    assert o.a == 4


def test_0003():
    o = MyClass()
    with raises(ValueError):
        o.a = 5
        o.b = 5
