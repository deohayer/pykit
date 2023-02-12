#!/usr/bin/env python3

from .app import App, Arg, Bundle

__all__ = [
    'AppRepoCommand',
    'AppRepoMain',
]


class AppRepoCommand(App):
    def __init__(
        self,
        name: str = None,
        help: str = None,
        prolog: str = None,
        epilog: str = None,
        args: 'list[Arg]' = None,
        apps: 'list[App]' = None,
    ) -> None:
        super().__init__(name, help, prolog, epilog, args, apps)


class AppRepoCmdWrapper(App):
    def __init__(self, app: 'AppRepoCommand', name: str, help: str) -> None:
        super().__init__(name, help)
        self.__app = app

    def name(self) -> str:
        return self.__app.name() or super().name()

    def help(self) -> str:
        return self.__app.help() or super().help()

    def prolog(self) -> str:
        return self.__app.prolog()

    def epilog(self) -> str:
        return self.__app.epilog()

    def args(self) -> 'list[Arg]':
        return self.__app.args()

    def apps(self) -> 'list[App]':
        return self.__app.apps()

    def __call__(self, bundle: Bundle) -> int:
        return self.__app.__call__(bundle)


class AppRepoMain(App):
    def __init__(
        self,
        name: str,
        fetch: 'AppRepoCommand' = None,
        build: 'AppRepoCommand' = None,
        package: 'AppRepoCommand' = None,
        deploy: 'AppRepoCommand' = None,
        clean: 'AppRepoCommand' = None,
        remove: 'AppRepoCommand' = None,
    ) -> None:
        super().__init__(name)
        self.__append(fetch, 'fetch', 'fetch the workspace.')
        self.__append(build, 'build', 'build the images.')
        self.__append(package, 'package', 'package the images.')
        self.__append(deploy, 'deploy', 'deploy the images.')
        self.__append(clean, 'clean', 'clean the images.')
        self.__append(remove, 'remove', 'remove the repository.')

    def __append(self, app: 'AppRepoCommand', name: str, help: str) -> None:
        if app != None:
            self.apps().append(AppRepoCmdWrapper(app, name, help))
