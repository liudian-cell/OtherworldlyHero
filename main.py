"""入口层：设备连接与启动游戏"""

import json
import os

import tkinter as tk
from tkinter import messagebox, ttk

from device_utils import connect_device, screenshot
from image_utils import find_image
from game import start_game
from settings import (
    CONFIG_PATH,
    DIFFICULTY_OPTIONS,
    JOB_DIR,
    AREA_DIR,
    HERO_NAME_MAP,
    SCREENSHOT_PATH,
)


def load_config():
    """
    加载英雄配置，文件不存在则从目录自动生成。
    配置结构: { 英雄名: { 区域名: 难度 } }
    """
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return generate_default_config()


def generate_default_config():
    """从 job 和 area 目录扫描，生成默认配置"""
    heroes = [os.path.splitext(f)[0] for f in sorted(os.listdir(JOB_DIR))
              if f.lower().endswith(".png")]
    areas = [os.path.splitext(f)[0] for f in sorted(os.listdir(AREA_DIR),
              key=lambda x: int(x.split("-")[0]))
              if f.lower().endswith(".png")]
    config = {hero: {area: "默认" for area in areas} for hero in heroes}
    save_config(config)
    return config


def save_config(config):
    """保存英雄配置到 JSON 文件"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def show_start_gui(config):
    """
    显示启动 GUI，使用 Notebook 分页展示每个英雄的区域难度配置。

    Args:
        config: 英雄配置字典 {英雄名: {区域名: 难度}}

    Returns:
        dict: 更新后的配置，取消返回 None
    """
    heroes = list(config.keys())
    combo_vars = {}  # {英雄名: {区域名: StringVar}}

    root = tk.Tk()
    root.title("异世界勇者")
    root.resizable(False, False)

    # --- 标题 ---
    tk.Label(root, text="异世界勇者自动刷本工具", font=("Microsoft YaHei", 14)).grid(
        row=0, column=0, pady=(12, 8)
    )

    # --- Notebook 分页 ---
    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, padx=15, pady=5)

    for hero in heroes:
        tab = tk.Frame(notebook)
        notebook.add(tab, text=HERO_NAME_MAP.get(hero, hero))

        # 表头
        tk.Label(tab, text="区域", font=("Microsoft YaHei", 9, "bold"), width=10,
                 anchor="w").grid(row=0, column=0, padx=(10, 5), pady=(8, 2))
        tk.Label(tab, text="难度", font=("Microsoft YaHei", 9, "bold"), width=8,
                 anchor="w").grid(row=0, column=1, padx=(5, 10), pady=(8, 2))

        hero_vars = {}
        areas = list(config[hero].keys())
        for i, area in enumerate(areas):
            row = i + 1
            tk.Label(tab, text=area, font=("Microsoft YaHei", 9), anchor="w").grid(
                row=row, column=0, padx=(10, 5), pady=1, sticky="w"
            )
            var = tk.StringVar(value=config[hero][area])
            combo = ttk.Combobox(tab, textvariable=var, values=DIFFICULTY_OPTIONS,
                                 state="readonly", width=8)
            combo.grid(row=row, column=1, padx=(5, 10), pady=1, sticky="w")
            hero_vars[area] = var

        combo_vars[hero] = hero_vars

    # --- 批量设置行 ---
    batch_frame = tk.Frame(root)
    batch_frame.grid(row=2, column=0, pady=(5, 0))

    tk.Label(batch_frame, text="当前页批量设置:", font=("Microsoft YaHei", 9)).pack(side="left", padx=(15, 5))

    def apply_batch(difficulty):
        """将当前选中页的所有区域设为指定难度"""
        current_tab = notebook.index(notebook.select())
        hero = heroes[current_tab]
        for area, var in combo_vars[hero].items():
            var.set(difficulty)

    for diff in DIFFICULTY_OPTIONS:
        tk.Button(
            batch_frame, text=diff, font=("Microsoft YaHei", 8),
            width=4, command=lambda d=diff: apply_batch(d)
        ).pack(side="left", padx=2)

    # --- 底部按钮 ---
    btn_frame = tk.Frame(root)
    btn_frame.grid(row=3, column=0, pady=(8, 12))

    result = {"started": False}

    def on_start():
        for hero, area_vars in combo_vars.items():
            for area, var in area_vars.items():
                config[hero][area] = var.get()
        save_config(config)
        root.destroy()
        result["started"] = True

    def on_cancel():
        root.destroy()

    tk.Button(
        btn_frame, text="开始战斗", font=("Microsoft YaHei", 11),
        width=10, command=on_start
    ).pack(side="left", padx=10)

    tk.Button(
        btn_frame, text="取  消", font=("Microsoft YaHei", 11),
        width=10, command=on_cancel
    ).pack(side="left", padx=10)

    # 居中显示
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"+{x}+{y}")

    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()

    return config if result["started"] else None


def main():
    # 1. 连接设备
    d = connect_device()

    # 2. 加载英雄配置并显示 GUI
    config = load_config()
    config = show_start_gui(config)
    if config is None:
        print("用户取消，程序退出")
        return

    # 3. 截取当前屏幕并保存
    screenshot(d)

    # 4. 寻找游戏中的"开始战斗"按钮
    button_pos = find_image('picture/start_game.png', SCREENSHOT_PATH)
    if button_pos:
        start_game(d, button_pos, config)
    else:
        messagebox.showerror("错误", "未找到目标按钮")


if __name__ == '__main__':
    main()
