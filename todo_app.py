import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import os
import threading
from tkinter import messagebox

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Todo List Application')
        
        # Center window on screen
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Set Windows theme
        self.style = ttk.Style()
        self.style.theme_use('vista')
        
        # Initialize database
        self.init_database()
        
        # Create GUI elements
        self.create_gui()
        
        # Load tasks
        self.load_tasks()
        
        # Start notification checker
        self.start_notification_checker()

    def check_due_tasks(self):
        current_time = datetime.now()
        with sqlite3.connect('todo.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT title, due_date 
                FROM tasks 
                WHERE completed = 0 AND due_date IS NOT NULL
            """)
            tasks = cursor.fetchall()
            
            for task in tasks:
                title, due_date = task
                if not due_date:
                    continue
                    
                try:
                    due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
                    
                    # Check if task is due today
                    if due_datetime.date() == current_time.date():
                        messagebox.showinfo(
                            "Task Reminder",
                            f"Task '{title}' is due today ({due_date})!"
                        )
                except ValueError:
                    continue
    
    def start_notification_checker(self):
        self.check_due_tasks()
        # Check for due tasks every minute
        threading.Timer(60, self.start_notification_checker).start()
    
    def init_database(self):
        # Create database and table if they don't exist
        with sqlite3.connect('todo.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    due_date TEXT,
                    completed INTEGER DEFAULT 0
                )
            ''')
            conn.commit()

    def create_gui(self):
        # Configure root window grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Configure custom styles
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        self.style.configure('Action.TButton', padding=5)
        self.style.configure('Priority.High.TLabel', foreground='red')
        self.style.configure('Priority.Medium.TLabel', foreground='orange')
        self.style.configure('Priority.Low.TLabel', foreground='green')

        # Task input frame
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.grid(row=0, column=0, sticky='nsew')
        input_frame.grid_columnconfigure(1, weight=3)
        input_frame.grid_columnconfigure(3, weight=1)
        input_frame.grid_columnconfigure(5, weight=1)
        input_frame.grid_columnconfigure(7, weight=1)

        # Task entry with header
        ttk.Label(input_frame, text="Task:", style='Header.TLabel').grid(row=0, column=0, padx=5, pady=5)
        self.task_entry = ttk.Entry(input_frame)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Category selection
        ttk.Label(input_frame, text="Category:", style='Header.TLabel').grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar(value="General")
        category_combo = ttk.Combobox(input_frame, textvariable=self.category_var,
                                    values=["General", "Work", "Personal", "Shopping", "Study"])
        category_combo.grid(row=0, column=3, padx=5, pady=5, sticky='ew')

        # Priority selection
        ttk.Label(input_frame, text="Priority:", style='Header.TLabel').grid(row=0, column=4, padx=5, pady=5)
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var,
                                    values=["High", "Medium", "Low"])
        priority_combo.grid(row=0, column=5, padx=5, pady=5, sticky='ew')

        # Due date and time frame
        date_time_frame = ttk.Frame(input_frame)
        date_time_frame.grid(row=0, column=6, columnspan=2, padx=5, pady=5, sticky='ew')
        
        ttk.Label(date_time_frame, text="Due Date:", style='Header.TLabel').grid(row=0, column=0, padx=5)
        self.due_date_entry = ttk.Entry(date_time_frame, width=12)
        self.due_date_entry.grid(row=0, column=1, padx=5)
        ttk.Button(date_time_frame, text="📅", command=self.show_calendar).grid(row=0, column=2, padx=2)
        
        ttk.Label(date_time_frame, text="Time:", style='Header.TLabel').grid(row=0, column=3, padx=5)
        self.due_time_var = tk.StringVar(value='00:00')
        self.due_time_entry = ttk.Entry(date_time_frame, textvariable=self.due_time_var, width=8)
        self.due_time_entry.grid(row=0, column=4, padx=5)
        
        # Notification settings
        notification_frame = ttk.Frame(date_time_frame)
        notification_frame.grid(row=1, column=0, columnspan=5, pady=5)
        
        ttk.Label(notification_frame, text="Notify before:", style='Header.TLabel').grid(row=0, column=0, padx=5)
        self.notification_time = ttk.Entry(notification_frame, width=5)
        self.notification_time.insert(0, '10')
        self.notification_time.grid(row=0, column=1, padx=2)
        
        self.notification_unit = ttk.Combobox(notification_frame, values=['minutes', 'hours', 'days'], width=8)
        self.notification_unit.set('minutes')
        self.notification_unit.grid(row=0, column=2, padx=5)

        # Add task button
        add_btn = ttk.Button(input_frame, text="Add Task", command=self.add_task, style='Action.TButton')
        add_btn.grid(row=0, column=8, padx=5, pady=5)

        # Task list with scrollbar
        tree_frame = ttk.Frame(self.root)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Task", "Category", "Priority", "Due Date", "Status"),
                                show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Configure columns with proportional widths
        self.tree.heading("ID", text="ID")
        self.tree.heading("Task", text="Task")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Status", text="Status")

        total_width = self.root.winfo_width()
        self.tree.column("ID", width=int(total_width * 0.05), minwidth=50)
        self.tree.column("Task", width=int(total_width * 0.35), minwidth=200)
        self.tree.column("Category", width=int(total_width * 0.15), minwidth=100)
        self.tree.column("Priority", width=int(total_width * 0.15), minwidth=100)
        self.tree.column("Due Date", width=int(total_width * 0.15), minwidth=100)
        self.tree.column("Status", width=int(total_width * 0.15), minwidth=100)

        # Buttons frame
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.grid(row=2, column=0, sticky='ew')
        button_frame.grid_columnconfigure(2, weight=1)

        ttk.Button(button_frame, text="Mark Complete", command=self.mark_complete, style='Action.TButton').grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Delete Task", command=self.delete_task, style='Action.TButton').grid(row=0, column=1, padx=5)

        # Copyright label with hyperlink
        copyright_frame = ttk.Frame(self.root, padding=5)
        copyright_frame.grid(row=3, column=0, sticky='ew')
        copyright_frame.grid_columnconfigure(0, weight=1)
        
        copyright_text = ttk.Label(copyright_frame, text="© 2024 Developed by ")
        copyright_text.grid(row=0, column=0, sticky='e')
        
        developer_link = ttk.Label(copyright_frame, text="Jasim Uddin", foreground='blue', cursor='hand2')
        developer_link.grid(row=0, column=1, sticky='w')
        developer_link.bind('<Button-1>', lambda e: os.startfile('https://www.facebook.com/jasimuddinevan'))

    def show_calendar(self):
        def validate_date(date_str):
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False

        def set_date():
            date_str = entry.get()
            if validate_date(date_str):
                self.due_date_entry.delete(0, tk.END)
                self.due_date_entry.insert(0, date_str)
                top.destroy()
            else:
                messagebox.showerror('Error', 'Invalid date format! Use YYYY-MM-DD')

        top = tk.Toplevel(self.root)
        top.title('Select Date')
        top.transient(self.root)
        top.grab_set()
        
        frame = ttk.Frame(top, padding='10')
        frame.pack(fill='both', expand=True)
        
        ttk.Label(frame, text='Enter date (YYYY-MM-DD):').pack(pady=5)
        entry = ttk.Entry(frame)
        entry.pack(pady=5)
        entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_frame, text='OK', command=set_date).pack(side='right', padx=5)
        ttk.Button(btn_frame, text='Cancel', command=top.destroy).pack(side='right', padx=5)

    def add_task(self):
        title = self.task_entry.get().strip()
        category = self.category_var.get()
        priority = self.priority_var.get()
        due_date = self.due_date_entry.get().strip()
        due_time = self.due_time_var.get().strip()
        notification_time = self.notification_time.get().strip()
        notification_unit = self.notification_unit.get()

        if not title:
            messagebox.showerror("Error", "Task cannot be empty!")
            return

        try:
            if due_date:
                datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
            return

        with sqlite3.connect('todo.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (title, category, priority, due_date) VALUES (?, ?, ?, ?)",
                         (title, category, priority, due_date))
            conn.commit()

        self.task_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)
        self.load_tasks()

    def load_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        with sqlite3.connect('todo.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY priority DESC, due_date ASC")
            for task in cursor.fetchall():
                status = "Completed" if task[5] else "Pending"
                item = self.tree.insert("", tk.END, values=(task[0], task[1], task[2], task[3], task[4], status))
                
                # Apply color based on priority
                if task[2] == "High":
                    self.tree.tag_configure(f'priority_{item}', foreground='red')
                elif task[2] == "Medium":
                    self.tree.tag_configure(f'priority_{item}', foreground='orange')
                else:  # Low priority
                    self.tree.tag_configure(f'priority_{item}', foreground='green')
                self.tree.item(item, tags=(f'priority_{item}',))
                
                # Highlight overdue tasks
                if task[4] and not task[5]:  # If has due date and not completed
                    try:
                        due_date = datetime.strptime(task[4], '%Y-%m-%d').date()
                        if due_date < datetime.now().date():
                            self.tree.tag_configure(f'overdue_{item}', background='#ffebee')
                            current_tags = self.tree.item(item)['tags']
                            self.tree.item(item, tags=current_tags + (f'overdue_{item}',))
                    except ValueError:
                        pass  # Skip invalid date formats

    def mark_complete(self):
        try:
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a task to mark as complete")
                return

            task_id = self.tree.item(selected_item[0])['values'][0]
            with sqlite3.connect('todo.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
                conn.commit()

            self.load_tasks()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to mark task as complete: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            task_id = self.tree.item(selected_item[0])['values'][0]
            with sqlite3.connect('todo.db') as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()

            self.load_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()