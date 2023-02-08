#!/usr/bin/env python3

from argapp.__argapp import ParserApp, App
import argparse as ap
import sys
from typing import *
sys.path.append('../')


STR_NAME = 'app'
STR_BRIEF = 'brief'
STR_PROLOG = 'prolog'
STR_EPILOG = 'epilog'


def check_parserapp(
    papp: ParserApp,
    app: App,
    parent: ParserApp,
    apps: List[App],
) -> None:
    assert papp.app() is app
    assert papp.parent() is parent
    assert len(apps) == len(papp.children())
    for i in range(len(apps)):
        assert papp.children()[i] is apps[i]
