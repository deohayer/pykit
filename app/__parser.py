#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import re
import sys
import argparse as ap
import argcomplete as ac
from typing import Iterable

from .app import *


RE_NAME = '^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
RE_SOPT = '^[-][a-zA-Z]$'
RE_LOPT = '^[-][-][a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
RE_COUNT = '^[?*+]$'


class ParserError(Exception):
    def __init__(
        self,
        origin: 'ParserApp | ParserArg | Parser',
        message: str,
    ) -> None:
        message = f'argapp: {ParserError.prefix(origin)}: {message}'
        super().__init__(message)
        self.message = message

    @staticmethod
    def prefix(origin: 'ParserApp | ParserArg | Parser') -> str:
        if isinstance(origin, ParserArg):
            return ParserError.__prefix_parg(origin)
        elif isinstance(origin, ParserApp):
            return ParserError.__prefix_papp(origin)
        elif isinstance(origin, Parser):
            return ParserError.__prefix_prsr(origin)
        else:
            return str(origin)

    @staticmethod
    def __prefix_parg(parg: 'ParserArg') -> str:
        str_papp = ParserError.__prefix_papp(parg.papp())
        str_parg = ParserError.__prefix_parg_name(parg)
        return f'{str_papp}.{str_parg}'

    @staticmethod
    def __prefix_papp(papp: 'ParserApp') -> str:
        names = []
        while papp:
            names.insert(0, ParserError.__prefix_papp_name(papp))
            papp = papp.parent()
        return '/'.join(names)

    @staticmethod
    def __prefix_prsr(prsr: 'Parser') -> str:
        return 'parser'

    @staticmethod
    def __prefix_papp_name(papp: 'ParserApp') -> str:
        name = papp.app().name
        if isinstance(name, str) and name:
            return name
        index = 0
        if not papp.is_root():
            index = papp.parent().papps().index(papp)
        return f'App{index}'

    @staticmethod
    def __prefix_parg_name(parg: 'ParserArg') -> str:
        name = parg.arg().name
        if isinstance(name, str) and name:
            return name
        return f'Arg{parg.papp().pargs().index(parg)}'


class ParserArg:
    def __init__(
        self,
        arg: Arg,
        papp: 'ParserApp',
    ) -> None:
        self.__arg = arg
        self.__papp = papp

    #
    # argapp interface.
    #

    def arg(self) -> Arg:
        return self.__arg

    def app(self) -> App:
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
        self.validate_valtype()
        self.validate_default()
        self.validate_choices()
        self.validate_count()
        self.validate_help()

    def validate_name(self) -> None:
        MESS_TYPE = 'Arg.name must be a non-empty str.'
        MESS_VAL = \
            'Arg.name must consist of letters (a-z, A-Z), numbers (0-9), ' \
            'dashes (-), or underscores (_). The first character must be ' \
            'a letter, the last - a letter or a number.'
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
            'following by a letter. the last character must be a letter or ' \
            'a number.'
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

    def validate_valtype(self) -> None:
        MESS_TYPE = 'Arg.valtype must be None or type.'
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
            mess = f'Choice {counter} is {type(item)} not {itemtype}.'
            if type(item) is not itemtype:
                raise ParserError(self, mess)
            counter += 1

    def validate_count(self) -> None:
        MESS_TYPE = 'Arg.count must be None, int or str.'
        MESS_IVAL = 'Arg.count as int must have a non-negative value.'
        MESS_SVAL = \
            'Arg.count as str must be "+" (1 or more), "*" (0 or more) ' \
            'or "?" (0 or 1).'
        MESS_ZERO = \
            'Arg.count must be greater than 0 for positional arguments.'
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
        if v == 0 and not self.arg().options:
            raise ParserError(self, MESS_ZERO)
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

    def eval_name(self) -> str:
        return self.arg().name.replace('_', '__').replace('-', '_')

    def eval_options(self) -> 'list[str]':
        v = self.arg().options or []
        return [x for x in v]

    def eval_metavar(self) -> str:
        v = self.arg().metavar
        if v != None:
            return v
        return self.eval_name().upper()

    def eval_valtype(self) -> type:
        v = self.arg().type
        default = self.eval_default()
        if default != None:
            v = v or type(default)
        choices = self.eval_choices()
        if choices != None:
            for item in choices:
                v = v or type(item)
                break
        return v or str

    def eval_default(self) -> object:
        return self.arg().default

    def eval_choices(self) -> list:
        v = self.arg().choices
        if not v:
            return None
        return [x for x in v]

    def eval_count(self) -> 'int | str':
        v = self.arg().count
        return v if v != None else 1

    def eval_required(self) -> bool:
        return bool(self.arg().required)

    def eval_help(self) -> str:
        return self.arg().help

    #
    # argparse interface.
    #

    def args(self) -> 'list[str]':
        return self.eval_options()

    def kwargs(self) -> 'dict[str, object]':
        kwargs = {}
        kwargs['dest'] = self.eval_name()
        kwargs['help'] = self.eval_help()
        kwargs['metavar'] = self.eval_metavar()
        if self.eval_options():
            self.__kwargs_optional(kwargs)
        else:
            self.__kwargs_positional(kwargs)
        return kwargs

    def __kwargs_optional(self, kwargs: 'dict[str, object]'):
        valtype = self.eval_valtype()
        default = self.eval_default()
        count = self.eval_count()
        kwargs['required'] = self.eval_required()
        if count != 0:
            kwargs['type'] = valtype
            kwargs['default'] = default
            kwargs['choices'] = self.eval_choices()
            kwargs['nargs'] = count
        else:
            if default != None:
                kwargs['type'] = valtype
                kwargs['action'] = 'store_const'
                kwargs['const'] = default
            elif valtype != None:
                kwargs['type'] = valtype
                kwargs['action'] = 'store_const'
                kwargs['const'] = valtype()
            else:
                kwargs['action'] = 'store_true'

    def __kwargs_positional(self, kwargs: 'dict[str, object]'):
        kwargs['type'] = self.eval_valtype()
        kwargs['default'] = self.eval_default()
        kwargs['choices'] = self.eval_choices()
        kwargs['nargs'] = self.eval_count()


class ParserApp:
    def __init__(
        self,
        app: App,
        parent: 'ParserApp' = None,
    ) -> None:
        self.__app = app
        self.__parent = parent
        self.__pargs = [ParserArg(x, self) for x in self.__app.args]
        self.__papps = [ParserApp(x, self) for x in self.__app.apps]

    #
    # argapp interface.
    #

    def app(self) -> App:
        return self.__app

    def args(self) -> 'list[Arg]':
        return self.__app.args

    def pargs(self) -> 'list[ParserArg]':
        return self.__pargs

    def apps(self) -> 'list[App]':
        return self.__app.apps

    def papps(self) -> 'list[ParserApp]':
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

    #
    # Attribute validation.
    #

    def validate(self) -> None:
        self.validate_name()
        self.validate_brief()
        self.validate_prolog()
        self.validate_epilog()
        self.validate_run()

    def validate_name(self) -> None:
        MESS_TYPE = 'App.name must be a non-empty str.'
        MESS_NONE = 'Only root App.name can be None.'
        MESS_VAL = \
            'App.name must consist of letters (a-z, A-Z), numbers (0-9), ' \
            'dashes (-), or underscores (_). The first character must be ' \
            'a letter, the last - a letter or a number.'
        v = self.app().name
        if v == None:
            if self.is_root():
                return
            else:
                raise ParserError(self, MESS_NONE)
        if not v or not isinstance(v, str):
            raise ParserError(self, MESS_TYPE)
        if not re.match(RE_NAME, v):
            raise ParserError(self, MESS_VAL)

    def validate_brief(self) -> None:
        self.__validate_help('brief')

    def validate_prolog(self) -> None:
        self.__validate_help('prolog')

    def validate_epilog(self) -> None:
        self.__validate_help('epilog')

    def validate_run(self) -> None:
        MESS_TYPE = 'App.run must be None or Callable.'
        v = self.app().run
        if v == None or callable(v):
            return
        raise ParserError(self, MESS_TYPE)

    def __validate_help(self, name: str) -> None:
        MESS_TYPE = f'App.{name} must be None or str.'
        v = getattr(self.app(), name)
        if v == None or isinstance(v, str):
            return
        raise ParserError(self, MESS_TYPE)

    #
    # argparse interface.
    #

    def args(self) -> list:
        return [self.app().name]

    def kwargs(self) -> 'dict[str, object]':
        return {
            'description': self.app().prolog,
            'epilog': self.app().epilog,
            'formatter_class': ap.RawTextHelpFormatter,
        }


class Parser:
    def __init__(self, app: App) -> None:
        self.__papp = ParserApp(app)
        self.__papp.validate()
        self.__parser = ap.ArgumentParser(
            *self.__papp.args(),
            **self.__papp.kwargs(),
        )
        Parser.__construct(self.__papp, self.__parser)

    #
    # Construction.
    #

    @staticmethod
    def __construct(
        papp: 'ParserApp',
        parser: ap.ArgumentParser,
    ) -> None:
        for parg in papp.pargs():
            parg.validate()
            parser.add_argument(*parg.args(), **parg.kwargs())
        if not papp.papps():
            return
        subparsers = parser.add_subparsers(
            dest=Parser.__subparsers_name(papp),
            help=Parser.__subparsers_help(papp),
            metavar='APP',
            required=True,
        )
        for p in papp.papps():
            p.validate()
            subparser = subparsers.add_parser(*p.args(), **p.kwargs())
            Parser.__construct(p, subparser)

    @staticmethod
    def __subparsers_name(papp: 'ParserApp') -> str:
        name = f'_argapp_'
        while papp.parent():
            papp = papp.parent()
            name = f'{papp.app().name}_{name}'
        return name.replace('-', '_')

    @staticmethod
    def __subparsers_help(papp: 'ParserApp') -> str:
        help = 'One of the following:'
        maxlen = 0
        for p in papp.papps():
            maxlen = max(len(p.app().name), maxlen)
        indent = '\n' + ' ' * (maxlen + 5)
        for p in papp.papps():
            brief = p.app().brief
            brief = f' - {brief}' if brief else ''
            brief = brief.replace('\n', indent)
            help = f'{help}\n* {p.app().name:{maxlen}}{brief}'
        return help

    #
    # Parsing.
    #

    def main(self) -> int:
        self.__argcomplete()
        bundle = self.__argparse()
        for app in bundle.apps:
            if app.run == None:
                continue
            code = (app.run)(app, bundle)
            if code != 0:
                return code
        return 0

    def __argcomplete(self) -> None:
        ac.autocomplete(
            self.__parser,
            always_complete_options=False,
        )

    def __argparse(self) -> 'Bundle':
        return Parser.__bundle(self.__papp, self.__parser.parse_args())

    @staticmethod
    def __bundle(
        papp: 'ParserApp',
        argv: ap.Namespace,
        apps: 'list[App]' = None,
        args: 'dict[Arg, object]' = None,
    ) -> Bundle:
        apps = apps or []
        args = args or {}
        apps.append(papp.app())
        for parg in papp.pargs():
            v = getattr(argv, parg.eval_name(), parg)
            if v is not parg:
                args[parg.arg()] = v
        if papp.apps():
            name = getattr(argv, Parser.__subparsers_name(papp))
            for p in papp.papps():
                if p.app().name == name:
                    Parser.__bundle(p, argv, apps, args)
        return Bundle(apps, args)
