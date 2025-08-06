# ./src/log_manager.py

import os
import time
import csv
import matplotlib.pyplot as plt

class LogManager:
    def __init__(self):
        # 创建日志目录
        timestamp = time.strftime("%Y_%m_%d_%H_%M_%S")
        self.log_dir = os.path.join("logs", timestamp)
        os.makedirs(self.log_dir, exist_ok=True)

        # 初始化日志文件
        self.log_file = os.path.join(self.log_dir, "log.csv")
        self.headers = ["timestamp", "type", "scheduled_time", "actual_duration"]
        self.log_data = []

        # 创建 CSV 文件并写入表头
        with open(self.log_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()

    def log_reminder(self, remind_type, scheduled_time, actual_duration):
        # 构建日志条目
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "type": remind_type,
            "scheduled_time": scheduled_time,
            "actual_duration": actual_duration,
        }
        self.log_data.append(log_entry)

        # 写入 CSV 文件
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(log_entry)

    def generate_report(self):
        if not self.log_data:
            return

        # 设置中文字体
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False

        # 提取数据
        timestamps = [entry["timestamp"] for entry in self.log_data]
        types = [entry["type"] for entry in self.log_data]
        durations = [int(entry["actual_duration"]) for entry in self.log_data]
        indices = list(range(len(timestamps)))

        # 分类数据
        eye_durations = [d for d, t in zip(durations, types) if t == "闭眼"]
        rest_durations = [d for d, t in zip(durations, types) if t == "休息"]
        eye_indices = [i for i, t in enumerate(types) if t == "闭眼"]
        rest_indices = [i for i, t in enumerate(types) if t == "休息"]

        # 绘图
        plt.figure(figsize=(12, 6))
        plt.title("提醒记录与持续时间")
        plt.xlabel("提醒时间戳")
        plt.ylabel("持续时间（秒）")
        plt.scatter(eye_indices, eye_durations, color="blue", label="闭眼提醒")
        plt.scatter(rest_indices, rest_durations, color="green", label="休息提醒")
        plt.xticks(indices, timestamps, rotation=45, ha="right")
        plt.tight_layout()
        plt.legend()

        # 保存图表
        plot_path = os.path.join(self.log_dir, "remind_stats.png")
        plt.savefig(plot_path)
        plt.close()