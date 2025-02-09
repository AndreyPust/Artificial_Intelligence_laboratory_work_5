#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Поиск файла с заданным уровнем доступа. Необходимо найти все файлы,
у которых права доступа установлены как «rwxr-xr--», начиная с глубины
3 уровней. Используйте итеративное углубление и остановите поиск при
нахождении первых 10 таких файлов.
"""

import math
import os
import sys
from abc import ABC, abstractmethod


class FSNode:
    """
    Содержит путь (str) к файлу/директории.
    """

    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f"<FSNode {self.path}>"


class Problem(ABC):
    """
    Абстрактный класс для формальной постановки задачи.
    """

    def __init__(self, initial=None):
        """
        initial: начальная директория (FSNode).
        """
        self.initial = initial

    @abstractmethod
    def actions(self, state):
        """
        Вернуть доступные действия (операторы) из данного состояния.
        """
        pass

    @abstractmethod
    def result(self, state, action):
        """
        Вернуть результат применения действия к состоянию.
        """
        pass

    def is_goal(self, state):
        """
        Проверяем, является ли файл подходящим.
        """
        return False

    def action_cost(self, s, a, s1):
        """
        По умолчанию = 1.
        """
        return 1

    def h(self, node):
        """
        Эвристика, по умолчанию = 0.
        """
        return 0


class Node:
    """
    Узел в дереве поиска.
    """

    def __init__(self, state, parent=None, action=None, path_cost=0.0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def __repr__(self):
        return f"<Node {self.state}>"

    def __len__(self):
        if self.parent is None:
            return 0
        return 1 + len(self.parent)


failure = Node("failure", path_cost=math.inf)
cutoff = Node("cutoff", path_cost=math.inf)


def expand(problem, node):
    s = node.state
    for action in problem.actions(s):
        s_next = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s_next)
        yield Node(state=s_next, parent=node, action=action, path_cost=cost)


class LIFOQueue(list):
    pass


def depth_limited_search(problem, limit, found_files=None):
    """
    Поиск с ограничением глубины.
    Ищет файлы, соответствующие условию (is_goal),
    но только начиная с глубины >= 3, которые собираются в found_files.
    При достижении 10 найденных файлов — возврат.
    """

    if found_files is None:
        found_files = []

    frontier = LIFOQueue([Node(problem.initial)])
    result = failure

    while frontier:
        node = frontier.pop()

        # Если глубина >= 3 и это цель - добавляем в список
        depth = len(node)
        if depth >= 3 and problem.is_goal(node.state):
            found_files.append(node.state.path)  # строка пути
            # если достигли 10 - прерываем
            if len(found_files) >= 10:
                return node

        if depth >= limit:
            result = cutoff
        else:
            for child in expand(problem, node):
                frontier.append(child)

    return result


def iterative_deepening_search(problem, start_depth, found_files):
    """
    Реализация итеративного углубления.
    Начинаем с limit = start_depth, увеличиваем,
    пока не соберём 10 файлов или не закончатся пути.
    """

    for limit in range(start_depth, sys.maxsize):
        result = depth_limited_search(problem, limit=limit, found_files=found_files)
        # Если вернулся "failure", значит вообще нет путей
        # Если вернулся не cutoff, значит закончились пути
        if len(found_files) >= 10:
            return

        if result != cutoff:
            # Значит все пути рассмотрены и либо ничего не найдено,
            # либо нашлось меньше 10, и расширять дальше смысла нет
            return


class WindowsFileSearchProblem(Problem):
    """
    Описание задачи поиска файлов.
    Ищем файлы в файловой системе Windows,
    у которых есть права и на чтение и на запись,
    начиная с заданной директории (initial.path).
    """

    def actions(self, state):
        """
        Действия: перейти (спуститься) в каждый файл / подпапку
        внутри текущей папки (если это папка).
        Возвращает список путей (FSNode) для подпапок и файлов.
        """
        path = state.path
        if os.path.isdir(path):
            try:
                items = os.listdir(path)
            except (PermissionError, FileNotFoundError):
                return []  # нет доступа/нет файла
            result = []
            for item in items:
                full = os.path.join(path, item)
                result.append(FSNode(full))
            return result
        else:
            return []  # если это файл, не расширяем

    def result(self, state, action):
        return action

    def is_goal(self, state):
        """
        Цель: проверить права, на чтение и запись.
        """
        path = state.path
        if os.path.isfile(path):
            try:
                mode = os.stat(path).st_mode
                # Проверяем, равны ли биты mode == 33206, то есть проверка на чтение и запись
                return mode == 33206
            except PermissionError:
                return False
        return False


def main():
    """
    Главная функция программы.
    """

    # Начальная папка
    root_path = r"C:\Users\Andrey\Desktop"

    # По условию задачи необходимо начинать с глубины 3
    start_depth = 3

    problem = WindowsFileSearchProblem(initial=FSNode(root_path))

    # Список для найденных файлов
    found_files = []

    iterative_deepening_search(problem, start_depth, found_files)

    # Выводим результаты
    if not found_files:
        print("Ничего не найдено.")
    else:
        print("Найденные файлы (не более 10):")
        for f in found_files:
            print(f)


if __name__ == "__main__":
    main()
