#!/usr/bin/env python3

from .__parser import *

__all__ = [
    'main',
]


def main(app: App) -> int:
    try:
        return Parser(app).main()
    except ParserError as e:
        raise ArgappError(e.message) from e
