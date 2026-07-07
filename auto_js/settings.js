/**
 * 配置层：集中管理工程全局配置
 * 从 settings.py + game.py (DIFFICULTY_SUFFIX) 迁移
 */

// --- 路径 ---
var SCRIPT_DIR = files.cwd();
// auto_js/ 与 picture/ 同级，通过 ../picture/ 引用
var PICTURE_DIR = files.join(SCRIPT_DIR, "../picture/");
var JOB_DIR = files.join(PICTURE_DIR, "job/");
var AREA_DIR = files.join(PICTURE_DIR, "area/");
var DIFFICULTY_DIR = files.join(PICTURE_DIR, "difficulty/");
var CONFIG_PATH = files.join(SCRIPT_DIR, "../hero_config.json");

// --- 时间参数（AutoX.js 使用毫秒） ---
var CLICK_DELAY = 500;        // 点击后等待时间，对应 Python 的 0.5s
var POLL_INTERVAL = 500;      // 轮询间隔，对应 Python 的 0.5s
var DEFAULT_MAX_ATTEMPTS = 20; // 默认最大尝试次数
var AUTO_BATTLE_MAX_ATTEMPTS = 300; // 自动战斗最大等待次数
var AUTO_BATTLE_INTERVAL = 2000;    // 自动战斗轮询间隔，对应 Python 的 2s

// --- GUI 配置 ---
var DIFFICULTY_OPTIONS = ["默认", "普通", "英雄", "史诗", "关闭"];

// 英雄职业英文名到中文名的映射（键名与 picture/job 目录下的图片文件名一致）
var HERO_NAME_MAP = {
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
};

// 难度对应的图片文件名后缀映射（从 game.py 迁移）
var DIFFICULTY_SUFFIX = {
    "默认": "",
    "普通": "_normal",
    "英雄": "_hero",
    "史诗": "_epic",
};

module.exports = {
    SCRIPT_DIR: SCRIPT_DIR,
    PICTURE_DIR: PICTURE_DIR,
    JOB_DIR: JOB_DIR,
    AREA_DIR: AREA_DIR,
    DIFFICULTY_DIR: DIFFICULTY_DIR,
    CONFIG_PATH: CONFIG_PATH,
    CLICK_DELAY: CLICK_DELAY,
    POLL_INTERVAL: POLL_INTERVAL,
    DEFAULT_MAX_ATTEMPTS: DEFAULT_MAX_ATTEMPTS,
    AUTO_BATTLE_MAX_ATTEMPTS: AUTO_BATTLE_MAX_ATTEMPTS,
    AUTO_BATTLE_INTERVAL: AUTO_BATTLE_INTERVAL,
    DIFFICULTY_OPTIONS: DIFFICULTY_OPTIONS,
    HERO_NAME_MAP: HERO_NAME_MAP,
    DIFFICULTY_SUFFIX: DIFFICULTY_SUFFIX,
};
