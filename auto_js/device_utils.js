/**
 * 设备工具层：负责基础交互
 * 替代 Python 的 uiautomator2，脚本即设备，无需连接
 */

var settings = require("./settings.js");

/**
 * 封装的点击接口，点击后自动等待
 *
 * @param {number} x - 点击的x坐标
 * @param {number} y - 点击的y坐标
 * @param {number} [delay] - 点击后等待的时间（毫秒），默认500
 */
function safeClick(x, y, delay) {
    click(x, y);
    sleep(delay || settings.CLICK_DELAY);
}

/**
 * 点击空白区域（默认坐标 10,10），点击两次以关闭弹窗
 */
function clickBlank() {
    safeClick(10, 10);
    safeClick(10, 10);
}

module.exports = {
    safeClick: safeClick,
    clickBlank: clickBlank,
};
