#!/usr/bin/env python3

import re
from pathlib import Path
from os import chdir
from typing import Dict, Optional, Iterator, Tuple
from subprocess import check_call, CalledProcessError
from time import sleep

from unidecode import unidecode  # pip install unidecode

DIR_ROOT = Path(__file__).parent.parent.resolve()

CATEGORIES_MAP = {
    'Teoretické základy informatiky a matematika': 'INF',
    'Programové, výpočetní a informační systémy': 'PVI'
}

TASK_MAP = Dict[str, Dict[int, str]]


def get_tasks() -> TASK_MAP:

    r: TASK_MAP = {}

    with DIR_ROOT.joinpath('README.md').open('r') as f:
        category: Optional[str] = None

        for line in f.read().split('\n'):
            if not line:
                continue
            if line.startswith('## '):
                category = CATEGORIES_MAP[line[2:].strip()]
                r[category] = {}
                continue
            question_match = re.match(r'^(\d+)\.\s+\*\*(.*)?\*\*', line)
            if question_match:
                assert category is not None
                question_number = int(question_match.group(1))
                question_name = question_match.group(2)
                if question_name.endswith('.'):
                    question_name = question_name[:-1]
                r[category][question_number] = question_name

    return r


def get_task_folder_names(task_map: TASK_MAP) -> Iterator[Tuple[str, str, int]]:
    for category, tasks in task_map.items():
        for task_num, task_name in tasks.items():
            task_name_file = unidecode(task_name)
            task_name_file = re.sub(r'\s+', '_', task_name_file)
            yield f"{category.upper()}_{task_num:02d}_{task_name_file.lower()}", task_name, task_num


def generate_task_file(task_name_file: str, task_name: str = '', task_num: Optional[int] = None) -> None:
    if task_num is None:
        task_prefix = ' '
    else:
        task_prefix = f' {task_num:02d}. '

    directory = DIR_ROOT.joinpath('otazky').joinpath(task_name_file).resolve()
    directory.mkdir(parents=True)
    with directory.joinpath('README.md').open('w') as f:
        f.write(f'# {task_prefix}{task_name}\n')


def main() -> None:
    chdir(f"{DIR_ROOT.absolute()}")

    for task_name_file, task_name, task_num in get_task_folder_names(get_tasks()):
        try:
            check_call(['git', 'checkout', '-b', task_name_file])
        except CalledProcessError:
            print('Skipping', task_name_file)
            continue
        generate_task_file(task_name_file, task_name, task_num)
        check_call(['git', 'add', 'otazky'])
        check_call(['git', 'commit', '-m', f'init {task_name_file}'])
        check_call(['git', 'push', '-u', 'origin', task_name_file])
        check_call(['git', 'checkout', 'main'])
        sleep(10)


if __name__ == '__main__':
    main()
