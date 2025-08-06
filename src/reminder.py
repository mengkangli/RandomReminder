# ./src/reminder.py

import tkinter as tk
import random
import threading
import time
from src.log_manager import LogManager
from tkinter import messagebox
from tkinter import *
from playsound import playsound

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("定时提醒软件")
        self.root.geometry("400x300")
        self.root.configure(bg="#f0f8ff")

        # 用于控制提醒线程是否运行
        self.running = False

        # 创建页面
        self.main_frame = tk.Frame(self.root, bg="#f0f8ff")
        self.reminder_frame = tk.Frame(self.root, bg="#f0f8ff")

        self.create_main_page()
        self.create_reminder_page()

        self.show_main_page()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.log_manager = LogManager()  # 初始化日志系统

    def create_main_page(self):
        frame = self.main_frame

        title_label = tk.Label(frame, text="定时提醒软件", font=("Arial", 18), bg="#f0f8ff")
        title_label.pack(pady=10)

        # 输入 t1
        self.t1_label = tk.Label(frame, text="请输入 t1（分钟）:", bg="#f0f8ff")
        self.t1_label.pack()
        self.t1_entry = tk.Entry(frame, width=30)
        self.t1_entry.pack(pady=5)

        # 输入 t2
        self.t2_label = tk.Label(frame, text="请输入 t2（分钟）:", bg="#f0f8ff")
        self.t2_label.pack()
        self.t2_entry = tk.Entry(frame, width=30)
        self.t2_entry.pack(pady=5)

        # 输入 t3
        self.t3_label = tk.Label(frame, text="请输入 t3（分钟）:", bg="#f0f8ff")
        self.t3_label.pack()
        self.t3_entry = tk.Entry(frame, width=30)
        self.t3_entry.pack(pady=5)

        # 启动按钮
        start_button = tk.Button(frame, text="启动提醒", command=self.start_reminders, bg="#4caf50", fg="white", width=20)
        start_button.pack(pady=20)

    def create_reminder_page(self):
        frame = self.reminder_frame

        label = tk.Label(frame, text="提醒已经启动", font=("Arial", 18), bg="#f0f8ff")
        label.pack(pady=50)

        back_button = tk.Button(frame, text="重新设置", command=self.back_to_settings, bg="#2196f3", fg="white", width=20)
        back_button.pack()

    def show_main_page(self):
        self.reminder_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)

    def show_reminder_page(self):
        self.main_frame.pack_forget()
        self.reminder_frame.pack(fill="both", expand=True)

    def back_to_settings(self):
        self.running = False
        self.show_main_page()

    def start_reminders(self):
        try:
            t1 = float(self.t1_entry.get())
            t2 = float(self.t2_entry.get())
            t3 = float(self.t3_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字！")
            return

        if t1 <= 0 or t2 <= 0 or t3 <= 0:
            messagebox.showerror("错误", "请输入正数！")
            return

        if t1 >= t2:
            messagebox.showerror("错误", "t1 必须小于 t2！")
            return

        # 跳转到提醒页面
        self.show_reminder_page()

        # 启动提醒线程
        self.running = True
        threading.Thread(target=self.run_reminders, args=(t1, t2, t3), daemon=True).start()

    def run_reminders(self, t1, t2, t3):
        # 转换为秒
        t1_seconds = t1 * 60
        t2_seconds = t2 * 60
        t3_seconds = t3 * 60

        # 独立计时器
        next_eye_time = time.time() + random.uniform(t1_seconds, t2_seconds)
        next_rest_time = time.time() + t3_seconds

        while self.running:
            current_time = time.time()

            # 优先处理休息提醒
            if current_time >= next_rest_time:
                duration = self.show_countdown_popup("休息提醒", "请休息", 20 * 60)
                print(f"用户休息了 {duration} 秒")
                next_rest_time = current_time + duration + t3_seconds  # 更新下一次休息时间
                # 休息期间可能跳过了若干次闭眼提醒，更新闭眼提醒时间
                next_eye_time = current_time + duration + random.uniform(t1_seconds, t2_seconds)
                self.log_manager.log_reminder("休息", next_rest_time, duration)
                continue

            # 处理闭眼提醒
            if current_time >= next_eye_time:
                duration = self.show_countdown_popup("闭眼提醒", "请闭眼", 10)
                print(f"用户闭眼了 {duration} 秒")
                next_eye_time = current_time + duration + random.uniform(t1_seconds, t2_seconds)
                self.log_manager.log_reminder("闭眼", next_eye_time, duration)
                continue

            # 如果两者都没有触发，检查哪个更近，适当调整等待时间，减少CPU占用
            wait_time = min(next_rest_time, next_eye_time) - current_time
            if wait_time > 0:
                time.sleep(min(wait_time, 0.5))  # 最多等待0.5秒
            else:
                time.sleep(0.1)

            



    def show_countdown_popup(self, title, message, total_seconds, play_sound=True):
        popup = Toplevel(self.root)
        popup.title(title)
        popup.geometry("350x150")
        popup.configure(bg="#fffacd")
        popup.grab_set()

        self.countdown_active = True
        start_time = time.time()

        label = Label(popup, text="", font=("Arial", 16), bg="#fffacd")
        label.pack(expand=True)

        def play_sound_effect(sound_file, enabled=True):
            if enabled and sound_file:
                try:
                    playsound(sound_file)
                except Exception as e:
                    print("音效播放失败:", e)

        threading.Thread(
            target=play_sound_effect,
            args=("sounds/eye.wav", play_sound),
            daemon=True
        ).start()

        def update_label(seconds_left):
            if self.countdown_active and seconds_left >= 0 and self.running:
                label.config(text=f"{message} 剩余时间：{seconds_left} 秒")
                if seconds_left > 0:
                    popup.after(1000, update_label, seconds_left - 1)
                else:
                    popup.destroy()

        def skip_countdown():
            self.countdown_active = False
            popup.destroy()

        skip_button = Button(popup, text="提前结束", command=skip_countdown, bg="#ff7f0e", fg="white")
        skip_button.pack(pady=5)

        update_label(total_seconds)

        self.root.wait_window(popup)

        self.actual_duration = int(time.time() - start_time)
        return self.actual_duration

    def on_closing(self):
        self.running = False
        self.log_manager.generate_report()  # 生成报告
        self.root.destroy()


# 启动程序
if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()