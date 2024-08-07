import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import datetime
import xml.etree.ElementTree as ET
import os

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Tracker")

        self.tasks = []
        self.completed_tasks = []
        self.current_task = None
        self.current_task_due_date = None
        self.timer_running = False
        self.timer_seconds = 0

        self.create_widgets()
        self.load_completed_tasks()
        self.check_reminders()

    def create_widgets(self):
        self.task_label = tk.Label(self.root, text="Task:")
        self.task_label.pack()

        self.task_entry = tk.Entry(self.root, width=50)
        self.task_entry.pack()

        self.due_date_label = tk.Label(self.root, text="Due Date:")
        self.due_date_label.pack()

        self.due_date_entry = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.due_date_entry.pack(pady=5)

        self.due_time_label = tk.Label(self.root, text="Due Time (HH:MM):")
        self.due_time_label.pack()

        self.due_time_entry = tk.Entry(self.root, width=5)
        self.due_time_entry.pack(pady=5)

        self.add_task_button = tk.Button(self.root, text="Add Task", command=self.add_task)
        self.add_task_button.pack(pady=5)

        self.task_listbox = tk.Listbox(self.root, width=50, height=10)
        self.task_listbox.pack(pady=5)

        self.current_task_label = tk.Label(self.root, text="Current Task: None", font=("Helvetica", 14))
        self.current_task_label.pack(pady=5)

        self.start_button = tk.Button(self.root, text="Start Pomodoro", command=self.start_pomodoro)
        self.start_button.pack(pady=5)

        self.done_button = tk.Button(self.root, text="Done", command=self.mark_done)
        self.done_button.pack(pady=5)

        self.time_label = tk.Label(self.root, text="25:00", font=("Helvetica", 48))
        self.time_label.pack(pady=5)

        self.break_label = tk.Label(self.root, text="", font=("Helvetica", 24))
        self.break_label.pack(pady=5)

        self.completed_tasks_label = tk.Label(self.root, text="Completed Tasks:", font=("Helvetica", 14))
        self.completed_tasks_label.pack(pady=5)

        self.completed_tasks_listbox = tk.Listbox(self.root, width=50, height=10)
        self.completed_tasks_listbox.pack(pady=5)

    def add_task(self):
        task = self.task_entry.get()
        due_date_str = self.due_date_entry.get_date().strftime("%Y-%m-%d")
        due_time_str = self.due_time_entry.get()

        if task and due_time_str:
            try:
                due_date = datetime.datetime.strptime(f"{due_date_str} {due_time_str}", "%Y-%m-%d %H:%M")
                self.tasks.append((task, due_date))
                self.task_listbox.insert(tk.END, f"{task} (Due: {due_date})")
                self.task_entry.delete(0, tk.END)
                self.due_time_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Invalid time", "Please enter a valid time in the format HH:MM")
        elif task:
            self.tasks.append((task, None))
            self.task_listbox.insert(tk.END, task)
            self.task_entry.delete(0, tk.END)

    def start_pomodoro(self):
        if not self.tasks:
            messagebox.showwarning("No tasks", "Please add a task to start the Pomodoro.")
            return

        if self.timer_running:
            messagebox.showwarning("Timer Running", "The Pomodoro is already running.")
            return

        self.current_task, self.current_task_due_date = self.tasks.pop(0)
        self.task_listbox.delete(0)
        self.current_task_label.config(text=f"Current Task: {self.current_task}")
        self.timer_seconds = 25 * 60
        self.run_timer()

    def run_timer(self):
        if self.timer_seconds > 0:
            self.timer_running = True
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            self.time_label.config(text=f"{minutes:02}:{seconds:02}")
            self.timer_seconds -= 1
            self.root.after(1000, self.run_timer)
        else:
            self.timer_running = False
            self.time_label.config(text="25:00")
            self.break_label.config(text="Take a 5-minute break!")
            self.root.after(5 * 60 * 1000, self.end_break)

    def mark_done(self):
        if self.timer_running:
            self.timer_running = False
            completion_time = datetime.datetime.now()
            self.completed_tasks.append((self.current_task, self.current_task_due_date, completion_time))
            self.completed_tasks_listbox.insert(tk.END, f"{self.current_task} (Completed: {completion_time})")
            self.current_task_label.config(text="Current Task: None")
            self.timer_seconds = 0
            self.time_label.config(text="25:00")
            self.break_label.config(text="Take a 5-minute break!")
            self.save_completed_task(self.current_task, self.current_task_due_date, completion_time)
            self.root.after(5 * 60 * 1000, self.end_break)
        else:
            messagebox.showinfo("No Active Pomodoro", "There is no active Pomodoro session.")

    def end_break(self):
        self.break_label.config(text="")
        if self.tasks:
            self.start_pomodoro()
        else:
            messagebox.showinfo("All Tasks Completed", "You have completed all tasks!")

    def check_reminders(self):
        now = datetime.datetime.now()
        for task, due_date in self.tasks:
            if due_date and now >= due_date:
                messagebox.showwarning("Task Due", f"The task '{task}' is due now!")
                self.tasks.remove((task, due_date))
                self.task_listbox.delete(0, tk.END)
                for t, d in self.tasks:
                    self.task_listbox.insert(tk.END, f"{t} (Due: {d})" if d else t)
        self.root.after(60000, self.check_reminders)  # Check every minute

    def save_completed_task(self, task, due_date, completion_time):
        root = None
        if os.path.exists("completed_tasks.xml"):
            tree = ET.parse("completed_tasks.xml")
            root = tree.getroot()
        else:
            root = ET.Element("tasks")

        task_element = ET.SubElement(root, "task")
        task_name = ET.SubElement(task_element, "name")
        task_name.text = task

        if due_date:
            due_date_element = ET.SubElement(task_element, "due_date")
            due_date_element.text = due_date.strftime("%Y-%m-%d %H:%M")

        completion_time_element = ET.SubElement(task_element, "completion_time")
        completion_time_element.text = completion_time.strftime("%Y-%m-%d %H:%M")

        tree = ET.ElementTree(root)
        tree.write("completed_tasks.xml")

    def load_completed_tasks(self):
        if os.path.exists("completed_tasks.xml"):
            tree = ET.parse("completed_tasks.xml")
            root = tree.getroot()

            for task_element in root.findall("task"):
                task_name = task_element.find("name").text
                due_date_element = task_element.find("due_date")
                due_date = datetime.datetime.strptime(due_date_element.text, "%Y-%m-%d %H:%M") if due_date_element is not None else None
                completion_time = datetime.datetime.strptime(task_element.find("completion_time").text, "%Y-%m-%d %H:%M")
                self.completed_tasks.append((task_name, due_date, completion_time))
                self.completed_tasks_listbox.insert(tk.END, f"{task_name} (Completed: {completion_time})")

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
