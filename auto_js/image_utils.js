/**
 * 视觉工具层：负责图像匹配与等待
 * 从 image_utils.py 迁移，使用 AutoX.js 的 images API
 * 核心变化：截图不再存盘，直接内存操作；增加模板缓存避免反复读盘
 */

var settings = require("./settings.js");

// 模板图片缓存，避免反复读盘
var _templateCache = {};

/**
 * 加载模板图片（带缓存）
 *
 * @param {string} path - 模板图片路径
 * @returns {Image} AutoX.js Image 对象
 */
function _loadTemplate(path) {
    if (!_templateCache[path]) {
        _templateCache[path] = images.read(path);
    }
    return _templateCache[path];
}

/**
 * 清理模板缓存，释放内存（英雄切换时调用）
 */
function clearTemplateCache() {
    for (var key in _templateCache) {
        if (_templateCache.hasOwnProperty(key)) {
            _templateCache[key].recycle();
        }
    }
    _templateCache = {};
}

/**
 * 用模板匹配寻找图片位置（单次匹配）
 *
 * @param {string} templatePath - 模板图片路径
 * @param {number} [threshold=0.8] - 匹配阈值
 * @returns {Object|null} 匹配成功返回中心点坐标 {x, y}，失败返回 null
 */
function findImage(templatePath, threshold) {
    threshold = threshold || 0.8;
    var screenImg = captureScreen();
    var tmplImg = _loadTemplate(templatePath);
    var result = images.matchTemplate(screenImg, tmplImg, { threshold: threshold });
    screenImg.recycle(); // 截图用完立即释放

    if (result.matches.length > 0) {
        var m = result.matches[0];
        // 返回中心点坐标，与 Python 的 x + w//2, y + h//2 一致
        return {
            x: Math.floor(m.x + tmplImg.getWidth() / 2),
            y: Math.floor(m.y + tmplImg.getHeight() / 2),
        };
    }
    return null;
}

/**
 * 等待直到匹配到指定图片
 *
 * @param {string} templatePath - 要匹配的图片路径
 * @param {number} [maxAttempts=20] - 最大尝试次数
 * @param {number} [interval=500] - 每次尝试之间的等待时间（毫秒）
 * @param {number} [threshold=0.8] - 匹配阈值
 * @returns {Object|null} 匹配成功返回 {x, y}，失败返回 null
 */
function waitForImage(templatePath, maxAttempts, interval, threshold) {
    maxAttempts = maxAttempts || settings.DEFAULT_MAX_ATTEMPTS;
    interval = interval || settings.POLL_INTERVAL;
    threshold = threshold || 0.8;

    for (var attempt = 0; attempt < maxAttempts; attempt++) {
        var pos = findImage(templatePath, threshold);
        if (pos) {
            log("第 " + (attempt + 1) + " 次尝试匹配成功，坐标：(" + pos.x + ", " + pos.y + ")");
            return pos;
        }
        log("第 " + (attempt + 1) + "/" + maxAttempts + " 次尝试未匹配到图片，等待 " + interval + "ms 后重试...");
        sleep(interval);
    }

    log("已尝试 " + maxAttempts + " 次，仍未匹配到图片");
    return null;
}

/**
 * 等待直到指定的图片不再出现在屏幕上
 *
 * @param {string} templatePath - 要等待消失的图片路径
 * @param {number} [maxAttempts=20] - 最大尝试次数
 * @param {number} [interval=500] - 每次尝试之间的等待时间（毫秒）
 * @param {number} [threshold=0.8] - 匹配阈值
 */
function waitForImageGone(templatePath, maxAttempts, interval, threshold) {
    maxAttempts = maxAttempts || settings.DEFAULT_MAX_ATTEMPTS;
    interval = interval || settings.POLL_INTERVAL;
    threshold = threshold || 0.8;

    for (var attempt = 0; attempt < maxAttempts; attempt++) {
        var pos = findImage(templatePath, threshold);
        if (pos === null) {
            log("第 " + (attempt + 1) + " 次尝试，图片已消失");
            return;
        }
        log("第 " + (attempt + 1) + "/" + maxAttempts + " 次尝试，图片仍存在，等待 " + interval + "ms 后重试...");
        sleep(interval);
    }

    log("已尝试 " + maxAttempts + " 次，图片仍未消失");
}

/**
 * 等待直到匹配到多个图片中的任意一个
 *
 * @param {string[]} templatePaths - 要匹配的图片路径列表
 * @param {number} [maxAttempts=20] - 最大尝试次数
 * @param {number} [interval=500] - 每次尝试之间的等待时间（毫秒）
 * @param {number} [threshold=0.8] - 匹配阈值
 * @returns {Object|null} 匹配成功返回 {x, y, templatePath}，失败返回 null
 */
function waitForAnyImage(templatePaths, maxAttempts, interval, threshold) {
    maxAttempts = maxAttempts || settings.DEFAULT_MAX_ATTEMPTS;
    interval = interval || settings.POLL_INTERVAL;
    threshold = threshold || 0.8;

    for (var attempt = 0; attempt < maxAttempts; attempt++) {
        for (var i = 0; i < templatePaths.length; i++) {
            var pos = findImage(templatePaths[i], threshold);
            if (pos) {
                log("第 " + (attempt + 1) + " 次尝试匹配图片" + (i + 1) + "成功，坐标：(" + pos.x + ", " + pos.y + ")");
                return {
                    x: pos.x,
                    y: pos.y,
                    templatePath: templatePaths[i],
                };
            }
        }
        log("第 " + (attempt + 1) + "/" + maxAttempts + " 次尝试未匹配到任意图片，等待 " + interval + "ms 后重试...");
        sleep(interval);
    }

    log("已尝试 " + maxAttempts + " 次，仍未匹配到任意图片，返回失败");
    return null;
}

module.exports = {
    findImage: findImage,
    waitForImage: waitForImage,
    waitForImageGone: waitForImageGone,
    waitForAnyImage: waitForAnyImage,
    clearTemplateCache: clearTemplateCache,
};
