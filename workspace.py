#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import sys
from typing import *

from argapp import *

class WorkspaceApp(App):
    def __init__(
        self, 
        name: str,
        brief: str,
        prolog: str = None, 
        epilog: str = None
    ) -> None:
        super().__init__(
            name,
            brief=brief,
            prolog=prolog,
            epilog=epilog,
        )
        self.run = self.__run
        self.args = self._args()

    def _run(self, bundle: Bundle) -> int:
        raise NotImplementedError()

    def _args(self) -> list[Arg]:
        raise NotImplementedError()

    @staticmethod
    def __run(app: 'WorkspaceApp', bundle: Bundle) -> int:
        return app._run(bundle)

class WorkspaceFetch(WorkspaceApp):
    def __init__(self) -> None:
        super().__init__(
            name='fetch',
            brief='Fetch the workspace.'
        )

    def _run(self, bundle: Bundle) -> int:
        return 0

    def _args(self) -> list[Arg]:
        return []

class WorkspaceBuild(WorkspaceApp):
    def __init__(self) -> None:
        super().__init__(
            name='build',
            brief='Build the images.'
        )

    def _run(self, bundle: Bundle) -> int:
        print('build')
        return 0

    def _args(self) -> list[Arg]:
        return []

class WorkspacePackage(WorkspaceApp):
    def __init__(self) -> None:
        super().__init__(
            name='package',
            brief='Package the images.'
        )

    def _run(self, bundle: Bundle) -> int:
        return 0

    def _args(self) -> list[Arg]:
        return []

class WorkspaceDeploy(WorkspaceApp):
    def __init__(self) -> None:
        super().__init__(
            name='deploy',
            brief='Deploy the images.'
        )

    def _run(self, bundle: Bundle) -> int:
        return 0

    def _args(self) -> list[Arg]:
        return []

class WorkspaceClean(WorkspaceApp):
    def __init__(self) -> None:
        super().__init__(
            name='clean',
            brief='Clean the images.'
        )

    def _run(self, bundle: Bundle) -> int:
        return 0

    def _args(self) -> list[Arg]:
        return []

class WorkspaceRemove(WorkspaceApp):
    def __init__(self) -> None:
        super().__init__(
            name='remove',
            brief='Remove the workspace.'
        )

    def _run(self, bundle: Bundle) -> int:
        return 0

    def _args(self) -> list[Arg]:
        return []


if __name__ == '__main__':
    exit(main(App(apps=[
        WorkspaceFetch(),
        WorkspaceBuild(),
        WorkspacePackage(),
        WorkspaceDeploy(),
        WorkspaceClean(),
        WorkspaceRemove(),
    ])))
