#!/usr/bin/env python3

from typing import *

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
        options: str | Iterable[str] = None,
        display: str = None,
        type: type = None,
        default: object | Callable[['Arg', 'App', 'Bundle'], object] = None,
        choices: Iterable = None,
        count: int | str = None,
        help: str = None,
        evaluate: Callable[[object, 'Arg', 'App', 'Bundle'], object] = None,
    ) -> None:
        self.name = name
        self.options = options
        self.display = display
        self.type = type
        self.default = default
        self.choices = choices
        self.count = count
        self.help = help
        self.evaluate = evaluate


class App:
    def __init__(
        self,
        name: str,
        brief: str = None,
        prolog: str = None,
        epilog: str = None,
        run: Callable[['App', 'Bundle'], int] = None,
        args: list['Arg'] = None,
        apps: list['App'] = None,
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
        args: dict['Arg', object],
        apps: list['App'],
    ) -> None:
        self.args = args
        self.apps = apps


class ArgappError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
