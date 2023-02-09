#!/usr/bin/env python3

import re
import argparse
from typing import *

from entities import *


RE_NAME = '^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
RE_SOPT = '^[-][a-zA-Z]$'
RE_LOPT = '^[-][-][a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
RE_COUNT = '^[?*+]$'


class ParserError(Exception):
    def __init__(
        self,
        origin: 'ParserApp' | 'ParserArg' | 'Parser',
        message: str,
    ) -> None:
        message = f'argapp: {ParserError.prefix(origin)}: {message}'
        super().__init__(message)
        self.message = message

    @staticmethod
    def prefix(origin: 'ParserApp' | 'ParserArg' | 'Parser') -> str:
        if isinstance(origin, ParserArg):
            return ParserError.prefix_parg(origin)
        elif isinstance(origin, ParserApp):
            return ParserError.prefix_papp(origin)
        elif isinstance(origin, Parser):
            return ParserError.prefix_prsr(origin)
        else:
            return str(origin)

    @staticmethod
    def prefix_parg(parg: 'ParserArg') -> str:
        str_papp = ParserError.prefix_papp(parg.papp())
        str_parg = ParserError.prefix_parg_name(parg)
        return f'{str_papp}.{str_parg}'

    @staticmethod
    def prefix_papp(papp: 'ParserApp') -> str:
        names = []
        while papp:
            names.insert(0, ParserError.prefix_papp_name(papp))
            papp = papp.parent()
        return '/'.join(names)

    @staticmethod
    def prefix_prsr(prsr: 'Parser') -> str:
        return 'parser'

    @staticmethod
    def prefix_papp_name(papp: 'ParserApp') -> str:
        name = papp.app().name
        if isinstance(name, str) and name:
            return name
        return f'App{papp.locate()}'

    @staticmethod
    def prefix_parg_name(parg: 'ParserArg') -> str:
        name = parg.arg().name
        if isinstance(name, str) and name:
            return name
        return f'Arg{parg.locate()}'


class ParserArg:
    def __init__(
        self,
        arg: 'Arg',
        papp: 'ParserApp',
    ) -> None:
        self.__arg = arg
        self.__papp = papp

    #
    # Non-specific interface.
    #

    def arg(self) -> 'Arg':
        return self.__arg

    def app(self) -> 'App':
        return self.papp().app()

    def papp(self) -> 'ParserApp':
        return self.__papp

    def locate(self) -> int:
        return self.papp().pargs().index(self)

    #
    # Validators.
    #

    def validate(self) -> None:
        self.validate_name()
        self.validate_options()
        self.validate_display()
        self.validate_type()
        self.validate_default()
        self.validate_choices()
        self.validate_count()
        self.validate_help()
        self.validate_evaluate()

    def validate_name(self) -> None:
        MESS_TYPE = 'Arg.name must be a non-empty str.'
        MESS_VAL = \
            'Arg.name must consist of letters (a-z, A-Z), numbers (0-9), ' \
            'dashes (-), or underscores (_). The first character must be ' \
            'a letter, the last - a leter or a number.'
        v = self.arg().name
        if not v or not isinstance(v, str):
            raise ParserError(self, MESS_TYPE)
        if not re.match(RE_NAME, v):
            raise ParserError(self, MESS_VAL)

    def validate_options(self) -> None:
        MESS_TYPE = 'Arg.option must be None, str or Iterable.'
        MESS_VAL = 'Each option must have at least two characters.'
        MESS_SVAL = \
            'A short option must consist of a dash (-) followed by a letter ' \
            '(a-z, A-Z).'
        MESS_LVAL = \
            'A long option must consist of letters (a-z, A-Z), numbers ' \
            '(0-9), dashes (-), or underscores (_). It must start with "--"' \
            'following by a letter. the last character must be a leter or a ' \
            'number.'
        v = self.arg().options
        if v == None:
            return
        if isinstance(v, str):
            v = [v]
        if not isinstance(v, Iterable):
            raise ParserError(self, MESS_TYPE)
        counter = 0
        for item in v:
            prefix = f'Invalid option {counter}. '
            if len(item) < 2:
                raise ParserError(self, prefix + MESS_VAL)
            elif len(item) == 2 and not re.match(RE_SOPT, item):
                raise ParserError(self, prefix + MESS_SVAL)
            elif len(item) > 2 and not re.match(RE_LOPT, item):
                raise ParserError(self, prefix + MESS_LVAL)
            counter += 1

    def validate_display(self) -> None:
        MESS_TYPE = 'Arg.option must be None or str.'
        MESS_VAL = \
            'Arg.display must consist of letters (a-z, A-Z), numbers (0-9), ' \
            'dashes (-), or underscores (_).'
        v = self.arg().display
        if v == None or v == '':
            return
        if not isinstance(v, str):
            raise ParserError(self, MESS_TYPE)
        if not re.match(RE_NAME, v):
            raise ParserError(self, MESS_VAL)

    def validate_type(self) -> None:
        MESS_TYPE = 'Arg.type must be None or type.'
        v = self.arg().type
        if v == None or isinstance(v, type):
            return
        raise ParserError(self, MESS_TYPE)

    def validate_default(self) -> None:
        'Arg.default must be None, Callable.'
        v = self.arg().default
        if v == None or isinstance(v, Callable):
            return
        # Get type.
        itemtype = self.arg().type
        # If type is None, determine it from choices.
        choices = self.arg().choices or []
        for item in choices:
            itemtype = itemtype or type(item)
            return
        # If type is None, fallback to object.
        itemtype = itemtype or object
        mess = f'Arg.default must be None, Callable or {itemtype.__name__}.'
        if not isinstance(v, itemtype):
            raise ParserError(self, mess)

    def validate_choices(self) -> None:
        MESS_TYPE = 'Arg.choices must be None or Iterable.'
        v = self.arg().choices
        if v == None:
            return
        if not isinstance(v, Iterable):
            raise ParserError(self, MESS_TYPE)
        # Get type.
        itemtype = self.arg().type
        # If type is None, get it from default.
        default = self.arg().default
        if self.arg().default and not isinstance(default, Callable):
            itemtype = itemtype or type(default)
        # Check if all items are of the same type.
        counter = 0
        for item in v:
            # If type is still None, get it from the first item.
            itemtype = itemtype or type(item)
            mess = f'Choice {counter} is not {itemtype.__name__}.'
            if not isinstance(type(item), itemtype):
                raise ParserError(self, mess)
            counter += 1

    def validate_count(self) -> None:
        MESS_TYPE = 'Arg.count must be None, int or str.'
        MESS_IVAL = 'Arg.count as int must have a non-negative value.'
        MESS_SVAL = \
            'Arg.count as str must be "+" (1 or more), "*" (0 or more) ' \
            'or "?" (0 or 1).'
        v = self.arg().count
        if v == None:
            return
        if isinstance(v, int):
            if v < 0:
                raise ParserError(self, MESS_IVAL)
            return
        if isinstance(v, str):
            if not re.match(RE_COUNT, v):
                raise ParserError(self, MESS_SVAL)
            return
        raise ParserError(self, MESS_TYPE)

    def validate_help(self) -> None:
        MESS_TYPE = 'Arg.help must be None or str.'
        v = self.arg().help
        if v == None or isinstance(v, str):
            return
        raise ParserError(self, MESS_TYPE)

    def validate_evaluate(self) -> None:
        MESS_TYPE = 'Arg.evaluate must be None or Callable.'
        v = self.arg().evaluate
        if v == None or isinstance(v, Callable):
            return
        raise ParserError(self, MESS_TYPE)

    #
    # Parameters.
    #

    #
    # Evaluation.
    #

    def default():
        pass

    def evaluate():
        pass


class ParserApp:
    def __init__(
        self,
        app: 'App',
        parent: 'ParserArg',
    ) -> None:
        self.__app = app
        self.__parent = parent
        self.__pargs = [ParserArg(x, self) for x in self.args()]
        self.__papps = [ParserApp(x, self) for x in self.apps()]

    #
    # Non-specific interface.
    #

    def app(self) -> 'App':
        return self.__app

    def args(self) -> List['Arg']:
        return self.__app.args

    def pargs(self) -> List['ParserArg']:
        return self.__pargs

    def apps(self) -> List['App']:
        return self.__app.apps

    def papps(self) -> List['ParserApp']:
        return self.__papps

    def parent(self) -> 'ParserApp':
        return self.__parent

    def root(self) -> 'ParserApp':
        current = self
        while not self.is_root():
            current = current.parent()
        return current

    def is_root(self) -> bool:
        return not self.parent()

    def locate(self) -> int:
        if self.is_root():
            return 0
        return self.parent().papps().index(self)


class Parser:
    pass

# class ParserApp:
#     def __init__(
#         self,
#         app: 'App',
#         parent: 'ParserApp' = None,
#     ) -> None:
#         self.__app = app
#         self.__parent = parent
#         self.__children: List['ParserApp'] = []
#         for app in self.apps():
#             self.__children.append(ParserApp(app, self))
#         self.__parser = None

#     #
#     # ParserApp fields.
#     #

#     def app(self) -> 'App':
#         return self.__app

#     def parent(self) -> 'ParserApp':
#         return self.__parent

#     def children(self) -> List['ParserApp']:
#         return self.__children

#     def parser(self) -> ap.ArgumentParser:
#         return self.__parser

#     #
#     # Evaluated fields of the underlying App.
#     #

#     def name(self) -> str:
#         return self.app().name

#     def brief(self) -> str:
#         return self.__help(self.app().brief)

#     def prolog(self) -> str:
#         return self.__help(self.app().prolog)

#     def epilog(self) -> str:
#         return self.__help(self.app().epilog)

#     def apps(self) -> List['App']:
#         return self.app().apps

#     def args(self) -> List['Arg']:
#         return self.app().args

#     def run(
#         self,
#         bundle: 'Bundle',
#     ) -> int:
#         if not self.app().run:
#             return 0
#         return (self.app().run)(self.app(), bundle)

#     def __help(
#         self,
#         help: str | App.FHelp,
#     ) -> str:
#         if callable(help):
#             return help(self.app())
#         else:
#             return help


# class Parser:
#     #
#     # Construct ParserApp-s.
#     #

#     def construct_apps(self) -> None:
#         if not self.parser():
#             self.__parser = self.construct_parser(None)
#         if not self.children():
#             return
#         subparsers = self.construct_subparsers()
#         for child in self.children():
#             child.__parser = child.construct_parser(subparsers)
#             child.construct_apps()

#     def construct_subparsers(self) -> Any:
#         return self.parser().add_subparsers(
#             dest=self.construct_subparsers_name(),
#             help=self.construct_subparsers_help(),
#             metavar='APP',
#             required=True,
#         )

#     def construct_parser(self, subparsers) -> ap.ArgumentParser:
#         kwargs = {
#             'prog': self.name(),
#             'description': self.prolog(),
#             'epilog': self.epilog(),
#             'formatter_class': ap.RawTextHelpFormatter,
#         }
#         if subparsers:
#             return subparsers.add_parser(kwargs)
#         return ap.ArgumentParser(kwargs)

#     def construct_subparsers_name(self) -> str:
#         papp = self
#         name = f'{self.name()}_cmd'
#         while papp.parent():
#             papp = papp.parent()
#             name = f'{papp.name()}_{name}'
#         return name

#     def construct_subparsers_help(self) -> str:
#         help = 'One of the following:'
#         for child in self.children():
#             brief = child.brief()
#             brief = f' - {brief}' if brief else ''
#             help = f'{help}\n  {child.name()}{brief}'
#         return help

#     #
#     # Construct ParserArg-s.
#     #

#     def construct_args(self) -> None:
#         pass

# def main(app: App) -> int:
#     papp = ParserApp(app)
#     ac.autocomplete(
#         papp.parser(),
#         always_complete_options=False,
#     )
#     bundle = papp.parse()
#     # counter = 0
#     # capp = papp
#     # while counter < len(bundle.apps):
#     #     code = capp.run(bundle)
#     #     if code:
#     #         return code
#     #     counter += 1
#     #     name = bundle.apps[counter].name
#     #     for child in capp.children():
#     #         if child.name() == name:
#     #             capp = child
#     #             continue
#     #     # Should not happen - argparse takes care of this.
#     #     raise ValueError(
#     #         f'argapp: Unknown App {name}. Call stack: {bundle.apps}'
#     #     )
#     return 0


def __main(app: 'App') -> int:
    return 0
