"""
task2_kmp_visualizer.py

Інтерактивний візуалізатор алгоритму Кнута — Морріса — Пратта.
Програма підтримує:
- введення тексту і шаблону;
- побудову префікс-функції;
- пошук шаблону в тексті;
- покроковий режим;
- автоматичне відтворення;
- регулювання швидкості;
- очищення результатів.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk, messagebox
from typing import List, Optional


DEFAULT_TEXT = "ABABDABACDABABCABAB"
DEFAULT_PATTERN = "ABABCABAB"


@dataclass
class Step:
    """Окремий крок візуалізації."""
    message: str
    text_index: Optional[int] = None
    pattern_index: Optional[int] = None
    prefix_index: Optional[int] = None
    prefix_values: Optional[List[int]] = None
    found_start: Optional[int] = None
    found_end: Optional[int] = None
    mismatch: bool = False


def build_prefix(pattern: str) -> List[int]:
    """Будує масив префікс-функції для шаблону."""
    prefix = [0] * len(pattern)
    j = 0

    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = prefix[j - 1]

        if pattern[i] == pattern[j]:
            j += 1

        prefix[i] = j

    return prefix


def kmp_search(text: str, pattern: str) -> int:
    """Повертає позицію першого входження шаблону в текст або -1."""
    if not pattern:
        return 0

    prefix = build_prefix(pattern)
    j = 0

    for i, char in enumerate(text):
        while j > 0 and char != pattern[j]:
            j = prefix[j - 1]

        if char == pattern[j]:
            j += 1

        if j == len(pattern):
            return i - j + 1

    return -1


class KMPVisualizer:
    """Головний клас графічного візуалізатора КМП."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Візуалізатор алгоритму Кнута — Морріса — Пратта")
        self.root.geometry("1120x720")
        self.root.minsize(1000, 640)

        self.text_value = tk.StringVar(value=DEFAULT_TEXT)
        self.pattern_value = tk.StringVar(value=DEFAULT_PATTERN)

        self.prefix: List[int] = []
        self.steps: List[Step] = []
        self.current_step = 0
        self.auto_running = False

        self.cell_width = 34
        self.cell_height = 36

        self._create_widgets()
        self._log("Програма запущена.")
        self._draw_empty_state()

    def _create_widgets(self) -> None:
        """Створює елементи графічного інтерфейсу."""
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        control = ttk.Frame(self.root, padding=10)
        control.grid(row=0, column=0, sticky="ns")

        workspace = ttk.Frame(self.root, padding=10)
        workspace.grid(row=0, column=1, sticky="nsew")
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(0, weight=1)

        ttk.Label(control, text="Панель керування", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 12))

        ttk.Label(control, text="Текст:").pack(anchor="w")
        ttk.Entry(control, textvariable=self.text_value, width=34).pack(anchor="w", pady=(2, 8))

        ttk.Label(control, text="Шаблон:").pack(anchor="w")
        ttk.Entry(control, textvariable=self.pattern_value, width=34).pack(anchor="w", pady=(2, 12))

        ttk.Button(control, text="Побудувати префікс-функцію", command=self.build_prefix_steps).pack(fill="x", pady=2)
        ttk.Button(control, text="Почати пошук", command=self.start_search).pack(fill="x", pady=2)
        ttk.Button(control, text="Очистити", command=self.clear).pack(fill="x", pady=2)

        ttk.Separator(control).pack(fill="x", pady=12)

        ttk.Label(control, text="Покроковий режим", font=("Arial", 11, "bold")).pack(anchor="w")
        ttk.Button(control, text="Крок назад", command=self.prev_step).pack(fill="x", pady=2)
        ttk.Button(control, text="Крок вперед", command=self.next_step).pack(fill="x", pady=2)
        ttk.Button(control, text="Авто-режим", command=self.start_auto).pack(fill="x", pady=(8, 2))
        ttk.Button(control, text="Стоп", command=self.stop_auto).pack(fill="x", pady=2)

        ttk.Label(control, text="Швидкість авто-режиму:").pack(anchor="w", pady=(12, 0))
        self.speed_var = tk.IntVar(value=650)
        ttk.Scale(control, from_=1200, to=150, variable=self.speed_var, orient="horizontal").pack(fill="x", pady=4)

        ttk.Separator(control).pack(fill="x", pady=12)

        self.result_label = ttk.Label(control, text="Результат: -", justify="left", wraplength=250)
        self.result_label.pack(anchor="w", pady=4)

        self.canvas = tk.Canvas(workspace, bg="white", highlightthickness=1, highlightbackground="#b8c0cc")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        log_frame = ttk.Frame(workspace)
        log_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)

        ttk.Label(log_frame, text="Лог виконання:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.log_text = tk.Text(log_frame, height=7, wrap="word")
        self.log_text.grid(row=1, column=0, sticky="ew")
        self.log_text.configure(state="disabled")

    def _validate_input(self) -> Optional[tuple[str, str]]:
        """Перевіряє введені користувачем дані."""
        text = self.text_value.get().strip()
        pattern = self.pattern_value.get().strip()

        if not text:
            messagebox.showwarning("Помилка", "Введіть текст.")
            return None

        if not pattern:
            messagebox.showwarning("Помилка", "Введіть шаблон.")
            return None

        if len(pattern) > len(text):
            messagebox.showwarning("Помилка", "Шаблон не може бути довшим за текст.")
            return None

        return text, pattern

    def build_prefix_steps(self) -> None:
        """Будує префікс-функцію та формує кроки для її демонстрації."""
        data = self._validate_input()
        if data is None:
            return

        _, pattern = data
        prefix = [0] * len(pattern)
        j = 0

        self.prefix = prefix[:]
        self.steps = [Step("Початок побудови префікс-функції.", prefix_values=prefix[:])]
        self.current_step = 0

        for i in range(1, len(pattern)):
            self.steps.append(
                Step(
                    f"Порівнюємо pattern[{i}] = '{pattern[i]}' та pattern[{j}] = '{pattern[j]}'.",
                    pattern_index=j,
                    prefix_index=i,
                    prefix_values=prefix[:],
                )
            )

            while j > 0 and pattern[i] != pattern[j]:
                old_j = j
                j = prefix[j - 1]
                self.steps.append(
                    Step(
                        f"Розбіжність. Змінюємо j з {old_j} на prefix[{old_j - 1}] = {j}.",
                        pattern_index=j,
                        prefix_index=i,
                        prefix_values=prefix[:],
                        mismatch=True,
                    )
                )

            if pattern[i] == pattern[j]:
                j += 1
                self.steps.append(
                    Step(
                        f"Символи збіглися. Збільшуємо j до {j}.",
                        pattern_index=j - 1,
                        prefix_index=i,
                        prefix_values=prefix[:],
                    )
                )

            prefix[i] = j
            self.steps.append(
                Step(
                    f"Записуємо prefix[{i}] = {j}.",
                    pattern_index=j - 1 if j > 0 else 0,
                    prefix_index=i,
                    prefix_values=prefix[:],
                )
            )

        self.prefix = prefix[:]
        self.steps.append(Step("Побудову префікс-функції завершено.", prefix_values=prefix[:]))
        self.current_step = len(self.steps) - 1
        self._draw_current_step()
        self._log("Побудовано префікс-функцію: " + str(prefix))
        self.result_label.configure(text="Префікс-функція:\n" + str(prefix))

    def start_search(self) -> None:
        """Формує кроки пошуку шаблону в тексті методом КМП."""
        data = self._validate_input()
        if data is None:
            return

        text, pattern = data
        prefix = build_prefix(pattern)
        self.prefix = prefix

        self.steps = [Step("Початок пошуку шаблону в тексті.", prefix_values=prefix)]
        self.current_step = 0

        j = 0
        found = -1

        for i, char in enumerate(text):
            self.steps.append(
                Step(
                    f"Порівнюємо text[{i}] = '{char}' та pattern[{j}] = '{pattern[j]}'.",
                    text_index=i,
                    pattern_index=j,
                    prefix_values=prefix,
                )
            )

            while j > 0 and char != pattern[j]:
                old_j = j
                j = prefix[j - 1]
                self.steps.append(
                    Step(
                        f"Розбіжність. Змінюємо j з {old_j} на prefix[{old_j - 1}] = {j}.",
                        text_index=i,
                        pattern_index=j,
                        prefix_values=prefix,
                        mismatch=True,
                    )
                )

            if char == pattern[j]:
                j += 1
                self.steps.append(
                    Step(
                        f"Символи збіглися. Збільшуємо j до {j}.",
                        text_index=i,
                        pattern_index=j - 1,
                        prefix_values=prefix,
                    )
                )

            if j == len(pattern):
                found = i - j + 1
                self.steps.append(
                    Step(
                        f"Шаблон знайдено з позиції {found}.",
                        text_index=i,
                        pattern_index=j - 1,
                        prefix_values=prefix,
                        found_start=found,
                        found_end=i,
                    )
                )
                break

        if found == -1:
            self.steps.append(Step("Шаблон не знайдено в тексті.", prefix_values=prefix))
            self.result_label.configure(text="Результат:\nшаблон не знайдено")
            self._log("Шаблон не знайдено.")
        else:
            self.result_label.configure(text=f"Результат:\nшаблон знайдено з позиції {found}")
            self._log(f"Шаблон знайдено з позиції {found}.")

        self.current_step = 0
        self._draw_current_step()

    def next_step(self) -> None:
        """Переходить до наступного кроку."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._draw_current_step()

    def prev_step(self) -> None:
        """Повертається до попереднього кроку."""
        if self.current_step > 0:
            self.current_step -= 1
            self._draw_current_step()

    def start_auto(self) -> None:
        """Запускає автоматичне відтворення."""
        if not self.steps:
            return
        self.auto_running = True
        self._auto_tick()

    def stop_auto(self) -> None:
        """Зупиняє автоматичне відтворення."""
        self.auto_running = False

    def _auto_tick(self) -> None:
        """Один крок автоматичного режиму."""
        if not self.auto_running:
            return

        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self._draw_current_step()
            self.root.after(int(self.speed_var.get()), self._auto_tick)
        else:
            self.auto_running = False

    def clear(self) -> None:
        """Очищує результати виконання."""
        self.stop_auto()
        self.steps = []
        self.current_step = 0
        self.prefix = []
        self.result_label.configure(text="Результат: -")
        self._draw_empty_state()
        self._log("Результати очищено.")

    def _draw_empty_state(self) -> None:
        """Відображає початковий стан."""
        self.canvas.delete("all")
        self.canvas.create_text(
            30,
            30,
            anchor="w",
            text="Введіть текст і шаблон, після чого запустіть побудову префікс-функції або пошук.",
            font=("Arial", 13, "bold"),
            fill="#333333",
        )
        self._draw_text_and_pattern(None, None, None, None, False)
        self._draw_prefix_table([0] * len(self.pattern_value.get().strip()), None)

    def _draw_current_step(self) -> None:
        """Малює поточний крок алгоритму."""
        self.canvas.delete("all")

        if not self.steps:
            self._draw_empty_state()
            return

        step = self.steps[self.current_step]
        self.canvas.create_text(
            30,
            25,
            anchor="w",
            text=f"Крок {self.current_step + 1}/{len(self.steps)}: {step.message}",
            font=("Arial", 12, "bold"),
            fill="#222222",
        )

        self._draw_text_and_pattern(
            step.text_index,
            step.pattern_index,
            step.found_start,
            step.found_end,
            step.mismatch,
        )
        self._draw_prefix_table(step.prefix_values or self.prefix, step.prefix_index)

    def _draw_text_and_pattern(
        self,
        text_index: Optional[int],
        pattern_index: Optional[int],
        found_start: Optional[int],
        found_end: Optional[int],
        mismatch: bool,
    ) -> None:
        """Малює рядки тексту і шаблону."""
        text = self.text_value.get().strip()
        pattern = self.pattern_value.get().strip()

        self.canvas.create_text(35, 90, anchor="w", text="Текст", font=("Arial", 12, "bold"))
        self._draw_symbol_row(text, 35, 115, text_index, found_start, found_end, mismatch)

        self.canvas.create_text(35, 190, anchor="w", text="Шаблон", font=("Arial", 12, "bold"))
        self._draw_symbol_row(pattern, 35, 215, pattern_index, None, None, mismatch)

    def _draw_symbol_row(
        self,
        value: str,
        x: int,
        y: int,
        active_index: Optional[int],
        found_start: Optional[int],
        found_end: Optional[int],
        mismatch: bool,
    ) -> None:
        """Малює один рядок символів."""
        for index, char in enumerate(value):
            bx = x + index * self.cell_width
            fill = "white"
            outline = "#9aa4b2"

            if found_start is not None and found_end is not None and found_start <= index <= found_end:
                fill = "#bff0c9"
                outline = "#2f8a44"

            if active_index == index:
                fill = "#ffd6d6" if mismatch else "#ffe99a"
                outline = "#b84141" if mismatch else "#c48a00"

            self.canvas.create_rectangle(bx, y, bx + 28, y + 30, fill=fill, outline=outline, width=2)
            self.canvas.create_text(bx + 14, y + 15, text=char, font=("Arial", 11, "bold"))
            self.canvas.create_text(bx + 14, y + 45, text=str(index), font=("Arial", 8), fill="#777777")

    def _draw_prefix_table(self, prefix: List[int], active_index: Optional[int]) -> None:
        """Малює таблицю префікс-функції."""
        pattern = self.pattern_value.get().strip()
        y0 = 335
        self.canvas.create_text(35, y0, anchor="w", text="Таблиця префікс-функції", font=("Arial", 12, "bold"))

        labels = ["i", "pattern[i]", "prefix[i]"]
        for row, label in enumerate(labels):
            self.canvas.create_text(35, y0 + 40 + row * 35, anchor="w", text=label, font=("Arial", 10, "bold"))

        start_x = 120
        for index, char in enumerate(pattern):
            fill = "#ffe99a" if active_index == index else "white"
            outline = "#c48a00" if active_index == index else "#9aa4b2"

            values = [str(index), char, str(prefix[index]) if index < len(prefix) else "0"]
            for row, val in enumerate(values):
                x = start_x + index * self.cell_width
                y = y0 + 25 + row * 35
                self.canvas.create_rectangle(x, y, x + 28, y + 28, fill=fill, outline=outline, width=2)
                self.canvas.create_text(x + 14, y + 14, text=val, font=("Arial", 10, "bold"))

    def _log(self, message: str) -> None:
        """Додає повідомлення до логу."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")


def main() -> None:
    """Точка входу в програму."""
    root = tk.Tk()
    KMPVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
