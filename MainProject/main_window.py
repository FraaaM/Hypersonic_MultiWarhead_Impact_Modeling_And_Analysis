import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import sys

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hypersonic Impact Modeling")
        self.geometry("400x300")
        self.resizable(True, True)
        self.minsize(400, 300)

        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.programs = {
            '3d': {'path': os.path.join("3d_programme", "pygame_main.py"), 'process': None, 'button': None},
            '2d': {'path': os.path.join("2d_programme", "2d_module.py"), 'process': None, 'button': None}
        }

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.check_processes()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#f0f0f0")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        title_label = tk.Label(
            main_frame,
            text="Hypersonic Impact Modeling",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=(0, 20))

        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(expand=True, fill='both')

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        style.map("TButton", background=[("active", "#005f73")])

        self.programs['3d']['button'] = ttk.Button(
            button_frame,
            text="3D Visualization",
            command=lambda: self.start_program('3d'),
            style="TButton"
        )
        self.programs['3d']['button'].pack(expand=True, fill='both', pady=(10, 10))

        self.programs['2d']['button'] = ttk.Button(
            button_frame,
            text="2D Visualization",
            command=lambda: self.start_program('2d'),
            style="TButton"
        )
        self.programs['2d']['button'].pack(expand=True, fill='both', pady=(10, 10))

        self.stop_button = ttk.Button(
            button_frame,
            text="Stop All and Exit",
            command=self.stop_all,
            style="TButton"
        )
        self.stop_button.pack(expand=True, fill='both', pady=(10, 0))

    def start_program(self, program_type):
        config = self.programs[program_type]
        if self.process_running(config['process']):
            messagebox.showinfo("Information", f"{program_type.upper()} is already running.")
            return

        full_path = os.path.join(self.base_dir, config['path'])
        if not self.validate_path(full_path):
            return

        try:
            config['process'] = subprocess.Popen(
                [sys.executable, full_path],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            print(f"Started {program_type} process: PID {config['process'].pid}")
            config['button'].config(state='disabled')
        except Exception as e:
            print(f"Error starting {program_type}: {e}")
            messagebox.showerror("Error", f"Failed to start {program_type.upper()}:\n{str(e)}")
            config['process'] = None
            config['button'].config(state='normal')

    def check_processes(self):
        for prog_type, config in self.programs.items():
            if config['process'] is not None and not self.process_running(config['process']):
                print(f"Process {prog_type} (PID: {config['process'].pid}) terminated")
                config['process'] = None
                config['button'].config(state='normal')
        self.after(500, self.check_processes)

    def validate_path(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Error", f"File not found: {path}")
            return False
        return True

    def stop_all(self):
        for prog in self.programs.values():
            self.terminate_process(prog['process'])
            prog['button'].config(state='normal')
        self.destroy()

    def on_closing(self):
        self.stop_all()

    @staticmethod
    def process_running(process):
        return process and process.poll() is None

    @staticmethod
    def terminate_process(process):
        if process and process.poll() is None:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    app = Application()
    app.mainloop()