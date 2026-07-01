"""设备工具层：负责设备连接与基础交互"""

import uiautomator2 as u2
import time


def connect_device(address="127.0.0.1:7555"):
    """
    连接设备

    Args:
        address: 设备地址，默认 MuMu 模拟器 '127.0.0.1:7555'

    Returns:
        uiautomator2 设备对象，连接失败则退出程序
    """
    d = u2.connect(address)
    if d.device_info:
        print("连接成功")
        return d
    else:
        print("连接失败")
        exit(1)


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


def click_blank(device, x=10, y=10):
    """点击空白区域（默认坐标 10,10），点击两次以关闭弹窗"""
    safe_click(device, x, y)
    safe_click(device, x, y)


def screenshot(device, path="screenshot.png"):
    """截取当前屏幕并保存到指定路径"""
    device.screenshot(path)
