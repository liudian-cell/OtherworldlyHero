import uiautomator2 as u2

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import DEVICE_ADDR, SCREENSHOT_PATH

d = u2.connect(DEVICE_ADDR)  # 连接默认设备

d.screenshot(SCREENSHOT_PATH)