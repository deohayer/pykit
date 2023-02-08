#!/usr/bin/env python3

from test_parserapp import *

# __init__


def test___init__():
    app = App(STR_NAME)
    papp = ParserApp(app)
    check_parserapp(papp, app, None, [])


# app


def test_app():
    app = App(STR_NAME)
    papp = ParserApp(app)
    assert papp.app() is app


# parent


def test_parent():
    app = App(STR_NAME)
    papp = ParserApp(app)
    assert papp.parent() is None


# children


def test_children():
    app = App(STR_NAME)
    papp = ParserApp(app)
    assert papp.children() == []


# parser


def test_parser():
    app = App(STR_NAME)
    papp = ParserApp(app)
    assert papp.parser() is None


# name


def test_name():
    app = App(STR_NAME)
    papp = ParserApp(app)
    assert papp.name() == STR_NAME


# brief


def test_brief():
    app = App(STR_NAME, brief=STR_BRIEF)
    papp = ParserApp(app)
    assert papp.brief() == STR_BRIEF


# prolog


def test_prolog():
    app = App(STR_NAME, prolog=STR_PROLOG)
    papp = ParserApp(app)
    assert papp.prolog() == STR_PROLOG


# epilog


def test_epilog():
    app = App(STR_NAME, epilog=STR_EPILOG)
    papp = ParserApp(app)
    assert papp.epilog() == STR_EPILOG


# apps


def test_apps():
    app = App(STR_NAME)
    papp = ParserApp(app)
    assert papp.apps() == []


# args


def test_args():
    app = App(STR_NAME)
    papp = ParserApp(app)
    assert papp.args() == []


# run


def test_run():
    app = App(STR_NAME)
    papp = ParserApp(app)
    assert papp.run(None, 0) == 0
