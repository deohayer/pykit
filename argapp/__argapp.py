#!/usr/bin/env python3

import os
import argparse as ap
import argcomplete as ac
from typing import *

__all__ = [
    'Arg',
    'App',
    'Bundle',
    'main',
]


# The following are called before parsing the command line (Arg, App):
#   help - generate a help message.
# The following are called after parsing the command line (Arg, App, Bundle):
#   default - set a value for a non-set arg.
#   evaluate - post-process a value of an already set arg.
class Arg:
    FValue = Callable[[Any, 'Arg', 'App', 'Bundle'], Any]
    FHelp = Callable[['Arg', 'App'], str]

    def __init__(
        self,
        name: str,
        options: str = None,
        display: str = None,
        type: type = None,
        choices: Iterable = None,
        count: int | str = None,
        default: Any | FValue = None,
        evaluate: Any | FValue = None,
        help: str | FHelp = None,
    ) -> None:
        self.name = name
        self.options = options
        self.display = display
        self.type = type
        self.choices = choices
        self.count = count
        self.default = default
        self.evaluate = evaluate
        self.help = help


class App:
    FRun = Callable[['Bundle', int], int]
    FHelp = Callable[['App'], str]

    def __init__(
        self,
        name: str,
        brief: str | FHelp = None,
        prolog: str | FHelp = None,
        epilog: str | FHelp = None,
        run: 'App.FRun' = None,
        args: List['Arg'] = None,
        apps: List['App'] = None,
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
        args: Dict['Arg', Any],
        apps: list['App'],
    ) -> None:
        self.args = args
        self.apps = apps


def main(app: 'App') -> int:
    return 0


##############################################################################

class ParserApp:
    def __init__(
        self,
        app: 'App',
        parent: 'ParserApp' = None,
    ) -> None:
        self.__app = app
        self.__parent = parent
        self.__children: List['ParserApp'] = []
        for app in self.apps():
            self.__children.append(ParserApp(app, self))
        self.__parser = None

    #
    # ParserApp fields.
    #

    def app(self) -> 'App':
        return self.__app

    def parent(self) -> 'ParserApp':
        return self.__parent

    def children(self) -> List['ParserApp']:
        return self.__children

    def parser(self) -> ap.ArgumentParser:
        return self.__parser

    #
    # Evaluated fields of the underlying App.
    #

    def name(self) -> str:
        return self.app().name

    def brief(self) -> str:
        return self.__help(self.app().brief)

    def prolog(self) -> str:
        return self.__help(self.app().prolog)

    def epilog(self) -> str:
        return self.__help(self.app().epilog)

    def apps(self) -> List['App']:
        return self.app().apps

    def args(self) -> List['Arg']:
        return self.app().args

    def run(
        self,
        bundle: 'Bundle',
        index: int,
    ) -> int:
        if not self.app().run:
            return 0
        return (self.app().run)(bundle, index)

    def __help(
        self,
        help: str | App.FHelp,
    ) -> str:
        if callable(help):
            return help(self.app())
        else:
            return help

    #
    # Construct ParserApp-s.
    #

    def construct_apps(self) -> None:
        if not self.parser():
            self.__parser = self.construct_parser(None)
        if not self.children():
            return
        subparsers = self.construct_subparsers()
        for child in self.children():
            child.__parser = child.construct_parser(subparsers)
            child.construct_apps()

    def construct_subparsers(self) -> Any:
        return self.parser().add_subparsers(
            dest=self.construct_subparsers_name(),
            help=self.construct_subparsers_help(),
            metavar='APP',
            required=True,
        )

    def construct_parser(self, subparsers) -> ap.ArgumentParser:
        kwargs = {
            'prog': self.name(),
            'description': self.prolog(),
            'epilog': self.epilog(),
            'formatter_class': ap.RawTextHelpFormatter,
        }
        if subparsers:
            return subparsers.add_parser(kwargs)
        return ap.ArgumentParser(kwargs)

    def construct_subparsers_name(self) -> str:
        papp = self
        name = f'{self.name()}_cmd'
        while papp.parent():
            papp = papp.parent()
            name = f'{papp.name()}_{name}'
        return name

    def construct_subparsers_help(self) -> str:
        help = 'One of the following:'
        for child in self.children():
            brief = child.brief()
            brief = f' - {brief}' if brief else ''
            help = f'{help}\n  {child.name()}{brief}'
        return help

    #
    # Construct ParserArg-s.
    #

    def construct_args(self) -> None:
        pass

    #
    # Parsing.
    #

    def parse(self) -> 'Bundle':
        return None


def main(app: App) -> int:
    papp = ParserApp(app)
    ac.autocomplete(
        papp.parser(),
        always_complete_options=False,
    )
    bundle = papp.parse()
    # counter = 0
    # capp = papp
    # while counter < len(bundle.apps):
    #     code = capp.run(bundle)
    #     if code:
    #         return code
    #     counter += 1
    #     name = bundle.apps[counter].name
    #     for child in capp.children():
    #         if child.name() == name:
    #             capp = child
    #             continue
    #     # Should not happen - argparse takes care of this.
    #     raise ValueError(
    #         f'argapp: Unknown App {name}. Call stack: {bundle.apps}'
    #     )
    return 0
