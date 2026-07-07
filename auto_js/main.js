"ui";

/**
 * 入口层：权限请求 → 配置界面 → 启动自动化
 * 从 main.py 迁移，使用 AutoX.js 的 "ui" 模式构建配置界面
 */

var settings = require("./settings.js");
var deviceUtils = require("./device_utils.js");
var imageUtils = require("./image_utils.js");
var game = require("./game.js");
var configManager = require("./config_manager.js");

// --- 等待无障碍服务 ---
auto.waitFor();

// --- 请求截图权限 ---
if (!requestScreenCapture()) {
    toast("请求截图权限失败");
    exit();
}

// --- 加载配置 ---
var config = configManager.loadConfig();
var heroes = Object.keys(config);

// --- 构建配置界面 ---
ui.layout(
    <vertical padding="16">
        <text text="异世界勇者自动刷本工具" textSize="18sp" gravity="center" marginBottom="12"/>

        <TabHost id="tabHost" h="350">
            <HorizontalScrollView>
                <TabWidget id="tabs"/>
            </HorizontalScrollView>
            <FrameLayout id="tabContent"/>
        </TabHost>

        <horizontal gravity="center" marginTop="8">
            <text text="当前页批量设置:" textSize="12sp"/>
            <button id="batchDefault" text="默认" textSize="10sp" w="50" h="32"/>
            <button id="batchNormal" text="普通" textSize="10sp" w="50" h="32"/>
            <button id="batchHero" text="英雄" textSize="10sp" w="50" h="32"/>
            <button id="batchEpic" text="史诗" textSize="10sp" w="50" h="32"/>
            <button id="batchClose" text="关闭" textSize="10sp" w="50" h="32"/>
        </horizontal>

        <horizontal gravity="center" marginTop="12">
            <button id="btnStart" text="开始战斗" w="120" h="44"/>
            <button id="btnCancel" text="取  消" w="120" h="44"/>
        </horizontal>
    </vertical>
);

// 保存每个英雄的 Spinner 引用 {hero: {area: Spinner}}
var spinnerMap = {};

// 动态创建每个英雄的 Tab
var tabHost = ui.tabHost;
var tabContent = ui.tabContent;

for (var h = 0; h < heroes.length; h++) {
    var hero = heroes[h];
    var heroConfig = config[hero];
    var areas = Object.keys(heroConfig);

    // 创建 Tab 内容
    var scrollView = <ScrollView><vertical padding="8" id="heroContent"/></vertical></ScrollView>;
    var content = ui.inflate(scrollView, tabContent, false);
    var contentLayout = content.findViewById(org.autojs.autoxjs6.R.id.heroContent);

    // 或者用更可靠的方式：
    // 直接用 ui.inflate 创建内容
    var tabSpec = tabHost.newTabSpec(hero);
    tabSpec.setIndicator(settings.HERO_NAME_MAP[hero] || hero);

    // 构建 Tab 内容布局
    var heroSpinnerMap = {};

    // 用 XML 拼接来构建区域列表
    var layoutXml = '<ScrollView><vertical padding="8">';
    for (var a = 0; a < areas.length; a++) {
        var areaName = areas[a];
        var spinnerId = "spinner_" + hero + "_" + areaName.replace(/-/g, "_");
        layoutXml += '<horizontal marginBottom="4">';
        layoutXml += '  <text text="' + areaName + '" textSize="13sp" w="100" gravity="center_vertical"/>';
        layoutXml += '  <spinner id="' + spinnerId + '" entries="' + settings.DIFFICULTY_OPTIONS.join("|") + '" w="100"/>';
        layoutXml += '</horizontal>';
    }
    layoutXml += '</vertical></ScrollView>';

    var tabView = ui.inflate(layoutXml, tabContent, false);
    tabSpec.setContent(tabView);
    tabHost.addTab(tabSpec);

    // 记录 Spinner 引用，并设置当前值
    for (var a2 = 0; a2 < areas.length; a2++) {
        var areaName2 = areas[a2];
        var spinnerId2 = "spinner_" + hero + "_" + areaName2.replace(/-/g, "_");
        var spinner = ui.findViewById(spinnerId2);
        heroSpinnerMap[areaName2] = spinner;

        // 设置 Spinner 当前选中值
        var currentDifficulty = heroConfig[areaName2];
        var idx = settings.DIFFICULTY_OPTIONS.indexOf(currentDifficulty);
        if (idx >= 0 && spinner) {
            spinner.setSelection(idx);
        }
    }

    spinnerMap[hero] = heroSpinnerMap;
}

// --- 批量设置按钮 ---
function applyBatch(difficulty) {
    var currentTab = tabHost.getCurrentTab();
    var hero = heroes[currentTab];
    var areaSpinners = spinnerMap[hero];
    var diffIdx = settings.DIFFICULTY_OPTIONS.indexOf(difficulty);
    if (diffIdx < 0) return;
    for (var area in areaSpinners) {
        if (areaSpinners.hasOwnProperty(area)) {
            areaSpinners[area].setSelection(diffIdx);
        }
    }
}

ui.batchDefault.on("click", function () { applyBatch("默认"); });
ui.batchNormal.on("click", function () { applyBatch("普通"); });
ui.batchHero.on("click", function () { applyBatch("英雄"); });
ui.batchEpic.on("click", function () { applyBatch("史诗"); });
ui.batchClose.on("click", function () { applyBatch("关闭"); });

// --- 开始战斗 ---
ui.btnStart.on("click", function () {
    // 从 Spinner 读取配置
    for (var hero in spinnerMap) {
        if (spinnerMap.hasOwnProperty(hero)) {
            for (var area in spinnerMap[hero]) {
                if (spinnerMap[hero].hasOwnProperty(area)) {
                    var spinner = spinnerMap[hero][area];
                    config[hero][area] = settings.DIFFICULTY_OPTIONS[spinner.getSelectedItemPosition()];
                }
            }
        }
    }
    configManager.saveConfig(config);
    ui.finish();

    // 在新线程中启动自动化
    threads.start(function () {
        runAutomation();
    });
});

// --- 取消 ---
ui.btnCancel.on("click", function () {
    ui.finish();
    exit();
});

/**
 * 自动化主流程
 */
function runAutomation() {
    // 保持屏幕常亮
    device.keepScreenOn();

    toast("开始运行...");

    // 寻找游戏中的"开始战斗"按钮
    var buttonPos = imageUtils.findImage(settings.PICTURE_DIR + "start_game.png");
    if (buttonPos) {
        game.startGame(buttonPos, config);
        toast("所有英雄已完成");
    } else {
        toast("未找到目标按钮");
    }

    // 清理
    imageUtils.clearTemplateCache();
    exit();
}
