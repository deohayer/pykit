#!/usr/bin/env python3

import sys

from .. import App, Bundle


class WorkspaceCommand(App):
    def __init__(
        self,
        name: str,
        brief: str,
    ) -> None:
        super().__init__(
            name,
            brief=brief,
        )
        self.run = self.__run

    def _run(self, bundle: Bundle) -> int:
        raise NotImplementedError()

    @staticmethod
    def __run(
        app: 'WorkspaceCommand',
        bundle: Bundle,
    ) -> int:
        return app._run(bundle)


class WorkspaceFetch(WorkspaceCommand):
    def __init__(self) -> None:
        super().__init__(
            name='fetch',
            brief='Fetch the workspace.',
        )

    def _run(self, bundle: Bundle) -> int:
        return 0


class WorkspaceBuild(WorkspaceCommand):
    def __init__(self) -> None:
        super().__init__(
            name='build',
            brief='Build the images.',
        )

    def _run(self, bundle: Bundle) -> int:
        print('build')
        return 0


class WorkspacePackage(WorkspaceCommand):
    def __init__(self) -> None:
        super().__init__(
            name='package',
            brief='Package the images.',
        )

    def _run(self, bundle: Bundle) -> int:
        return 0


class WorkspaceDeploy(WorkspaceCommand):
    def __init__(self) -> None:
        super().__init__(
            name='deploy',
            brief='Deploy the images.',
        )

    def _run(self, bundle: Bundle) -> int:
        return 0


class WorkspaceClean(WorkspaceCommand):
    def __init__(self) -> None:
        super().__init__(
            name='clean',
            brief='Clean the images.',
        )

    def _run(self, bundle: Bundle) -> int:
        return 0


class WorkspaceRemove(WorkspaceCommand):
    def __init__(self) -> None:
        super().__init__(
            name='remove',
            brief='Remove the workspace.',
        )

    def _run(self, bundle: Bundle) -> int:
        return 0


class WorkspaceApp(App):
    def __init__(
        self,
        name: str = None,
        fetch: WorkspaceFetch = None,
        build: WorkspaceBuild = None,
        package: WorkspacePackage = None,
        deploy: WorkspaceDeploy = None,
        clean: WorkspaceClean = None,
        remove: WorkspaceRemove = None,
    ):
        name = name or sys.argv[0]
        super().__init__(name)
        self.__append_cmd(fetch)
        self.__append_cmd(build)
        self.__append_cmd(package)
        self.__append_cmd(deploy)
        self.__append_cmd(clean)
        self.__append_cmd(remove)

    def __append_cmd(self, cmd: WorkspaceCommand) -> None:
        if cmd:
            self.apps.append(cmd)
