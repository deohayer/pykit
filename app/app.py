#!/usr/bin/env python3

from typing import Callable, Iterable

__all__ = [
    'Arg',
    'App',
    'Bundle',
    'ArgappError',
]


class Arg:
    def __init__(
        self,
        name: str,
        options: 'str | Iterable[str]' = None,
        metavar: str = None,
        valtype: type = None,
        default: object = None,
        choices: Iterable = None,
        count: 'int | str' = None,
        required: bool = None,
        help: str = None,
    ) -> None:
        self.name = name
        self.options = options
        self.metavar = metavar
        self.type = valtype
        self.default = default
        self.choices = choices
        self.count = count
        self.required = required
        self.help = help


class App:
    def __init__(
        self,
        name: str = None,
        brief: str = None,
        prolog: str = None,
        epilog: str = None,
        run: 'Callable[[App, Bundle], int]' = None,
        args: 'list[Arg]' = None,
        apps: 'list[App]' = None,
    ) -> None:
        self.name = name
        self.brief = brief
        self.prolog = prolog
        self.epilog = epilog
        self.run = run
        self.args = args or []
        self.apps = apps or []


class Bundle:
    def __init__(
        self,
        apps: 'list[App]',
        args: 'dict[Arg, object]',
    ) -> None:
        self.args = args
        self.apps = apps


class ArgappError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
