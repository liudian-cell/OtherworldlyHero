"""视觉工具层：负责图像匹配与等待"""

import cv2
import numpy as np
import time

from device_utils import screenshot


def find_image(template_path, curscreenshot_path, threshold=0.8):
    """
    用 OpenCV 模板匹配寻找图片位置

    Args:
        template_path: 模板图片路径
        curscreenshot_path: 当前截图路径
        threshold: 匹配阈值，默认0.8

    Returns:
        tuple: 匹配成功返回中心点坐标 (x, y)，失败返回 None
    """
    screen = cv2.imread(curscreenshot_path, 0)
    template = cv2.imread(template_path, 0)
    h, w = template.shape  # OpenCV shape: (高度, 宽度)
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    for x, y in zip(loc[1], loc[0]):  # loc[1]=x数组, loc[0]=y数组
        return (int(x + w // 2), int(y + h // 2))
    return None


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
        screenshot(device)
        match_pos = find_image(template_path, 'screenshot.png', threshold)
        if match_pos:
            print(f"第 {attempt + 1} 次尝试匹配成功，坐标：({match_pos[0]}, {match_pos[1]})")
            return match_pos
        print(f"第 {attempt + 1}/{max_attempts} 次尝试未匹配到图片，等待 {interval} 秒后重试...")
        time.sleep(interval)

    print(f"已尝试 {max_attempts} 次，仍未匹配到图片")
    return None


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
        screenshot(device)
        match_pos = find_image(template_path, 'screenshot.png', threshold)
        if match_pos is None:
            print(f"第 {attempt + 1} 次尝试，图片已消失")
            return
        print(f"第 {attempt + 1}/{max_attempts} 次尝试，图片仍存在，等待 {interval} 秒后重试...")
        time.sleep(interval)

    print(f"已尝试 {max_attempts} 次，图片仍未消失")


def wait_for_any_image(device, template_paths, max_attempts=20, interval=0.5, threshold=0.8):
    """
    等待直到匹配到多个图片中的任意一个

    Args:
        device: uiautomator2 设备对象
        template_paths: 要匹配的图片路径列表
        max_attempts: 最大尝试次数，默认20次
        interval: 每次尝试之间的等待时间（秒），默认0.5秒
        threshold: 图片匹配阈值，默认0.8

    Returns:
        tuple: 匹配成功返回坐标 (x, y) 和匹配的图片路径，失败返回 None
               例如：(x, y, template_path) 或 None
    """
    for attempt in range(max_attempts):
        screenshot(device)
        for i, template_path in enumerate(template_paths):
            match_pos = find_image(template_path, 'screenshot.png', threshold)
            if match_pos:
                print(f"第 {attempt + 1} 次尝试匹配图片{i + 1}成功，坐标：({match_pos[0]}, {match_pos[1]})")
                return (match_pos[0], match_pos[1], template_path)
        print(f"第 {attempt + 1}/{max_attempts} 次尝试未匹配到任意图片，等待 {interval} 秒后重试...")
        time.sleep(interval)

    print(f"已尝试 {max_attempts} 次，仍未匹配到任意图片，返回失败")
    return None
