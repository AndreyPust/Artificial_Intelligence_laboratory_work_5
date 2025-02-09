#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Необходимо построить дерево, где каждый узел представляет каталог
в файловой системе, а цель поиска – определенный файл. Найти путь
от корневого каталога до каталога (или файла), содержащего искомый
файл, используя алгоритм итеративного углубления.
"""

import math
import sys
from abc import ABC, abstractmethod


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def add_children(self, *args):
        for child in args:
            self.add_child(child)

    def __repr__(self):
        return f"<{self.value}>"


class Problem(ABC):
    """
    Абстрактный класс для формальной постановки задачи.
    Новый домен (конкретная задача) должен специализировать этот класс,
    переопределяя методы actions и result, а при необходимости
    action_cost, h и is_goal.
    """

    def __init__(self, initial=None, goal=None):
        """
        initial: корневой узел (TreeNode);
        goal: имя искомого файла.
        """
        self.initial = initial
        self.goal = goal

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
        Проверка, является ли состояние целевым.
        """
        return state.value == self.goal

    def action_cost(self, s, a, s1):
        """По умолчанию = 1."""
        return 1

    def h(self, node):
        """Эвристическая функция; по умолчанию 0."""
        return 0


class Node:
    """
    Узел в дереве поиска.
    """

    def __init__(self, state, parent=None, action=None, path_cost=0.0):
        self.state = state  # Текущее состояние
        self.parent = parent  # Родительский узел
        self.action = action  # Действие
        self.path_cost = path_cost

    def __repr__(self):
        return f"<Node {self.state}>"

    def __lt__(self, other):
        """Для приоритетных очередей; здесь не используется."""
        return self.path_cost < other.path_cost

    # Глубина узла — длина пути от корня (по цепочке parent)
    def __len__(self):
        if self.parent is None:
            return 0
        return 1 + len(self.parent)


# Специальные «сигнальные» узлы
failure = Node("failure", path_cost=math.inf)
cutoff = Node("cutoff", path_cost=math.inf)


def expand(problem, node):
    """
    Генерируем (расширяем) дочерние узлы, применяя actions(state).
    """

    s = node.state
    for action in problem.actions(s):
        s_next = problem.result(s, action)
        yield Node(
            state=s_next, parent=node, action=action, path_cost=node.path_cost + problem.action_cost(s, action, s_next)
        )


def path_states(node):
    """
    Восстановление последовательности состояний
    (каталогов/файлов) от корня до данного узла.
    """
    if node.parent is None:
        return [node.state.value]
    return path_states(node.parent) + [node.state.value]


class LIFOQueue(list):
    """
    Реализация стека в виде списка.
    """

    pass


def depth_limited_search(problem, limit):
    """
    Поиск с ограничением глубины.
    Пока стек не пуст, извлекаем вершину.
    Если это цель, возвращаем её.
    Если глубина >= limit, result = cutoff.
    Иначе расширяем вершину, добавляя потомков в стек.
    Если всё исчерпано и цель не найдена, возвращаем failure.
    """
    frontier = LIFOQueue([Node(problem.initial)])
    result = failure

    while frontier:
        node = frontier.pop()

        # Если это цель — возврат
        if problem.is_goal(node.state):
            return node

        # Если глубина достигла лимита, помечаем как cutoff
        if len(node) >= limit:
            result = cutoff
        else:
            # Расширяем
            for child in expand(problem, node):
                frontier.append(child)

    return result


def iterative_deepening_search(problem):
    """
    Реализация итеративного углубления.
    Многократно вызывает depth_limited_search,
    увеличивая limit от 1 до "бесконечности".
    Если результат != cutoff, то возвращает его.
    """
    for limit in range(1, sys.maxsize):
        result = depth_limited_search(problem, limit=limit)
        if result != cutoff:
            return result


class FileSearchProblem(Problem):
    """
    Описание задачи.
    Имеется дерево (TreeNode, файловая система),
    нужно найти узел, чье value == goal.
    """

    def actions(self, state):
        """
        Действия: перейти к дочернему каталогу/файлу.
        """
        return state.children

    def result(self, state, action):
        return action


def main():
    """
    Главная функция программы.
    """

    # Создание структуры файлов
    root = TreeNode("root")
    subdir_1 = TreeNode("subdir_1")
    subdir_2 = TreeNode("subdir_2")
    file_a = TreeNode("file_a")
    subdir_3 = TreeNode("subdir_3")
    file_b = TreeNode("file_b")
    file_c = TreeNode("file_c")
    file_d = TreeNode("file_d")

    root.add_children(subdir_1, subdir_2)
    subdir_1.add_children(file_a, subdir_3)
    subdir_3.add_children(file_b, file_d)
    subdir_2.add_child(file_c)

    goal = "file_d"

    problem = FileSearchProblem(initial=root, goal=goal)

    solution_node = iterative_deepening_search(problem)

    if solution_node is None or solution_node is failure:
        print("False")
    else:
        if solution_node is cutoff:
            print("False")
        else:
            # Восстанавливаем путь до целевого файла
            route = path_states(solution_node)
            print(" -> ".join(route))


if __name__ == "__main__":
    main()
