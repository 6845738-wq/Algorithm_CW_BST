"""
task1_bst_analysis.py

Побудова та аналіз двійкового дерева пошуку для варіанта №23.
Послідовність: 10, 20, 30, 40, 50, 9, 8, 7, 6, 11, 12, 13.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, List


VARIANT_23_VALUES = [10, 20, 30, 40, 50, 9, 8, 7, 6, 11, 12, 13]


@dataclass
class TreeNode:
    """Вузол двійкового дерева пошуку."""
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


def insert(root: Optional[TreeNode], value: int) -> TreeNode:
    """
    Додає нове значення до двійкового дерева пошуку.

    Якщо дерево порожнє, створюється новий корінь.
    Якщо value < root.value, елемент додається до лівого піддерева.
    Якщо value > root.value, елемент додається до правого піддерева.
    Повторні значення у цій реалізації ігноруються.
    """
    if root is None:
        return TreeNode(value)

    if value < root.value:
        root.left = insert(root.left, value)
    elif value > root.value:
        root.right = insert(root.right, value)

    return root


def inorder(node: Optional[TreeNode], result: List[int]) -> None:
    """Виконує симетричний обхід дерева."""
    if node is not None:
        inorder(node.left, result)
        result.append(node.value)
        inorder(node.right, result)


def height_edges(node: Optional[TreeNode]) -> int:
    """
    Обчислює висоту дерева у кількості ребер.

    Порожнє дерево має висоту -1.
    Дерево з одним вузлом має висоту 0.
    """
    if node is None:
        return -1

    left_h = height_edges(node.left)
    right_h = height_edges(node.right)

    return 1 + max(left_h, right_h)


def count_nodes(node: Optional[TreeNode]) -> int:
    """Повертає кількість вузлів дерева."""
    if node is None:
        return 0

    return 1 + count_nodes(node.left) + count_nodes(node.right)


def longest_paths(node: Optional[TreeNode]) -> List[List[int]]:
    """Повертає всі найдовші шляхи від кореня до листків."""
    if node is None:
        return []

    if node.left is None and node.right is None:
        return [[node.value]]

    paths = []
    for child in (node.left, node.right):
        for path in longest_paths(child):
            paths.append([node.value] + path)

    if not paths:
        return [[node.value]]

    max_len = max(len(path) for path in paths)
    return [path for path in paths if len(path) == max_len]


def build_tree(values: List[int]) -> Optional[TreeNode]:
    """Будує двійкове дерево пошуку з переданої послідовності."""
    root = None
    for value in values:
        root = insert(root, value)
    return root


def main() -> None:
    """Головна функція програми."""
    print("Побудова двійкового дерева пошуку")
    print("Варіант №23")
    print("Вхідна послідовність:", VARIANT_23_VALUES)

    start_time = time.perf_counter()
    root = build_tree(VARIANT_23_VALUES)
    end_time = time.perf_counter()

    traversal: List[int] = []
    inorder(root, traversal)

    height = height_edges(root)
    levels = height + 1
    nodes_count = count_nodes(root)
    execution_time_ms = (end_time - start_time) * 1000

    print("\nРезультати аналізу:")
    print("Симетричний обхід:", traversal)
    print("Кількість вузлів:", nodes_count)
    print("Висота дерева:", height, "ребра")
    print("Кількість рівнів:", levels)
    print("Час побудови:", f"{execution_time_ms:.6f}", "мс")

    print("\nНайдовші шляхи:")
    for path in longest_paths(root):
        print(" -> ".join(map(str, path)))


if __name__ == "__main__":
    main()
