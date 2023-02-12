#!/usr/bin/env python3

import os
import subprocess

__all__ = [
    'ShellError',
    'Shell',
]


class ShellError(Exception):
    def __init__(self, shell: 'Shell') -> None:
        mess = f'Shell command failed with exit code {shell.ret()}'
        super().__init__(mess)
        self.__mess = mess
        self.__shell = shell

    def message(self) -> str:
        return self.__mess

    def shell(self) -> 'Shell':
        return self.__shell


class Shell:
    ENC_UTF8: str = 'utf-8'

    def __init__(self) -> None:
        self.__env: 'dict[str, str]' = {}
        self.__out: str = ''
        self.__err: str = ''
        self.__ret: int = 0
        self.__enc: str = Shell.ENC_UTF8
        self.__exc: bool = False

    def run(
        self,
        command: str,
        capture: bool = False,
    ) -> int:
        envset = ''
        if self.__env:
            env = [x for x in self.__env.items() if x[1] != None]
            envset = '; '.join(f'export {x[0]}={x[1]}' for x in env)
            envset += '; '
        result = subprocess.run(
            f'{envset}{command}',
            shell=True,
            capture_output=capture,
            encoding=self.__enc,
        )
        if capture:
            self.__out = result.stdout
            self.__err = result.stderr
        self.__ret = result.returncode
        if self.__exc and self.ret() != 0:
            raise ShellError(self)
        return self.ret()

    def set(self, var: str, val: str = None) -> None:
        self.__env[var] = val

    def get(self, var: str, val: str = None) -> str:
        return self.__env.get(var, os.getenv(var, val))

    def has(self, var: str) -> bool:
        return self.get(var) != None

    def enc(self, fmt: str = None) -> str:
        self.__enc = fmt or self.__enc
        return self.__enc

    def out(self, notrail: bool = True) -> str:
        return self.__out.removesuffix('\n') if notrail else self.__out

    def err(self, notrail: bool = True) -> str:
        return self.__err.removesuffix('\n') if notrail else self.__err

    def ret(self) -> int:
        return self.__ret

    def exc(self, val: bool) -> None:
        self.__exc = val

    def cls(self) -> None:
        self.__env.clear()
        self.__out = ''
        self.__err = ''
        self.__ret = 0
