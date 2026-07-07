/**
 * 业务层：游戏逻辑，包括角色选择和战斗流程
 * 从 game.py 1:1 翻译，去掉 device 参数（AutoX.js 全局函数）
 */

var settings = require("./settings.js");
var deviceUtils = require("./device_utils.js");
var imageUtils = require("./image_utils.js");

/**
 * 遍历 job 目录下的图片，匹配并点击，然后点击开始战斗按钮
 *
 * @param {Object} buttonPos - 开始战斗按钮的坐标 {x, y}
 * @param {Object} config - 英雄配置字典 {英雄名: {区域名: 难度}}
 */
function startGame(buttonPos, config) {
    var jobDir = settings.JOB_DIR;
    var jobFiles = files.listDir(jobDir);
    var index = 0;

    while (index < jobFiles.length) {
        var filename = jobFiles[index];
        var heroName = filename.replace(/\.png$/i, "");
        var heroConfig = config[heroName] || {};
        var templatePath = files.join(jobDir, filename);

        var matchPos = imageUtils.findImage(templatePath);
        if (matchPos) {
            deviceUtils.safeClick(matchPos.x, matchPos.y);
            log("点击了职业图片 " + filename + "，坐标：(" + matchPos.x + ", " + matchPos.y + ")");

            // 点击开始战斗按钮
            deviceUtils.safeClick(buttonPos.x, buttonPos.y);
            log("点击了开始战斗按钮，坐标：(" + buttonPos.x + ", " + buttonPos.y + ")");

            // 进入战斗
            if (jobWar(heroConfig)) {
                index += 1; // 成功才继续下一个
                log("当前角色所有副本已通关，找到设置按钮并点击");
            } else {
                log("jobWar 执行失败，重试当前 template_path: " + filename);
                log("等待20s");
                sleep(20000);
                deviceUtils.clickBlank();
                log("当前角色未执行完成，找到设置按钮并点击");
            }

            matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "Settings.png", 10, 500, 0.6);
            if (matchPos === null) {
                log("未找到设置按钮");
                return false;
            }
            deviceUtils.safeClick(matchPos.x, matchPos.y);

            log("找到返回角色选择并点击");
            matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "return_job_select.png");
            if (matchPos === null) {
                log("未找到返回角色选择按钮");
                return false;
            }
            deviceUtils.safeClick(matchPos.x, matchPos.y);

            // 切换英雄时清理模板缓存
            imageUtils.clearTemplateCache();
        } else {
            return;
        }
    }
}

/**
 * 战斗流程：选择区域 → 选择副本难度 → 自动战斗 → 卖装备
 *
 * @param {Object} heroConfig - 当前英雄的区域配置 {区域名: 难度}
 * @returns {boolean} 战斗流程是否成功
 */
function jobWar(heroConfig) {
    log("开始游戏后等待开始界面加载");
    var matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "start_war.png");

    if (matchPos === null) {
        log("战斗超时，未能匹配到结束图片");
        return false;
    }

    // 遍历 area 目录下的所有区域图片
    var areaDir = settings.AREA_DIR;
    var areaFiles = files.listDir(areaDir);
    // 按数字前缀排序
    areaFiles.sort(function (a, b) {
        return parseInt(a.replace(/\.png$/i, "").split("-")[0])
             - parseInt(b.replace(/\.png$/i, "").split("-")[0]);
    });

    var areaIndex = 0;

    while (areaIndex < areaFiles.length) {
        var areaFilename = areaFiles[areaIndex];
        var areaName = areaFilename.replace(/\.png$/i, "");
        var areaPath = files.join(areaDir, areaFilename);
        var difficulty = heroConfig[areaName] || "默认";

        if (difficulty === "关闭") {
            log("区域 " + areaName + " 已设置为关闭，跳过");
            areaIndex += 1;
            continue;
        }

        if (!_selectDungeon(areaPath, areaFilename)) {
            return false;
        }

        matchPos = imageUtils.waitForAnyImage(
            [settings.PICTURE_DIR + "free1.png", settings.PICTURE_DIR + "free2.png"],
            2, 500
        );
        if (matchPos === null) {
            log("未找到免费副本，切换到下一个区域");
            areaIndex += 1;
            deviceUtils.clickBlank();
            continue;
        }

        log("点击一个免费区域");
        deviceUtils.safeClick(matchPos.x, matchPos.y);

        // 根据配置选择难度
        selectDifficulty(difficulty);

        if (!_startDungeonBattle()) {
            return false;
        }

        // 等待自动战斗结束
        log("开始战斗副本后开始售卖装备");
        // 卖装备
        if (!_sellItems()) {
            // 卖装备失败不算战斗失败，继续循环
        }
        log("点击空地两次");
        deviceUtils.clickBlank();
        log("装备买完了");
        log("等待自动按钮消失，等待500s");
        imageUtils.waitForImageGone(
            settings.PICTURE_DIR + "Auto_battle.png",
            settings.AUTO_BATTLE_MAX_ATTEMPTS,
            settings.AUTO_BATTLE_INTERVAL,
            0.6
        );
        log("自动按钮消失后再等待3s");
        sleep(3000);

        areaIndex += 1;
    }

    return true;
}

/**
 * 根据配置的难度选择对应难度按钮
 *
 * @param {string} difficulty - 难度名称（默认/普通/英雄/史诗）
 */
function selectDifficulty(difficulty) {
    if (difficulty === "默认") {
        log("难度为默认，跳过难度选择");
        return;
    }

    log("先判断当前的难度是否是期望的难度");
    // 默认图片为普通
    var difficultyImg = settings.DIFFICULTY_DIR + "Ordinary.png";
    var difficultySelect = settings.DIFFICULTY_DIR + "select_ordinary.png";
    if (difficulty === "英雄") {
        difficultyImg = settings.DIFFICULTY_DIR + "Hero.png";
        difficultySelect = settings.DIFFICULTY_DIR + "select_hero.png";
    } else if (difficulty === "史诗") {
        difficultyImg = settings.DIFFICULTY_DIR + "Epic.png";
        difficultySelect = settings.DIFFICULTY_DIR + "select_epic.png";
    }

    log("选择难度: " + difficulty + "，匹配图片: " + difficultyImg);
    var matchPos = imageUtils.waitForImage(difficultyImg, 1, 500);
    if (matchPos !== null) {
        log("当前难度不需要重新选择");
        return;
    }

    log("重新选择难度");
    log("先找到难度选择按钮");
    matchPos = imageUtils.waitForImage(settings.DIFFICULTY_DIR + "select.png", 2, 500, 0.95);
    if (matchPos === null) {
        log("未找到选择按钮");
        return;
    }
    log("点击难度选择按钮");
    deviceUtils.safeClick(matchPos.x, matchPos.y);

    log("找到对应的难度图标");
    matchPos = imageUtils.waitForImage(difficultySelect, 1, 500, 0.6);
    if (matchPos === null) {
        log("未找到难度按钮");
        return;
    }
    deviceUtils.safeClick(matchPos.x, matchPos.y);
    log("点击了难度按钮 " + difficulty + "，坐标：(" + matchPos.x + ", " + matchPos.y + ")");
}

/**
 * 选择副本区域和区域图片
 *
 * @param {string} areaPath - 区域图片路径
 * @param {string} areaFilename - 区域图片文件名
 * @returns {boolean} 选择是否成功
 */
function _selectDungeon(areaPath, areaFilename) {
    log("找到副本选择按钮并点击");
    var matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "opt.png");
    if (matchPos === null) {
        log("未找到副本选择按钮");
        return false;
    }
    deviceUtils.safeClick(matchPos.x, matchPos.y);

    log("找到区域切换按钮并点击");
    matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "switch_area.png");
    if (matchPos === null) {
        log("未找到区域切换按钮");
        return false;
    }
    deviceUtils.safeClick(matchPos.x, matchPos.y);

    log("选择指定的区域: " + areaFilename);
    matchPos = imageUtils.waitForImage(areaPath);
    if (matchPos === null) {
        log("未找到区域图片: " + areaFilename);
        return false;
    }
    deviceUtils.safeClick(matchPos.x, matchPos.y);

    return true;
}

/**
 * 点击开始战斗按钮
 *
 * @returns {boolean} 是否成功
 */
function _startDungeonBattle() {
    log("开始战斗副本");
    var matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "free_start.png");
    if (matchPos === null) {
        log("未找到开始战斗按钮");
        return false;
    }
    deviceUtils.safeClick(matchPos.x, matchPos.y);
    return true;
}

/**
 * 判断是否需要卖东西，如果需要则执行售卖流程
 *
 * @returns {boolean} 售卖是否成功
 */
function _sellItems() {
    log("卖东西");
    log("判断是否需要卖东西");
    var matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "is_have_empty.png", 2, 500);
    if (matchPos !== null) {
        log("不需要卖东西");
        return true;
    }

    log("需要卖东西");
    log("先查看是否有整理售卖");
    matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "Organising_sales.png", 2, 500);
    if (matchPos === null) {
        log("没有则点击装备");
        matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "gear.png");
        if (matchPos === null) {
            deviceUtils.clickBlank();
            return false;
        }
        deviceUtils.safeClick(matchPos.x, matchPos.y);

        log("再找到整理售卖");
        matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "Organising_sales.png", 20, 500, 0.9);
        if (matchPos === null) {
            log("未找到整理售卖按钮");
            return false;
        }
    }

    log("点击整理售卖");
    deviceUtils.safeClick(matchPos.x, matchPos.y);

    log("点击自动选中");
    matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "Automatically_selected.png");
    if (matchPos === null) {
        deviceUtils.clickBlank();
        return false;
    }
    deviceUtils.safeClick(matchPos.x, matchPos.y);

    // 若存在 sale_select.png，则一直点击，直到不再存在
    _clickUntilGone(settings.PICTURE_DIR + "sale_select.png");

    log("点击确定");
    matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "sale_ok1.png");
    if (matchPos === null) {
        log("未找到确定按钮");
        return false;
    }
    deviceUtils.safeClick(matchPos.x, matchPos.y);

    log("点击出售");
    matchPos = imageUtils.waitForImage(settings.PICTURE_DIR + "sale.png");
    if (matchPos === null) {
        log("未找到出售按钮");
        return false;
    }
    deviceUtils.safeClick(matchPos.x, matchPos.y);

    return true;
}

/**
 * 持续点击某个图片直到它消失
 *
 * @param {string} templatePath - 模板图片路径
 * @param {number} [threshold=0.8] - 匹配阈值
 */
function _clickUntilGone(templatePath, threshold) {
    threshold = threshold || 0.8;
    while (true) {
        var matchPos = imageUtils.findImage(templatePath, threshold);
        if (matchPos === null) {
            log(templatePath + " 不再存在，退出循环");
            break;
        }
        deviceUtils.safeClick(matchPos.x, matchPos.y);
        log("点击了 " + templatePath + "，坐标：(" + matchPos.x + ", " + matchPos.y + ")");
    }
}

module.exports = {
    startGame: startGame,
    jobWar: jobWar,
    selectDifficulty: selectDifficulty,
};
