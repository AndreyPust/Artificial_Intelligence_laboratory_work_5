#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Представьте себе систему управления доступом, где каждый пользователь
представлен узлом в дереве. Каждый узел содержит уникальный идентификатор
пользователя. Необходимо разработать метод поиска, который позволит
проверить существование пользователя с заданным идентификатором в системе,
используя структуру дерева и алгоритм итеративного углубления.
"""

import math
import sys
from abc import ABC, abstractmethod


class BinaryTreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def add_children(self, left, right):
        self.left = left
        self.right = right

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
        initial: корневой узел (BinaryTreeNode)
        goal: искомое значение
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
        """
        По умолчанию 1.
        """
        return 1

    def h(self, node):
        """
        Эвристическая функция, по умолчанию 0.
        """
        return 0


class Node:
    """
    Узел в дереве поиска.
    """

    def __init__(self, state, parent=None, action=None, path_cost=0.0):
        self.state = state  # Текущее состояние
        self.parent = parent  # Родительский узел
        self.action = action  # Действие, которое привело сюда
        self.path_cost = path_cost

    def __repr__(self):
        return f"<Node {self.state}>"

    def __lt__(self, other):
        return self.path_cost < other.path_cost

    def __len__(self):
        if self.parent is None:
            return 0
        else:
            return 1 + len(self.parent)


failure = Node("failure", path_cost=math.inf)
cutoff = Node("cutoff", path_cost=math.inf)


def expand(problem, node):
    """
    Генерируем дочерние узлы, применяя actions(state).
    """
    s = node.state
    for action in problem.actions(s):
        s_next = problem.result(s, action)
        yield Node(
            state=s_next, parent=node, action=action, path_cost=node.path_cost + problem.action_cost(s, action, s_next)
        )


class LIFOQueue(list):
    """
    Реализация стека в виде списка.
    """

    pass


def depth_limited_search(problem, limit=10):
    """
    Поиск с ограничением глубины/
    Пока стек не пуст, извлекаем вершину.
    Если это цель, возвращаем её.
    Если глубина >= limit, запоминаем result = cutoff.
    Если все исчерпано, return failure.
    """
    frontier = LIFOQueue([Node(problem.initial)])
    result = failure

    while frontier:
        node = frontier.pop()

        if problem.is_goal(node.state):
            return node

        if len(node) >= limit:
            result = cutoff

        for child in expand(problem, node):
            frontier.append(child)

    return result


def iterative_deepening_search(problem):
    """
    Функция осуществления итеративного углубления.
    """
    for limit in range(1, sys.maxsize):
        result = depth_limited_search(problem, limit=limit)
        if result != cutoff:
            return result


class UserSearchProblem(Problem):
    """
    Описание конкретной задачи.
    Дано бинарное дерево (BinaryTreeNode) с пользователями.
    Нужно проверить, существует ли узел с value == goal.
    """

    def actions(self, state):
        """
        Действия: перейти в left или в right, если они существуют
        """
        moves = []
        if state.left:
            moves.append(state.left)
        if state.right:
            moves.append(state.right)
        return moves

    def result(self, state, action):
        return action


def main():
    """
    Главная функция программы.
    """

    root = BinaryTreeNode(1)
    left_child = BinaryTreeNode(2)
    right_child = BinaryTreeNode(3)

    # Подвешиваем их к корню
    root.add_children(left_child, right_child)

    # Расширяем поддерево слева
    left_left = BinaryTreeNode(6, left=BinaryTreeNode(8))
    left_right = BinaryTreeNode(7)
    left_child.add_children(left_left, left_right)

    # Расширяем поддерево справа
    right_left = BinaryTreeNode(9, right=BinaryTreeNode(4))
    right_right = BinaryTreeNode(5)
    right_child.add_children(right_left, right_right)

    # Целевое значение (идентификатор пользователя)
    goal = 4

    problem = UserSearchProblem(initial=root, goal=goal)

    solution_node = iterative_deepening_search(problem)

    if solution_node is None or solution_node is failure:
        print(False)
    else:
        # Если это не cutoff, либо реальный узел с решением
        if solution_node is cutoff:
            print(False)
        else:
            print(True)


if __name__ == "__main__":
    main()
