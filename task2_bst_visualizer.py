"""
task2_bst_visualizer.py

Інтерактивний візуалізатор двійкового дерева пошуку для варіанта №23.
Програма підтримує:
- завантаження контрольної послідовності;
- додавання нових елементів;
- пошук значення;
- покроковий перегляд;
- автоматичний режим;
- очищення дерева;
- відображення висоти, кількості вузлів та InOrder-обходу.
"""

from __future__ import annotations

import copy
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk, messagebox
from typing import Optional, List, Tuple, Dict, Any


VARIANT_23_VALUES = [10, 20, 30, 40, 50, 9, 8, 7, 6, 11, 12, 13]


@dataclass
class TreeNode:
    """Вузол двійкового дерева пошуку."""
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


@dataclass
class Step:
    """Окремий стан для покрокової візуалізації."""
    tree: Optional[TreeNode]
    message: str
    active_value: Optional[int] = None
    found_value: Optional[int] = None


class BSTVisualizer:
    """Головний клас графічного візуалізатора."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Візуалізатор двійкового дерева пошуку")
        self.root.geometry("1100x720")
        self.root.minsize(1000, 650)

        self.tree_root: Optional[TreeNode] = None
        self.steps: List[Step] = []
        self.current_step = 0
        self.auto_running = False

        self.node_radius = 22
        self.level_gap = 82

        self._create_widgets()
        self._save_step("Програма запущена. Дерево порожнє.")
        self._draw_current_step()
        self._update_info()

    def _create_widgets(self) -> None:
        """Створює елементи інтерфейсу."""
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.grid(row=0, column=0, sticky="ns")

        canvas_frame = ttk.Frame(self.root, padding=10)
        canvas_frame.grid(row=0, column=1, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        ttk.Label(left_frame, text="Панель керування", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 12))

        ttk.Label(left_frame, text="Значення:").pack(anchor="w")
        self.value_entry = ttk.Entry(left_frame, width=22)
        self.value_entry.pack(anchor="w", pady=(2, 8))

        ttk.Button(left_frame, text="Додати", command=self.add_value).pack(fill="x", pady=2)
        ttk.Button(left_frame, text="Пошук", command=self.search_value).pack(fill="x", pady=2)
        ttk.Button(left_frame, text="Завантажити варіант №23", command=self.load_variant_23).pack(fill="x", pady=(10, 2))
        ttk.Button(left_frame, text="Очистити дерево", command=self.clear_tree).pack(fill="x", pady=2)

        ttk.Separator(left_frame).pack(fill="x", pady=12)

        ttk.Label(left_frame, text="Покроковий режим", font=("Arial", 11, "bold")).pack(anchor="w")
        ttk.Button(left_frame, text="Крок назад", command=self.prev_step).pack(fill="x", pady=2)
        ttk.Button(left_frame, text="Крок вперед", command=self.next_step).pack(fill="x", pady=2)
        ttk.Button(left_frame, text="Авто-режим", command=self.start_auto).pack(fill="x", pady=(8, 2))
        ttk.Button(left_frame, text="Стоп", command=self.stop_auto).pack(fill="x", pady=2)

        ttk.Label(left_frame, text="Швидкість авто-режиму:").pack(anchor="w", pady=(12, 0))
        self.speed_var = tk.IntVar(value=650)
        self.speed_scale = ttk.Scale(left_frame, from_=1200, to=150, variable=self.speed_var, orient="horizontal")
        self.speed_scale.pack(fill="x", pady=4)

        ttk.Separator(left_frame).pack(fill="x", pady=12)

        self.info_label = ttk.Label(left_frame, text="", justify="left", wraplength=230)
        self.info_label.pack(anchor="w", pady=2)

        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, highlightbackground="#b8c0cc")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        log_frame = ttk.Frame(canvas_frame)
        log_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)

        ttk.Label(log_frame, text="Лог виконання:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w")

        self.log_text = tk.Text(log_frame, height=7, wrap="word")
        self.log_text.grid(row=1, column=0, sticky="ew")
        self.log_text.configure(state="disabled")

    def _read_int_value(self) -> Optional[int]:
        """Зчитує ціле число з поля введення."""
        raw = self.value_entry.get().strip()

        if not raw:
            messagebox.showwarning("Помилка введення", "Введіть числове значення.")
            return None

        try:
            return int(raw)
        except ValueError:
            messagebox.showwarning("Помилка введення", "Значення повинно бути цілим числом.")
            return None

    def _insert_without_steps(self, node: Optional[TreeNode], value: int) -> TreeNode:
        """Додає елемент до дерева без формування кроків."""
        if node is None:
            return TreeNode(value)

        if value < node.value:
            node.left = self._insert_without_steps(node.left, value)
        elif value > node.value:
            node.right = self._insert_without_steps(node.right, value)

        return node

    def _insert_with_steps(self, value: int) -> None:
        """Додає елемент до дерева з формуванням кроків візуалізації."""
        if self.tree_root is None:
            self.tree_root = TreeNode(value)
            self._save_step(f"Дерево порожнє. Створено корінь зі значенням {value}.", active_value=value)
            return

        current = self.tree_root

        while current is not None:
            self._save_step(f"Порівняння значення {value} з вузлом {current.value}.", active_value=current.value)

            if value == current.value:
                self._save_step(f"Значення {value} вже існує у дереві. Повторне додавання не виконується.", active_value=current.value)
                return

            if value < current.value:
                self._save_step(f"{value} < {current.value}. Перехід до лівого піддерева.", active_value=current.value)

                if current.left is None:
                    current.left = TreeNode(value)
                    self._save_step(f"Створено новий вузол {value} ліворуч від {current.value}.", active_value=value)
                    return

                current = current.left
            else:
                self._save_step(f"{value} > {current.value}. Перехід до правого піддерева.", active_value=current.value)

                if current.right is None:
                    current.right = TreeNode(value)
                    self._save_step(f"Створено новий вузол {value} праворуч від {current.value}.", active_value=value)
                    return

                current = current.right

    def add_value(self) -> None:
        """Обробляє додавання нового значення з поля введення."""
        value = self._read_int_value()
        if value is None:
            return

        self._insert_with_steps(value)
        self.current_step = len(self.steps) - 1
        self._draw_current_step()
        self._update_info()

    def load_variant_23(self) -> None:
        """Завантажує контрольну послідовність варіанта №23."""
        self.clear_tree(save_start=False)
        self._save_step("Початок завантаження послідовності варіанта №23.")

        for value in VARIANT_23_VALUES:
            self._insert_with_steps(value)

        self._save_step("Послідовність варіанта №23 повністю завантажена.")
        self.current_step = len(self.steps) - 1
        self._draw_current_step()
        self._update_info()

    def clear_tree(self, save_start: bool = True) -> None:
        """Очищує дерево та список кроків."""
        self.stop_auto()
        self.tree_root = None
        self.steps = []
        self.current_step = 0

        if save_start:
            self._save_step("Дерево очищено.")
            self._draw_current_step()
            self._update_info()

    def search_value(self) -> None:
        """Виконує пошук введеного значення у дереві."""
        value = self._read_int_value()
        if value is None:
            return

        if self.tree_root is None:
            self._save_step("Пошук неможливий: дерево порожнє.")
            self.current_step = len(self.steps) - 1
            self._draw_current_step()
            return

        current = self.tree_root

        while current is not None:
            self._save_step(f"Пошук {value}. Порівняння з вузлом {current.value}.", active_value=current.value)

            if value == current.value:
                self._save_step(f"Елемент {value} знайдено.", found_value=current.value)
                self.current_step = len(self.steps) - 1
                self._draw_current_step()
                return

            if value < current.value:
                self._save_step(f"{value} < {current.value}. Перехід ліворуч.", active_value=current.value)
                current = current.left
            else:
                self._save_step(f"{value} > {current.value}. Перехід праворуч.", active_value=current.value)
                current = current.right

        self._save_step(f"Елемент {value} не знайдено.")
        self.current_step = len(self.steps) - 1
        self._draw_current_step()

    def next_step(self) -> None:
        """Переходить до наступного стану."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._draw_current_step()

    def prev_step(self) -> None:
        """Повертається до попереднього стану."""
        if self.current_step > 0:
            self.current_step -= 1
            self._draw_current_step()

    def start_auto(self) -> None:
        """Запускає автоматичне відтворення кроків."""
        if not self.steps:
            return

        self.auto_running = True
        self._auto_tick()

    def stop_auto(self) -> None:
        """Зупиняє автоматичний режим."""
        self.auto_running = False

    def _auto_tick(self) -> None:
        """Один крок автоматичного режиму."""
        if not self.auto_running:
            return

        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._draw_current_step()
            delay = int(self.speed_var.get())
            self.root.after(delay, self._auto_tick)
        else:
            self.auto_running = False

    def _save_step(self, message: str, active_value: Optional[int] = None, found_value: Optional[int] = None) -> None:
        """Зберігає поточний стан дерева."""
        tree_copy = copy.deepcopy(self.tree_root)
        self.steps.append(Step(tree=tree_copy, message=message, active_value=active_value, found_value=found_value))
        self._append_log(message)

    def _draw_current_step(self) -> None:
        """Малює стан дерева, який відповідає поточному кроку."""
        self.canvas.delete("all")

        if not self.steps:
            self.canvas.create_text(500, 250, text="Дерево порожнє", fill="#777777", font=("Arial", 18, "bold"))
            return

        step = self.steps[self.current_step]
        self.canvas.create_text(
            20,
            20,
            anchor="w",
            text=f"Крок {self.current_step + 1}/{len(self.steps)}: {step.message}",
            fill="#222222",
            font=("Arial", 12, "bold"),
        )

        if step.tree is None:
            self.canvas.create_text(500, 260, text="Дерево порожнє", fill="#777777", font=("Arial", 18, "bold"))
            return

        canvas_width = max(self.canvas.winfo_width(), 800)
        self._draw_tree(step.tree, canvas_width // 2, 70, canvas_width // 4, step.active_value, step.found_value)

    def _draw_tree(
        self,
        node: Optional[TreeNode],
        x: int,
        y: int,
        x_gap: int,
        active_value: Optional[int],
        found_value: Optional[int],
    ) -> None:
        """Рекурсивно малює дерево на Canvas."""
        if node is None:
            return

        next_gap = max(x_gap // 2, 35)

        if node.left is not None:
            child_x = x - x_gap
            child_y = y + self.level_gap
            self.canvas.create_line(x, y, child_x, child_y, fill="#555555", width=2)
            self._draw_tree(node.left, child_x, child_y, next_gap, active_value, found_value)

        if node.right is not None:
            child_x = x + x_gap
            child_y = y + self.level_gap
            self.canvas.create_line(x, y, child_x, child_y, fill="#555555", width=2)
            self._draw_tree(node.right, child_x, child_y, next_gap, active_value, found_value)

        fill_color = "#e8f2ff"
        outline_color = "#2f6fb0"

        if active_value == node.value:
            fill_color = "#ffe99a"
            outline_color = "#c48a00"

        if found_value == node.value:
            fill_color = "#bff0c9"
            outline_color = "#2f8a44"

        r = self.node_radius
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill_color, outline=outline_color, width=3)
        self.canvas.create_text(x, y, text=str(node.value), font=("Arial", 12, "bold"))

    def _append_log(self, message: str) -> None:
        """Додає повідомлення до логу."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _inorder(self, node: Optional[TreeNode], result: List[int]) -> None:
        """Виконує симетричний обхід дерева."""
        if node is not None:
            self._inorder(node.left, result)
            result.append(node.value)
            self._inorder(node.right, result)

    def _height_edges(self, node: Optional[TreeNode]) -> int:
        """Обчислює висоту дерева у кількості ребер."""
        if node is None:
            return -1

        return 1 + max(self._height_edges(node.left), self._height_edges(node.right))

    def _count_nodes(self, node: Optional[TreeNode]) -> int:
        """Повертає кількість вузлів дерева."""
        if node is None:
            return 0

        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)

    def _update_info(self) -> None:
        """Оновлює інформаційну панель."""
        result: List[int] = []
        self._inorder(self.tree_root, result)

        height = self._height_edges(self.tree_root)
        levels = height + 1 if height >= 0 else 0
        nodes_count = self._count_nodes(self.tree_root)

        info = (
            f"Кількість вузлів: {nodes_count}\n"
            f"Висота: {height if height >= 0 else '-'} ребра\n"
            f"Рівнів: {levels}\n"
            f"InOrder:\n{result if result else '-'}"
        )
        self.info_label.configure(text=info)


def main() -> None:
    """Точка входу в програму."""
    root = tk.Tk()
    app = BSTVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
