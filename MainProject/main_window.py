import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import os
import sys

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hypersonic Impact Modeling")
        self.geometry("350x380")
        self.resizable(True, True)
        self.configure(bg="#2d2d2d")
        
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 14, "bold"), background="#2d2d2d", foreground="white")
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.programs = {
            '3d': {'path': os.path.join("3d_programme", "pygame_main.py"), 'process': None, 'button': None},
            '2d': {'path': os.path.join("2d_programme", "2d_module.py"), 'process': None, 'button': None}
        }

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.check_processes()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg="#2d2d2d")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        title_label = ttk.Label(main_frame, text="Hypersonic Impact Modeling", style="TLabel")
        title_label.pack(pady=30)

        button_frame = tk.Frame(main_frame, bg="#2d2d2d")
        button_frame.pack(expand=True)

        self.programs['3d']['button'] = tk.Button(button_frame, 
                                                 text="Запустить 3D визуализацию", 
                                                 font=("Arial", 12), bg="#2d2d2d", fg="#007acc",
                                                 activebackground="#4a4a4a", activeforeground="#007acc",
                                                 relief="flat", pady=10,
                                                 command=lambda: self.start_program('3d'))
        self.programs['3d']['button'].pack(pady=10, fill='x', padx=50)

        self.programs['2d']['button'] = tk.Button(button_frame, 
                                                 text="Запустить 2D визуализацию", 
                                                 font=("Arial", 12), bg="#2d2d2d", fg="#007acc",
                                                 activebackground="#4a4a4a", activeforeground="#007acc",
                                                 relief="flat", pady=10,
                                                 command=lambda: self.start_program('2d'))
        self.programs['2d']['button'].pack(pady=10, fill='x', padx=50)

        self.stop_button = tk.Button(button_frame, 
                                    text="Завершить все и выйти", 
                                    font=("Arial", 12), bg="#2d2d2d", fg="white",
                                    activebackground="#4a4a4a", activeforeground="#007acc",
                                    relief="flat", pady=10, command=self.stop_all)
        self.stop_button.pack(pady=20, fill='x', padx=50)

    def start_program(self, program_type):
        config = self.programs[program_type]
        if self.process_running(config['process']):
            messagebox.showinfo("Информация", f"Программа {program_type.upper()} уже запущена.")
            return

        full_path = os.path.join(self.base_dir, config['path'])
        if not self.validate_path(full_path):
            return

        try:
            config['process'] = subprocess.Popen([sys.executable, full_path],
                                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0)
            print(f"Запущен процесс {program_type}: PID {config['process'].pid}")
            config['button'].config(state='disabled')
        except Exception as e:
            print(f"Ошибка запуска {program_type}: {e}")
            messagebox.showerror("Ошибка", f"Не удалось запустить {program_type.upper()}:\n{str(e)}")
            config['process'] = None
            config['button'].config(state='normal')

    def validate_path(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Ошибка", f"Файл не найден: {path}")
            return False
        return True

    def stop_all(self):
        for prog in self.programs.values():
            self.terminate_process(prog['process'])
            prog['button'].config(state='normal')
        self.destroy()

    def on_closing(self):
        #if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите завершить все программы и выйти?"):
            self.stop_all()

    def check_processes(self):
        for prog_type, config in self.programs.items():
            if config['process'] is not None and not self.process_running(config['process']):
                print(f"Процесс {prog_type} (PID: {config['process'].pid}) завершён")
                config['process'] = None
                config['button'].config(state='normal')
        self.after(500, self.check_processes) 

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