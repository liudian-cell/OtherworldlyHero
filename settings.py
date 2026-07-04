"""配置层：集中管理工程全局配置"""

# --- 设备 ---
# MuMu 模拟器默认地址
DEVICE_ADDR = "127.0.0.1:16384"

# --- 文件路径 ---
CONFIG_PATH = "hero_config.json"
SCREENSHOT_PATH = "screenshot.png"
JOB_DIR = "picture/job"
AREA_DIR = "picture/area"

# --- GUI 配置 ---
DIFFICULTY_OPTIONS = ["默认", "普通", "英雄", "史诗", "关闭"]

# 英雄职业英文名到中文名的映射（键名与 picture/job 目录下的图片文件名一致）
HERO_NAME_MAP = {
    "DeathKnight": "死亡骑士",
    "Druid": "德鲁伊",
    "Hunter": "猎人",
    "Mage": "法师",
    "MagicHunter": "魔法猎人",
    "Monk": "武僧",
    "Paladin": "圣骑士",
    "Shaman": "萨满",
    "Thief": "盗贼",
    "Warlock": "术士",
    "Warrior": "战士",
    "priest": "牧师",
}
