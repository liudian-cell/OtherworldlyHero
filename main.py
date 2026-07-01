"""入口层：设备连接与启动游戏"""

from device_utils import connect_device, screenshot
from image_utils import find_image
from game import start_game


def main():
    # 1. 连接设备（假设设备已通过adb连接）
    # 如果是模拟器，地址可能是 '127.0.0.1:7555' (MuMu模拟器默认端口)
    d = connect_device("127.0.0.1:7555")

    # 2. 截取当前屏幕并保存
    screenshot(d)

    # 3. 寻找游戏中的"开始战斗"按钮
    button_pos = find_image('picture/start_game.png', 'screenshot.png')
    if button_pos:
        start_game(d, button_pos)
    else:
        print("未找到目标按钮")


if __name__ == '__main__':
    main()
