import uiautomator2 as u2
import cv2
import numpy as np
import time

# 封装click接口，点击后等待0.5秒
def safe_click(device, x, y, delay=0.5):
    """
    封装的点击接口，点击后自动等待

    Args:
        device: uiautomator2 设备对象
        x: 点击的x坐标
        y: 点击的y坐标
        delay: 点击后等待的时间（秒），默认0.5秒
    """
    device.click(x, y)
    time.sleep(delay)

# 用OpenCV寻找图片位置的函数
def find_image(template_path, curscreenshot_path, threshold=0.8):
    # 读取截图和模板图片
    screen = cv2.imread(curscreenshot_path, 0)
    template = cv2.imread(template_path, 0)
    h, w = template.shape  # OpenCV shape: (高度, 宽度)
    # 进行模板匹配
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    # 如果找到，返回中心点坐标
    for x, y in zip(loc[1], loc[0]):  # loc[1]=x数组, loc[0]=y数组
        return (int(x + w // 2), int(y + h // 2))
    return None

# 4. 开始战斗函数
def start_game(device, button_pos):
    """遍历job目录下的图片，匹配并点击，然后点击开始战斗按钮"""
    import os

    job_dir = 'job'
    files = os.listdir(job_dir)
    index = 7
    while index < len(files):
        filename = files[index]
        template_path = os.path.join(job_dir, filename)
        device.screenshot("screenshot.png")
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
            if job_war(device):
                index += 1  # 成功才继续下一个
                print("当前角色所有副本已通关，找到设置按钮并点击")
            else:
                print(f"job_war 执行失败，重试当前 template_path: {filename}")
                print("等待20s")
                time.sleep(20)
                print("点击空地两次")
                x, y = int(10), int(10)
                safe_click(device, x, y)
                safe_click(device, x, y)
                print("当前角色未执行完成，找到设置按钮并点击")

            match_pos = wait_for_image(device, 'Settings.png',10,0.5,0.6)
            if match_pos is None:
                print("未找到设置按钮")
                return False
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)

            print("找到返回角色选择并点击")
            match_pos = wait_for_image(device, 'return_job_select.png')
            if match_pos is None:
                print("未找到返回角色选择按钮")
                return False
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)
        else:
            return

# 等待匹配图片的通用函数
def wait_for_image(device, template_path, max_attempts=20, interval=0.5, threshold=0.8):
    """
    等待直到匹配到指定图片

    Args:
        device: uiautomator2 设备对象
        template_path: 要匹配的图片路径
        max_attempts: 最大尝试次数，默认20次
        interval: 每次尝试之间的等待时间（秒），默认0.5秒
        threshold: 图片匹配阈值，默认0.8

    Returns:
        tuple: 匹配成功返回坐标 (x, y)，失败返回 None
    """
    for attempt in range(max_attempts):
        # 截取当前屏幕
        device.screenshot("screenshot.png")

        # 尝试匹配图片
        match_pos = find_image(template_path, 'screenshot.png', threshold)

        if match_pos:
            print(f"第 {attempt + 1} 次尝试匹配成功，坐标：({match_pos[0]}, {match_pos[1]})")
            return match_pos

        # 未匹配到，等待后重试
        print(f"第 {attempt + 1}/{max_attempts} 次尝试未匹配到图片，等待 {interval} 秒后重试...")
        time.sleep(interval)

    print(f"已尝试 {max_attempts} 次，仍未匹配到图片，返回失败")
    return None

# 等待图片消失的函数
def wait_for_image_gone(device, template_path, max_attempts=20, interval=0.5, threshold=0.8):
    """
    等待直到指定的图片不再出现在屏幕上

    Args:
        device: uiautomator2 设备对象
        template_path: 要等待消失的图片路径
        max_attempts: 最大尝试次数，默认20次
        interval: 每次尝试之间的等待时间（秒），默认0.5秒
        threshold: 图片匹配阈值，默认0.8
    """
    for attempt in range(max_attempts):
        # 截取当前屏幕
        device.screenshot("screenshot.png")

        # 尝试匹配图片
        match_pos = find_image(template_path, 'screenshot.png', threshold)

        if match_pos is None:
            # 图片已消失
            print(f"第 {attempt + 1} 次尝试，图片已消失")
            return

        # 图片仍然存在，等待后重试
        print(f"第 {attempt + 1}/{max_attempts} 次尝试，图片仍存在，等待 {interval} 秒后重试...")
        time.sleep(interval)

    print(f"已尝试 {max_attempts} 次，图片仍未消失")

# 等待匹配多个图片之一的通用函数
def wait_for_any_image(device, template_path1, template_path2, max_attempts=20, interval=0.5, threshold=0.8):
    """
    等待直到匹配到两个图片中的任意一个

    Args:
        device: uiautomator2 设备对象
        template_path1: 第一个要匹配的图片路径
        template_path2: 第二个要匹配的图片路径
        max_attempts: 最大尝试次数，默认20次
        interval: 每次尝试之间的等待时间（秒），默认0.5秒
        threshold: 图片匹配阈值，默认0.8

    Returns:
        tuple: 匹配成功返回坐标 (x, y) 和匹配的图片路径，失败返回 None
               例如：(x, y, template_path1) 或 None
    """
    for attempt in range(max_attempts):
        # 截取当前屏幕
        device.screenshot("screenshot.png")

        # 尝试匹配第一个图片
        match_pos1 = find_image(template_path1, 'screenshot.png', threshold)
        if match_pos1:
            print(f"第 {attempt + 1} 次尝试匹配图片1成功，坐标：({match_pos1[0]}, {match_pos1[1]})")
            return (match_pos1[0], match_pos1[1], template_path1)

        # 尝试匹配第二个图片
        match_pos2 = find_image(template_path2, 'screenshot.png', threshold)
        if match_pos2:
            print(f"第 {attempt + 1} 次尝试匹配图片2成功，坐标：({match_pos2[0]}, {match_pos2[1]})")
            return (match_pos2[0], match_pos2[1], template_path2)

        # 两个都未匹配到，等待后重试
        print(f"第 {attempt + 1}/{max_attempts} 次尝试未匹配到任意图片，等待 {interval} 秒后重试...")
        time.sleep(interval)

    print(f"已尝试 {max_attempts} 次，仍未匹配到任意图片，返回失败")
    return None

# 5. 战斗函数
def job_war(device):

    print("开始游戏后等待开始界面加载")
    match_pos = wait_for_image(device, 'start_war.png')

    if match_pos is None:
        print("战斗超时，未能匹配到结束图片")
        return False

    # 遍历area目录下的所有区域图片
    import os
    area_dir = 'area'
    area_files = os.listdir(area_dir)
    area_index = 0

    while area_index < len(area_files):
        area_filename = area_files[area_index]
        area_path = os.path.join(area_dir, area_filename)

        print("找到副本选择按钮并点击")
        match_pos = wait_for_image(device, 'opt.png')
        if match_pos is None:
            print("未找到副本选择按钮")
            return False
        x, y = int(match_pos[0]), int(match_pos[1])
        safe_click(device, x, y)

        print("找到区域切换按钮并点击")
        match_pos = wait_for_image(device, 'switch_area.png')
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

        print("找到一个免费的副本")
        match_pos = wait_for_any_image(device, 'free1.png', 'free1.png',2,0.5)
        if match_pos is None:
            print("未找到免费副本，切换到下一个区域")
            area_index += 1  # 只有未找到免费副本时，才更新到下一个区域
            print("点击空地两次")
            x, y = int(10), int(10)
            safe_click(device, x, y)
            safe_click(device, x, y)
            continue

        x, y = int(match_pos[0]), int(match_pos[1])
        safe_click(device, x, y)

        print("开始战斗副本")
        match_pos = wait_for_image(device, 'free_start.png')
        if match_pos is None:
            print("未找到开始战斗按钮")
            return False
        x, y = int(match_pos[0]), int(match_pos[1])
        safe_click(device, x, y)

        print("开始战斗副本后等待10s")
        time.sleep(10)

        print("等待自动按钮消失，等待500s")
        wait_for_image_gone(device, 'Auto_battle.png', 300, 2,0.6)

        print("自动按钮消失后再等待5s")
        time.sleep(3)

        print("卖东西")
        print("判断是否需要卖东西")
        match_pos = wait_for_image(device, 'is_have_empty.png',2,0.5)
        if match_pos is None:
            print("需要卖东西")
            print("先查看是否有整理售卖")
            match_pos = wait_for_image(device, 'Organising_sales.png', 2, 0.5)
            if match_pos is None:
                print("没有则点击装备")
                match_pos = wait_for_image(device, 'gear.png')
                if match_pos is None:
                    x, y = int(10), int(10)
                    safe_click(device, x, y)
                    safe_click(device, x, y)
                    continue
                x, y = int(match_pos[0]), int(match_pos[1])
                safe_click(device, x, y)
                print("再找到整理售卖")
                match_pos = wait_for_image(device, 'Organising_sales.png', 20, 0.5, 0.9)
                if match_pos is None:
                    print("未找到整理售卖按钮")
                    return False

            print("点击整理售卖")
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)

            print("点击自动选中")
            match_pos = wait_for_image(device, 'Automatically_selected.png')
            if match_pos is None:
                x, y = int(10), int(10)
                safe_click(device, x, y)
                safe_click(device, x, y)
                continue
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)

            # 若存在sale_select.png，则一直点击，直到不再存在sale_select.png
            while True:
                device.screenshot("screenshot.png")
                match_pos = find_image('sale_select.png', 'screenshot.png')
                if match_pos is None:
                    print("sale_select.png 不再存在，退出循环")
                    break
                x, y = int(match_pos[0]), int(match_pos[1])
                safe_click(device, x, y)
                print(f"点击了 sale_select.png，坐标：({x}, {y})")

            print("点击确定")
            match_pos = wait_for_image(device, 'sale_ok1.png')
            if match_pos is None:
                print("未找到确定按钮")
                return False
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)

            print("点击出售")
            match_pos = wait_for_image(device, 'sale.png')
            if match_pos is None:
                print("未找到出售按钮")
                return False
            x, y = int(match_pos[0]), int(match_pos[1])
            safe_click(device, x, y)
        else:
            print("不需要卖东西")


        print("点击空地两次")
        x, y = int(10), int(10)
        safe_click(device, x, y)
        safe_click(device, x, y)

    return True

if __name__ == '__main__':
    # 1. 连接设备（假设设备已通过adb连接）
    # 如果是模拟器，地址可能是 '127.0.0.1:7555' (MuMu模拟器默认端口)[reference:35]
    d = u2.connect("127.0.0.1:7555")  # 连接默认设备
    if d.device_info:  # 属性访问，不会抛异常
        print("连接成功")
    else:
        print("连接失败")
        exit(1)
    # 2. 截取当前屏幕并保存
    d.screenshot("screenshot.png")

    # 4. 寻找游戏中的“开始战斗”
    button_pos = find_image('start_game.png', 'screenshot.png')  # 你需要提前截取这个按钮的图片
    if button_pos:
        start_game(d, button_pos)
    else:
        print("未找到目标按钮")