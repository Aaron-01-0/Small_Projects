import customtkinter as ctk
from datetime import datetime
import json
import os

class TodoApp:
    def __init__(self):
        # Set up the window
        self.window = ctk.CTk()
        self.window.title("Modern Todo List")
        self.window.geometry("600x700")
        self.window.configure(fg_color="#2b2b2b")

        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Load existing todos
        self.todos = self.load_todos()

        self.create_widgets()

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        header_frame.pack(pady=20, padx=20, fill="x")

        title_label = ctk.CTkLabel(
            header_frame,
            text="Todo List",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack()

        # Input area
        input_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        input_frame.pack(pady=10, padx=20, fill="x")

        self.task_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter a new task...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.task_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        add_button = ctk.CTkButton(
            input_frame,
            text="Add Task",
            width=100,
            height=40,
            command=self.add_task,
            font=ctk.CTkFont(size=14)
        )
        add_button.pack(side="right")

        # Tasks area
        self.tasks_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent",
            height=500
        )
        self.tasks_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Bind Enter key to add_task
        self.window.bind('<Return>', lambda event: self.add_task())

        # Load existing todos
        self.refresh_tasks()

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            # Create new todo
            todo = {
                "text": task_text,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.todos.append(todo)
            self.save_todos()
            self.task_entry.delete(0, 'end')
            self.refresh_tasks()

    def toggle_task(self, index):
        self.todos[index]["completed"] = not self.todos[index]["completed"]
        self.save_todos()
        self.refresh_tasks()

    def delete_task(self, index):
        del self.todos[index]
        self.save_todos()
        self.refresh_tasks()

    def refresh_tasks(self):
        # Clear existing tasks
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        if not self.todos:
            empty_label = ctk.CTkLabel(
                self.tasks_frame,
                text="No tasks yet. Add one above!",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            empty_label.pack(pady=20)
            return

        # Recreate task widgets
        for i, todo in enumerate(self.todos):
            task_frame = ctk.CTkFrame(
                self.tasks_frame,
                fg_color=("#f0f0f0", "#333333"),
                corner_radius=10
            )
            task_frame.pack(pady=5, padx=5, fill="x")

            checkbox = ctk.CTkCheckBox(
                task_frame,
                text="",
                command=lambda i=i: self.toggle_task(i),
                width=20
            )
            checkbox.pack(side="left", padx=10, pady=10)
            checkbox.select() if todo["completed"] else checkbox.deselect()

            task_text = ctk.CTkLabel(
                task_frame,
                text=todo["text"],
                font=ctk.CTkFont(size=14),
                text_color=("gray" if todo["completed"] else "white")
            )
            task_text.pack(side="left", pady=10, fill="x", expand=True)

            delete_btn = ctk.CTkButton(
                task_frame,
                text="Delete",
                width=70,
                height=30,
                fg_color="transparent",
                hover_color="#ff4444",
                command=lambda i=i: self.delete_task(i)
            )
            delete_btn.pack(side="right", padx=10, pady=10)

    def load_todos(self):
        try:
            if os.path.exists("todos.json"):
                with open("todos.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_todos(self):
        with open("todos.json", "w") as f:
            json.dump(self.todos, f)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TodoApp()
    app.run()
