#!/usr/bin/env python3

#!/usr/bin/env python3

import re
import argparse
import argcomplete
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
        metavar: str = None,
        type: type = None,
        default: object = None,
        choices: Iterable = None,
        count: int | str = None,
        required: bool = None,
        help: str = None,
    ) -> None:
        self.name = name
        self.options = options
        self.metavar = metavar
        self.type = type
        self.default = default
        self.choices = choices
        self.count = count
        self.required = required
        self.help = help


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

###############################################################################
#                                                                             #
#                               Implementation                                #
#                                                                             #
###############################################################################


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
        index = 0
        if not papp.is_root():
            index = papp.parent().papps().index(papp)
        return f'App{index}'

    @staticmethod
    def prefix_parg_name(parg: 'ParserArg') -> str:
        name = parg.arg().name
        if isinstance(name, str) and name:
            return name
        return f'Arg{parg.papp().pargs().index(parg)}'


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

    #
    # Attribute validation.
    #

    def validate(self) -> None:
        self.validate_name()
        self.validate_options()
        self.validate_metavar()
        self.validate_type()
        self.validate_default()
        self.validate_choices()
        self.validate_count()
        self.validate_help()

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
            mess = f'Invalid option {counter}. '
            if len(item) < 2:
                raise ParserError(self, mess + MESS_VAL)
            elif len(item) == 2 and not re.match(RE_SOPT, item):
                raise ParserError(self, mess + MESS_SVAL)
            elif len(item) > 2 and not re.match(RE_LOPT, item):
                raise ParserError(self, mess + MESS_LVAL)
            counter += 1

    def validate_metavar(self) -> None:
        MESS_TYPE = 'Arg.option must be None or str.'
        MESS_VAL = \
            'Arg.metavar must consist of letters (a-z, A-Z), numbers (0-9), ' \
            'dashes (-), or underscores (_).'
        v = self.arg().metavar
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
        v = self.arg().default
        if v == None:
            return
        # Get type.
        itemtype = self.arg().type
        # If type is None, get it from the first choice.
        choices = self.arg().choices or []
        for item in choices:
            itemtype = itemtype or type(item)
            break
        # If type is None, fallback to object.
        itemtype = itemtype or object
        mess = f'Arg.default must be None or {itemtype.__name__}.'
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
        if default != None:
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

    def validate_required(self) -> None:
        MESS_TYPE = 'Arg.required must be None or bool.'
        v = self.arg().count
        if v == None:
            return
        if not isinstance(v, bool):
            raise ParserError(self, MESS_TYPE)

    def validate_help(self) -> None:
        MESS_TYPE = 'Arg.help must be None or str.'
        v = self.arg().help
        if v == None or isinstance(v, str):
            return
        raise ParserError(self, MESS_TYPE)

    #
    # Attribute evaluation.
    #

    def evaluate_name(self) -> str:
        return self.arg().name

    def evaluate_options(self) -> list[str]:
        v = self.arg().options or []
        return [x for x in v]

    def evaluate_metavar(self) -> str:
        v = self.arg().metavar
        if v != None:
            return v
        return self.evaluate_name().upper()

    def evaluate_type(self) -> type:
        v = self.arg().type
        default = self.evaluate_default()
        if default != None:
            v = v or type(default)
        choices = self.evaluate_choices()
        for item in choices:
            v = v or type(item)
            break
        return v or str

    def evaluate_default(self) -> object:
        return self.arg().default

    def evaluate_choices(self) -> list:
        v = self.arg().choices
        if not v:
            return None
        return [x for x in v]

    def evaluate_count(self) -> int | str:
        return self.arg().count or 1

    def evaluate_required(self) -> bool:
        return bool(self.arg().required or not self.evaluate_options())

    def evaluate_help(self) -> str:
        return self.arg().help

    #
    # Translation to argparse.
    #

    def argparse_args(self) -> list:
        return self.evaluate_options()

    def argparse_kwargs(self) -> dict[str, object]:
        return {
            'action': self.argparse_action(),
            'nargs': self.argparse_nargs(),
            'const': self.argparse_const(),
            'default': self.argparse_default(),
            'type': self.argparse_type(),
            'choices': self.argparse_choices(),
            'required': self.argparse_required(),
            'help': self.argparse_help(),
            'metavar': self.argparse_metavar(),
            'dest': self.argparse_dest(),
            'version': self.argparse_version(),
        }

    def argparse_action(self) -> str:
        return None

    def argparse_nargs(self) -> str | int:
        return self.evaluate_count()

    def argparse_const(self) -> object:
        return None

    def argparse_default(self) -> object:
        return self.evaluate_default()

    def argparse_type(self) -> type:
        return self.evaluate_type()

    def argparse_choices(self) -> list:
        return self.evaluate_choices()

    def argparse_required(self) -> bool:
        return self.evaluate_required()

    def argparse_help(self) -> str:
        return self.evaluate_help()

    def argparse_metavar(self) -> str:
        return self.evaluate_metavar()

    def argparse_dest(self) -> str:
        return self.evaluate_name().replace('-', '_')

    def argparse_version(self) -> str:
        return None


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
