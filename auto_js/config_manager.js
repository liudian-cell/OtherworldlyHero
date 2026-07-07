/**
 * 配置管理模块：负责 hero_config.json 的读写与默认配置生成
 * 从 main.py 的 load_config / generate_default_config / save_config 迁移
 */

var settings = require("./settings.js");

/**
 * 加载英雄配置，文件不存在则从目录自动生成。
 * 配置结构: { 英雄名: { 区域名: 难度 } }
 *
 * @returns {Object} 配置对象
 */
function loadConfig() {
    if (files.exists(settings.CONFIG_PATH)) {
        var content = files.read(settings.CONFIG_PATH);
        return JSON.parse(content);
    }
    return generateDefaultConfig();
}

/**
 * 从 job 和 area 目录扫描，生成默认配置
 * 所有区域默认难度为"默认"
 *
 * @returns {Object} 默认配置对象
 */
function generateDefaultConfig() {
    // 扫描 job 目录
    var jobFiles = files.listDir(settings.JOB_DIR);
    var heroes = [];
    for (var i = 0; i < jobFiles.length; i++) {
        if (/\.png$/i.test(jobFiles[i])) {
            heroes.push(jobFiles[i].replace(/\.png$/i, ""));
        }
    }
    heroes.sort();

    // 扫描 area 目录，按数字前缀排序
    var areaFiles = files.listDir(settings.AREA_DIR);
    var areas = [];
    for (var j = 0; j < areaFiles.length; j++) {
        if (/\.png$/i.test(areaFiles[j])) {
            areas.push(areaFiles[j].replace(/\.png$/i, ""));
        }
    }
    areas.sort(function (a, b) {
        return parseInt(a.split("-")[0]) - parseInt(b.split("-")[0]);
    });

    // 构建默认配置
    var config = {};
    for (var h = 0; h < heroes.length; h++) {
        config[heroes[h]] = {};
        for (var a = 0; a < areas.length; a++) {
            config[heroes[h]][areas[a]] = "默认";
        }
    }

    saveConfig(config);
    return config;
}

/**
 * 保存英雄配置到 JSON 文件
 *
 * @param {Object} config - 配置对象
 */
function saveConfig(config) {
    files.write(settings.CONFIG_PATH, JSON.stringify(config, null, 4));
}

module.exports = {
    loadConfig: loadConfig,
    generateDefaultConfig: generateDefaultConfig,
    saveConfig: saveConfig,
};
