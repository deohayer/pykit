#!/usr/bin/env python3

from .. import Arg


class ArgUrl(Arg):
    def __init__(
        self,
        opt: bool = False,
        help: str = None,
    ) -> None:
        options = ['-u', '--url'] if opt else None
        help = help or 'URL.'
        super().__init__(
            'url',
            options=options,
            metavar='URL',
            help=help,
        )


class ArgRevision(Arg):
    def __init__(
        self,
        opt: bool = False,
        help: str = None,
    ) -> None:
        options = ['-r', '--rev'] if opt else None
        help = help or 'Revision.'
        super().__init__(
            'rev',
            options=options,
            metavar='REV',
            help=help,
        )


class ArgDir(Arg):
    def __init__(
        self,
        opt: bool = False,
        help: str = None,
    ) -> None:
        options = ['-d', '--dir'] if opt else None
        help = help or 'Directory path.'
        super().__init__(
            'dir',
            options=options,
            metavar='DIR',
            help=help,
        )


class ArgFile(Arg):
    def __init__(
        self,
        opt: bool = False,
        help: str = None,
    ) -> None:
        options = ['-f', '--file'] if opt else None
        help = help or 'File path.'
        super().__init__(
            'file',
            options=options,
            metavar='FILE',
            help=help,
        )


class ArgDest(Arg):
    def __init__(
        self,
        opt: bool = False,
        help: str = None,
    ) -> None:
        options = ['-d', '--dest'] if opt else None
        help = help or 'Destination path.'
        super().__init__(
            'dest',
            options=options,
            metavar='DEST',
            help=help,
        )


class ArgSrc(Arg):
    def __init__(
        self,
        opt: bool = False,
        help: str = None,
    ) -> None:
        options = ['-s', '--src'] if opt else None
        help = help or 'Source path.'
        super().__init__(
            'src',
            options=options,
            metavar='SRC',
            help=help,
        )
