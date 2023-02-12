#!/usr/bin/env python3

__all__ = [
    'help_list',
    'help_twins',
    'help_grid',
]

def help_list(help: str, lst: list, prefix: str = ' * ') -> str:
    return (f'{help}\n{prefix}' + prefix.join(lst)).removeprefix('\n')

def help_twins(
    help: str, 
    lst1: list, 
    lst2: list, 
    prefix: str = ' * ', 
    infix = ' - '
) -> str:
    size = max(len(lst1), len(lst2))
    align = max([len(x) for x in lst1])
    for i in range(size):
        help += f'\n{prefix}{lst1[i]:{align}}{infix}{lst2[i]}'
    return help.removeprefix('\n')

def help_grid(help: str, lst: list, cols: int, infix = ' ') -> str:
    align = max([len(x) for x in lst])
    size = len(lst)
    rows = int(size / cols)
    for i in range(rows):
        help += '\n'
        for j in range(cols):
            help += f'{lst[i * cols + j]:{align}}{infix}'
        help = help.removesuffix(f'{infix}')
    help += '\n'
    for i in range(size % cols):
        help += f'{lst[int(size / cols) * cols + i]:{align}}{infix}'
    help = help.removesuffix(f'{infix}')
    return help.removeprefix('\n')
