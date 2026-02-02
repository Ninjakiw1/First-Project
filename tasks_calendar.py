"""Graphical task calendar application."""
from __future__ import annotations

import calendar
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = Path("tasks.json")


@dataclass
class Task:
    description: str
    completed: bool = False

    def mark_completed(self) -> None:
        self.completed = True


class TaskCalendar:
    def __init__(self, data_file: Path = DATA_FILE) -> None:
        self.data_file = data_file
        self.tasks: Dict[str, List[Task]] = {}
        self.load()

    def load(self) -> None:
        if self.data_file.exists():
            try:
                data = json.loads(self.data_file.read_text())
                self.tasks = {
                    day: [Task(**task) for task in tasks]
                    for day, tasks in data.items()
                }
            except json.JSONDecodeError:
                messagebox.showwarning(
                    "Task Calendar",
                    "tasks.json is corrupted. Starting with an empty calendar.",
                )
                self.tasks = {}
        else:
            self.tasks = {}

    def save(self) -> None:
        data = {
            day: [asdict(task) for task in tasks]
            for day, tasks in self.tasks.items()
        }
        self.data_file.write_text(json.dumps(data, indent=2))

    def add_task(self, task_date: date, description: str) -> None:
        key = task_date.isoformat()
        self.tasks.setdefault(key, []).append(Task(description=description))
        self.save()

    def list_tasks(self, task_date: date) -> List[Task]:
        return self.tasks.get(task_date.isoformat(), [])

    def iter_tasks(self) -> List[tuple[date, int, Task]]:
        """Return all tasks sorted by date with their index on that date."""

        items: List[tuple[date, int, Task]] = []
        for day_key, tasks in self.tasks.items():
            try:
                day_date = date.fromisoformat(day_key)
            except ValueError:
                # Skip malformed keys silently; they cannot be mapped to dates.
                continue
            for idx, task in enumerate(tasks):
                items.append((day_date, idx, task))

        items.sort(key=lambda item: item[0])
        return items

    def mark_task_completed(self, task_date: date, index: int) -> bool:
        tasks = self.list_tasks(task_date)
        if 0 <= index < len(tasks):
            tasks[index].mark_completed()
            self.save()
            return True
        return False

    def has_tasks(self, task_date: date) -> bool:
        return bool(self.list_tasks(task_date))

    def all_tasks_completed(self, task_date: date) -> bool:
        tasks = self.list_tasks(task_date)
        return tasks != [] and all(task.completed for task in tasks)


class TaskCalendarGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.calendar = TaskCalendar()
        self.root.title("Task Calendar")
        self.root.geometry("360x260")

        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            main_frame,
            text="Task Calendar",
            font=("Segoe UI", 18, "bold"),
            anchor="center",
        )
        title.pack(pady=(0, 20))

        ttk.Button(
            main_frame,
            text="Add Task",
            command=self.open_add_task_window,
            width=25,
        ).pack(pady=5)

        ttk.Button(
            main_frame,
            text="View Task List",
            command=self.open_view_tasks_window,
            width=25,
        ).pack(pady=5)

        ttk.Button(
            main_frame,
            text="View Monthly Calendar",
            command=self.open_view_calendar_window,
            width=25,
        ).pack(pady=5)

        ttk.Button(
            main_frame,
            text="Quit",
            command=self.root.destroy,
            width=25,
        ).pack(pady=(20, 0))

    def open_add_task_window(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Add Task")
        window.geometry("320x180")
        window.resizable(False, False)

        frame = ttk.Frame(window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        date_var = tk.StringVar()
        desc_var = tk.StringVar()

        ttk.Label(frame, text="Date (YYYY-MM-DD):").pack(anchor="w")
        date_entry = ttk.Entry(frame, textvariable=date_var)
        date_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, text="Description:").pack(anchor="w")
        desc_entry = ttk.Entry(frame, textvariable=desc_var)
        desc_entry.pack(fill=tk.X, pady=(0, 10))

        def save_task() -> None:
            try:
                task_date = datetime.strptime(date_var.get(), "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror(
                    "Add Task", "Please enter a valid date in YYYY-MM-DD format."
                )
                return

            description = desc_var.get().strip()
            if not description:
                messagebox.showerror("Add Task", "Task description cannot be empty.")
                return

            self.calendar.add_task(task_date, description)
            messagebox.showinfo("Add Task", "Task added successfully.")
            window.destroy()

        ttk.Button(frame, text="Save Task", command=save_task).pack(pady=(5, 0))

    def open_view_tasks_window(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Task List")
        window.geometry("420x360")
        window.resizable(False, False)

        frame = ttk.Frame(window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        filters = ttk.Frame(frame)
        filters.pack(fill=tk.X, pady=(0, 10))

        date_var = tk.StringVar()
        status_var = tk.StringVar(value="All")

        ttk.Label(filters, text="Date (YYYY-MM-DD):").grid(
            row=0, column=0, sticky="w"
        )
        date_entry = ttk.Entry(filters, textvariable=date_var, width=18)
        date_entry.grid(row=1, column=0, sticky="we", padx=(0, 10))

        def clear_date() -> None:
            date_var.set("")
            apply_filters()

        ttk.Button(
            filters,
            text="Clear Date Filter",
            command=clear_date,
            width=18,
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))

        style = ttk.Style(window)
        style.configure("Filter.TRadiobutton", indicatoron=False, padding=4)

        status_frame = ttk.Frame(filters)
        status_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
        ttk.Label(status_frame, text="Status:").pack(anchor="w")

        status_buttons = ttk.Frame(status_frame)
        status_buttons.pack(fill=tk.X, pady=(4, 0))

        status_options = [
            ("All Tasks", "All"),
            ("Completed", "Completed"),
            ("Pending", "Not Completed"),
        ]

        filters.columnconfigure(0, weight=1)
        filters.columnconfigure(1, weight=1)

        tasks_box = tk.Listbox(frame, height=10)
        tasks_box.pack(fill=tk.BOTH, expand=True)

        status_label = ttk.Label(frame, text="")
        status_label.pack(fill=tk.X, pady=(5, 0))

        displayed_tasks: List[tuple[date, int]] = []

        def apply_filters() -> None:
            tasks_box.delete(0, tk.END)
            status_label.config(text="")
            displayed_tasks.clear()

            filter_text = date_var.get().strip()
            filter_date = None
            if filter_text:
                try:
                    filter_date = datetime.strptime(filter_text, "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror(
                        "Task List", "Please enter a valid date in YYYY-MM-DD format."
                    )
                    return

            status_filter = status_var.get()

            for task_date, idx, task in self.calendar.iter_tasks():
                if filter_date and task_date != filter_date:
                    continue
                if status_filter == "Completed" and not task.completed:
                    continue
                if status_filter == "Not Completed" and task.completed:
                    continue

                status = "✓" if task.completed else "✗"
                tasks_box.insert(
                    tk.END,
                    f"{task_date.isoformat()}  [{status}] {task.description}",
                )
                displayed_tasks.append((task_date, idx))

            if not displayed_tasks:
                status_label.config(text="No tasks match the selected filters.")

        for text, value in status_options:
            ttk.Radiobutton(
                status_buttons,
                text=text,
                value=value,
                variable=status_var,
                command=apply_filters,
                style="Filter.TRadiobutton",
            ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        date_entry.bind("<Return>", lambda _: apply_filters())

        def mark_completed() -> None:
            selection = tasks_box.curselection()
            if not selection:
                messagebox.showwarning("Task List", "Select a task to mark as completed.")
                return

            task_date, idx = displayed_tasks[selection[0]]
            if self.calendar.mark_task_completed(task_date, idx):
                messagebox.showinfo("Task List", "Task marked as completed.")
                apply_filters()
            else:
                messagebox.showerror("Task List", "Unable to mark the task as completed.")

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons, text="Refresh List", command=apply_filters).pack(
            side=tk.LEFT
        )
        ttk.Button(
            buttons, text="Mark Selected Completed", command=mark_completed
        ).pack(side=tk.RIGHT)

        apply_filters()

    def open_view_calendar_window(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Monthly Calendar")
        window.geometry("420x380")
        window.resizable(False, False)

        frame = ttk.Frame(window, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        today = date.today()
        year_var = tk.IntVar(value=today.year)
        month_var = tk.IntVar(value=today.month)

        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Year:").grid(row=0, column=0, padx=(0, 5))
        year_spin = ttk.Spinbox(controls, from_=1900, to=2100, textvariable=year_var, width=6)
        year_spin.grid(row=0, column=1)

        ttk.Label(controls, text="Month:").grid(row=0, column=2, padx=(10, 5))
        month_spin = ttk.Spinbox(controls, from_=1, to=12, textvariable=month_var, width=4)
        month_spin.grid(row=0, column=3)

        calendar_frame = ttk.Frame(frame)
        calendar_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        legend = ttk.Label(
            frame,
            text="Orange: tasks pending  |  Green: all tasks completed",
            font=("Segoe UI", 9),
        )
        legend.pack(pady=(0, 10))

        def render_calendar() -> None:
            for child in calendar_frame.winfo_children():
                child.destroy()

            try:
                year = int(year_var.get())
                month = int(month_var.get())
            except ValueError:
                messagebox.showerror("Monthly Calendar", "Year and month must be numbers.")
                return

            if month < 1 or month > 12:
                messagebox.showerror("Monthly Calendar", "Month must be between 1 and 12.")
                return

            ttk.Label(
                calendar_frame,
                text=f"{calendar.month_name[month]} {year}",
                font=("Segoe UI", 14, "bold"),
            ).grid(row=0, column=0, columnspan=7, pady=(0, 10))

            weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for idx, weekday in enumerate(weekdays):
                ttk.Label(
                    calendar_frame,
                    text=weekday,
                    font=("Segoe UI", 10, "bold"),
                ).grid(row=1, column=idx, padx=5, pady=5)

            cal = calendar.Calendar(firstweekday=0)
            for row, week in enumerate(cal.monthdatescalendar(year, month), start=2):
                for col, day_date in enumerate(week):
                    text = str(day_date.day)
                    fg = "black"
                    bg = "white"

                    if day_date.month != month:
                        fg = "#9e9e9e"

                    if self.calendar.has_tasks(day_date):
                        if self.calendar.all_tasks_completed(day_date):
                            bg = "#c8f7c5"
                        else:
                            bg = "#fdd9b5"

                    label = tk.Label(
                        calendar_frame,
                        text=text,
                        width=5,
                        height=2,
                        bg=bg,
                        fg=fg,
                        relief=tk.RIDGE,
                        borderwidth=1,
                    )
                    label.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

        ttk.Button(controls, text="Show", command=render_calendar).grid(
            row=0, column=4, padx=(10, 0)
        )
        render_calendar()


def main() -> None:
    root = tk.Tk()
    TaskCalendarGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
