# Task Calendar

A desktop-friendly task calendar that lets you add, review, and complete dated tasks with a simple graphical interface.

## Features
- Add tasks to any day using a guided dialog.
- Browse every scheduled task in date order with button toggles for completion status, then mark items done.
- Explore a color-coded monthly calendar that highlights days with pending or completed work.
- Persistent storage in `tasks.json` so your tasks stay available between sessions.

## Getting Started
1. Ensure you have Python 3.9 or later available.
2. Install the Tkinter dependencies if your platform does not bundle them (they ship with standard Python on Windows and most Linux distributions).
3. Launch the application:
   ```bash
   python tasks_calendar.py
   ```
4. Use the main menu buttons to add tasks, open the task list, or view the monthly calendar.

### Calendar Legend
- **Orange cells** – at least one task scheduled for that day still needs attention.
- **Green cells** – every task on that day is complete.

Your data is saved automatically in `tasks.json` in the project directory.

## Troubleshooting

If you encounter the message `stream disconnected before completion: Your input exceeds the context window of this model` while working with an AI assistant, refer to [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for guidance on trimming the request so it fits within the model's context limit.
