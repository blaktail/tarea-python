import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()


# db connection 
class Task(Base):
    __tablename__ = 'tareas'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)

engine = create_engine('sqlite:///dbtareas.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


# main
class TaskManager:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestor de Tareas")
        self.session = Session()

        name = 'Nombre'
        description = 'Descripción'
        state = 'Estado'

        self.tree = ttk.Treeview(master, columns=(name, description, state), show='headings')
        self.tree.heading(name, text=name)
        self.tree.heading(description, text=description)
        self.tree.heading(state, text=state)
        self.tree.pack(pady=10)
        input_frame = ttk.Frame(master)
        input_frame.pack(pady=10)

        self.name_entry = ttk.Entry(input_frame, width=40)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        self.description_entry = ttk.Entry(input_frame, width=40)
        self.description_entry.pack(side=tk.LEFT, padx=5)
        

        ttk.Button(master, text="Agregar Tarea", command=self.add_task).pack(pady=5)
        ttk.Button(master, text="Marcar como Completada", command=self.mark_completed).pack(pady=5)
        ttk.Button(master, text="Eliminar Tarea", command=self.delete_task).pack(pady=5)
        ttk.Button(master, text="Guardar Tareas", command=self.save_tasks).pack(pady=5)
        ttk.Button(master, text="Cargar Tareas", command=self.load_tasks).pack(pady=5)

        self.load_tasks_from_db()

    def add_task(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        if description and name:
            new_task = Task(name=name, description=description)
            self.session.add(new_task)
            self.session.commit()
            self.tree.insert('', 'end', values=(name, description, 'Pendiente'))
            self.name_entry.delete(0, 'end')
            self.description_entry.delete(0, 'end')
        else:
            messagebox.showwarning("Advertencia", "Por favor, ingrese un nombre y descripción de la tarea.")

    def mark_completed(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_name = self.tree.item(selected_item)['values'][0]
            task_description = self.tree.item(selected_item)['values'][1]
            task = self.session.query(Task).filter_by(name=task_name).first()
            if task:
                task.completed = True
                self.session.commit()
                self.tree.item(selected_item, values=(task_name,task_description, 'Completada'))
        else:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una tarea.")

    def delete_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_name = self.tree.item(selected_item)['values'][0]
            task = self.session.query(Task).filter_by(name=task_name).first()
            if task:
                self.session.delete(task)
                self.session.commit()
                self.tree.delete(selected_item)
        else:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una tarea.")

    def save_tasks(self):
        tasks = self.session.query(Task).all()
        tasks_data = [{'name': task.name,'description': task.description, 'completed': task.completed} for task in tasks]
        file_path = filedialog.asksaveasfilename(defaultextension=".json")
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(tasks_data, f)
            messagebox.showinfo("Éxito", "Tareas guardadas exitosamente.")

    def load_tasks(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                tasks_data = json.load(f)
            self.session.query(Task).delete()
            for task_data in tasks_data:
                new_task = Task(name=task_data['name'],description=task_data['description'], completed=task_data['completed'])
                self.session.add(new_task)
            self.session.commit()
            self.load_tasks_from_db()
            messagebox.showinfo("Éxito", "Tareas cargadas exitosamente.")

    def load_tasks_from_db(self):
        self.tree.delete(*self.tree.get_children())
        tasks = self.session.query(Task).all()
        for task in tasks:
            status = 'Completada' if task.completed else 'Pendiente'
            self.tree.insert('', 'end', values=(task.name, task.description, status))

# execute
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()