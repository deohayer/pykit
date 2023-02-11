#!/usr/bin/env python3

from .. import Arg


class ArgUrl(Arg):
    def __init__(self, help: str = None) -> None:
       super().__init__(
           'url',
           options=['-u', '--url'],
           metavar='URL',
           help=help,
       )


class ArgRevision(Arg):
    def __init__(self, help: str = None) -> None:
       super().__init__(
           'revision',
           options=['-r', '--revision'],
           metavar='REV',
           help=help,
       )


class ArgDir(Arg):
    def __init__(self, help: str = None) -> None:
       super().__init__(
           'dir',
           options=['-d', '--dir'],
           metavar='PATH',
           help=help,
       )


class ArgFile(Arg):
    def __init__(self, help: str = None) -> None:
       super().__init__(
           'file',
           options=['-f', '--file'],
           metavar='PATH',
           help=help,
       )
