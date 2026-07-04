import cv2
import numpy as np

# 读取两个图片
template_path = 'picture/difficulty/select.png'
screenshot = cv2.imread('screenshot.png')
template = cv2.imread(template_path)

print(f"截图尺寸: {screenshot.shape}")
print(f"模板尺寸: {template.shape}")

# 转灰度匹配
screen_gray = cv2.imread('screenshot.png', 0)
template_gray = cv2.imread(template_path, 0)

res = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

print(f"\n匹配结果:")
print(f"最大匹配值: {max_val:.4f}")
print(f"匹配位置: {max_loc}")
print(f"当前阈值: 0.8")

if max_val >= 0.8:
    print("✅ 匹配成功！")
else:
    print(f"❌ 匹配失败，最大置信度 {max_val:.4f} < 0.8")
    print(f"建议：降低阈值到 {max_val:.2f} 或重新截取按钮图片")

# 显示最佳匹配位置
h, w = template_gray.shape
top_left = max_loc
bottom_right = (top_left[0] + w, top_left[1] + h)
cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
cv2.imwrite('debug/match_result.png', screenshot)
print(f"\n已保存匹配结果到 match_result.png（绿色框为最佳匹配位置）")
