"""业务层：游戏逻辑，包括角色选择和战斗流程"""

import os
import time

from device_utils import safe_click, click_blank, screenshot
from image_utils import find_image, wait_for_image, wait_for_image_gone, wait_for_any_image

# 难度对应的图片文件名后缀映射
DIFFICULTY_SUFFIX = {
    "默认": "",
    "普通": "_normal",
    "英雄": "_hero",
    "史诗": "_epic",
}


def start_game(device, button_pos, config):
    """
    遍历 job 目录下的图片，匹配并点击，然后点击开始战斗按钮

    Args:
        device: uiautomator2 设备对象
        button_pos: 开始战斗按钮的坐标 (x, y)
        config: 英雄配置字典 {英雄名: {区域名: 难度}}
    """
    job_dir = 'picture/job'
    files = os.listdir(job_dir)
    index = 0
    while index < len(files):
        filename = files[index]
        hero_name = os.path.splitext(filename)[0]
        hero_config = config.get(hero_name, {})
        template_path = os.path.join(job_dir, filename)
        screenshot(device)
        match_pos = find_image(template_path, 'screenshot.png')
        if match_pos:
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)
            print(f"点击了职业图片 {filename}，坐标：({x}, {y})")

            # 点击开始战斗按钮
            x, y = int(button_pos[0]), int(button_pos[1])
            safe_click(device, x, y)
            print(f"点击了开始战斗按钮，坐标：({x}, {y})")

            # 进入战斗
            if job_war(device, hero_config):
                index += 1  # 成功才继续下一个
                print("当前角色所有副本已通关，找到设置按钮并点击")
            else:
                print(f"job_war 执行失败，重试当前 template_path: {filename}")
                print("等待20s")
                time.sleep(20)
                click_blank(device)
                print("当前角色未执行完成，找到设置按钮并点击")

            match_pos = wait_for_image(device, 'picture/Settings.png', 10, 0.5, 0.6)
            if match_pos is None:
                print("未找到设置按钮")
                return False
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)

            print("找到返回角色选择并点击")
            match_pos = wait_for_image(device, 'picture/return_job_select.png')
            if match_pos is None:
                print("未找到返回角色选择按钮")
                return False
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)
        else:
            return


def job_war(device, hero_config):
    """
    战斗流程：选择区域 → 选择副本难度 → 自动战斗 → 卖装备

    Args:
        device: uiautomator2 设备对象
        hero_config: 当前英雄的区域配置 {区域名: 难度}

    Returns:
        bool: 战斗流程是否成功
    """
    print("开始游戏后等待开始界面加载")
    match_pos = wait_for_image(device, 'picture/start_war.png')

    if match_pos is None:
        print("战斗超时，未能匹配到结束图片")
        return False

    # 遍历 area 目录下的所有区域图片
    area_dir = 'picture/area'
    area_files = os.listdir(area_dir)
    area_index = 0

    while area_index < len(area_files):
        area_filename = area_files[area_index]
        area_name = os.path.splitext(area_filename)[0]
        area_path = os.path.join(area_dir, area_filename)
        difficulty = hero_config.get(area_name, "默认")

        if not _select_dungeon(device, area_path, area_filename):
            return False

        match_pos = wait_for_any_image(device, ['picture/free1.png', 'picture/free2.png'], 2, 0.5)
        if match_pos is None:
            print("未找到免费副本，切换到下一个区域")
            area_index += 1
            click_blank(device)
            continue

        print("点击一个免费区域")
        x, y = int(match_pos[0]), int(match_pos[1])
        safe_click(device, x, y)

        # 根据配置选择难度
        select_difficulty(device, difficulty)

        if not _start_dungeon_battle(device):
            return False

        # 等待自动战斗结束
        print("开始战斗副本后等待10s")
        time.sleep(10)
        print("等待自动按钮消失，等待500s")
        wait_for_image_gone(device, 'picture/Auto_battle.png', 300, 2, 0.6)
        print("自动按钮消失后再等待5s")
        time.sleep(3)

        # 卖装备
        if not _sell_items(device):
            # 卖装备失败不算战斗失败，继续循环
            pass

        print("点击空地两次")
        click_blank(device)

    return True


def select_difficulty(device, difficulty):
    """
    根据配置的难度选择对应难度按钮

    Args:
        device: uiautomator2 设备对象
        difficulty: 难度名称（默认/普通/英雄/史诗）

    Returns:
        bool: 选择成功返回 True，"默认"跳过返回 True，找不到按钮返回 False
    """
    if difficulty == "默认":
        print(f"难度为默认，跳过难度选择")
        return

    print(f"先判断当前的难度是否是期望的难度")
    # 默认图片为普通
    difficulty_img = 'picture/difficulty/Ordinary.png'
    difficulty_select = 'picture/difficulty/select_ordinary.png'
    if difficulty == "英雄":
        difficulty_img = 'picture/difficulty/Hero.png'
        difficulty_select = 'picture/difficulty/select_hero.png'
    elif difficulty == "史诗":
        difficulty_img = 'picture/difficulty/Epic.png'
        difficulty_select = 'picture/difficulty/select_epic.png'

    print(f"选择难度: {difficulty}，匹配图片: {difficulty_img}")
    match_pos = wait_for_image(device, difficulty_img, 1, 0.5)
    if match_pos is not None:
        print(f"当前难度不需要重新选择")
        return
    print(f"重新选择难度")
    print(f"先找到难度选择按钮")
    match_pos = wait_for_image(device, 'picture/difficulty/select.png', 2, 0.5,0.95)
    if match_pos is None:
        print("未找到选择按钮")
        return
    x, y = int(match_pos[0]), int(match_pos[1])
    print("点击难度选择按钮")
    safe_click(device, x, y)
    print("找到对应的难度图标")
    match_pos = wait_for_image(device, difficulty_select, 1, 0.5, 0.6)
    if match_pos is None:
        print("未找到难度按钮")
        return
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)
    print(f"点击了难度按钮 {difficulty}，坐标：({x}, {y})")
    return


def _select_dungeon(device, area_path, area_filename):
    """选择副本区域和区域图片"""
    print("找到副本选择按钮并点击")
    match_pos = wait_for_image(device, 'picture/opt.png')
    if match_pos is None:
        print("未找到副本选择按钮")
        return False
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)

    print("找到区域切换按钮并点击")
    match_pos = wait_for_image(device, 'picture/switch_area.png')
    if match_pos is None:
        print("未找到区域切换按钮")
        return False
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)

    print(f"选择指定的区域: {area_filename}")
    match_pos = wait_for_image(device, area_path)
    if match_pos is None:
        print(f"未找到区域图片: {area_filename}")
        return False
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)

    return True


def _start_dungeon_battle(device):
    """点击开始战斗按钮"""
    print("开始战斗副本")
    match_pos = wait_for_image(device, 'picture/free_start.png')
    if match_pos is None:
        print("未找到开始战斗按钮")
        return False
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)
    return True


def _sell_items(device):
    """判断是否需要卖东西，如果需要则执行售卖流程"""
    print("卖东西")
    print("判断是否需要卖东西")
    match_pos = wait_for_image(device, 'picture/is_have_empty.png', 2, 0.5)
    if match_pos is not None:
        print("不需要卖东西")
        return True

    print("需要卖东西")
    print("先查看是否有整理售卖")
    match_pos = wait_for_image(device, 'picture/Organising_sales.png', 2, 0.5)
    if match_pos is None:
        print("没有则点击装备")
        match_pos = wait_for_image(device, 'picture/gear.png')
        if match_pos is None:
            click_blank(device)
            return False
        x, y = int(match_pos[0]), int(match_pos[1])
        safe_click(device, x, y)
        print("再找到整理售卖")
        match_pos = wait_for_image(device, 'picture/Organising_sales.png', 20, 0.5, 0.9)
        if match_pos is None:
            print("未找到整理售卖按钮")
            return False

    print("点击整理售卖")
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)

    print("点击自动选中")
    match_pos = wait_for_image(device, 'picture/Automatically_selected.png')
    if match_pos is None:
        click_blank(device)
        return False
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)

    # 若存在 sale_select.png，则一直点击，直到不再存在
    _click_until_gone(device, 'picture/sale_select.png')

    print("点击确定")
    match_pos = wait_for_image(device, 'picture/sale_ok1.png')
    if match_pos is None:
        print("未找到确定按钮")
        return False
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)

    print("点击出售")
    match_pos = wait_for_image(device, 'picture/sale.png')
    if match_pos is None:
        print("未找到出售按钮")
        return False
    x, y = int(match_pos[0]), int(match_pos[1])
    safe_click(device, x, y)

    return True


def _click_until_gone(device, template_path, threshold=0.8):
    """持续点击某个图片直到它消失"""
    while True:
        screenshot(device)
        match_pos = find_image(template_path, 'screenshot.png', threshold)
        if match_pos is None:
            print(f"{template_path} 不再存在，退出循环")
            break
        x, y = int(match_pos[0]), int(match_pos[1])
        safe_click(device, x, y)
        print(f"点击了 {template_path}，坐标：({x}, {y})")
