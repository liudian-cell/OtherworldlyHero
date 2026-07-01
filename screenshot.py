import uiautomator2 as u2

d = u2.connect("127.0.0.1:7555")  # 连接默认设备

d.screenshot("screenshot.png")