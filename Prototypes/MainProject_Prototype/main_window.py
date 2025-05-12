import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hypersonic Impact Modeling")
        self.geometry("300x190")
        self.resizable(True, True)
        self.minsize(300, 190)
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.programs = {
            '3d': {'path': os.path.join("3d_programme", "pygame_main.py"), 'process': None, 'button': None},
            '2d': {'path': os.path.join("2d_programme", "2d_module.py"), 'process': None, 'button': None}
        }

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.check_processes()

    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(expand=True, fill='both')

        button_frame = tk.Frame(main_frame)
        button_frame.pack(expand=True, fill='both')

        self.programs['3d']['button'] = tk.Button(button_frame, 
                                                 text="3D visualization",
                                                 bg="green", fg="white", font=(None, 11, "bold"),
                                                 command=lambda: self.start_program('3d'))
        self.programs['3d']['button'].pack(expand=True, fill='both')

        self.programs['2d']['button'] = tk.Button(button_frame, 
                                                 text="2D visualization",
                                                 bg="green", fg="white", font=(None, 11, "bold"),
                                                 command=lambda: self.start_program('2d'))
        self.programs['2d']['button'].pack(expand=True, fill='both')

        self.stop_button = tk.Button(button_frame, 
                                    text="Complete everything and exit",
                                    bg="red", fg="white", font=(None, 11, "bold"),
                                    command=self.stop_all)
        self.stop_button.pack(expand=True, fill='both')

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
            # Устанавливаем серый фон и белый текст для активной кнопки
            config['button'].config(state='disabled', bg='grey', fg='white')
        except Exception as e:
            print(f"Ошибка запуска {program_type}: {e}")
            messagebox.showerror("Ошибка", f"Не удалось запустить {program_type.upper()}:\n{str(e)}")
            config['process'] = None
            config['button'].config(state='normal', bg='green', fg='white')

    def check_processes(self):
        for prog_type, config in self.programs.items():
            if config['process'] is not None and not self.process_running(config['process']):
                print(f"Процесс {prog_type} (PID: {config['process'].pid}) завершён")
                config['process'] = None
                config['button'].config(state='normal', bg='green', fg='white')
        self.after(500, self.check_processes)

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