"""
Event Countdown Animation Toggle
Class Widgets 2 内置"事件倒计时"组件动画开关扩展插件

原理：
1. 内置组件 `classwidgets.eventCountdown`（src/qml/widgets/eventCountdown.qml）的
   分钟/秒数字使用 AnimatedDigits 滚动动画，且无编辑界面、无法关闭动画。
2. 官方插件 API 无法给已注册的内置组件追加设置页（同名注册仅更新名称），
   因此本插件在加载时对主程序 QML 资源打"可逆补丁"（备份原文件），
   使组件支持动画开关；并在主程序设置页（TTS 服务同款模式）提供开关。
3. 卸载插件时自动恢复主程序原始 QML，内置组件不受影响。
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from loguru import logger
from PySide6.QtCore import Slot

from ClassWidgets.SDK import CW2Plugin, PluginAPI

from config import AnimConfig

# 补丁标记：写入补丁版 QML 文件头，用于识别当前文件是否已被本插件修改
PATCH_MARK = "// [patched by com.event.countdown.anim]"


def _main_app_dir() -> Path:
    """主程序 exe 所在目录（插件运行于主程序进程内）。"""
    return Path(sys.executable).parent


def _target_qml() -> Path:
    """内置"事件倒计时"组件的 QML 资源路径。"""
    return _main_app_dir() / "src" / "qml" / "widgets" / "eventCountdown.qml"


class Plugin(CW2Plugin):
    def __init__(self, api: PluginAPI):
        super().__init__(api)
        self._config = AnimConfig()

    # ---- 生命周期 ----------------------------------------------------------

    def on_load(self):
        super().on_load()

        # 注册配置模型（供设置页与补丁 QML 读取）
        try:
            self.api.config.register_plugin_model(self.pid, self._config)
            logger.info("[event.countdown.anim] 配置模型注册成功")
        except Exception as e:
            logger.error("[event.countdown.anim] 配置模型注册失败: {}", e)

        # 对内置组件 QML 打补丁（可逆，卸载时恢复）
        self._patch_qml()

        # 主程序设置页（TTS 服务同款模式）
        self._register_settings_page()

    def on_unload(self):
        # 恢复主程序原始 QML，内置组件不受影响
        self._restore_qml()
        logger.info("[event.countdown.anim] 插件已卸载")

    # ---- QML Slots（设置页调用） ------------------------------------------

    @Slot(result=bool)
    def getAnimation(self) -> bool:
        """当前动画开关状态。"""
        return self._config.animation

    @Slot(bool)
    def setAnimation(self, value: bool) -> None:
        """设置动画开关并持久化（补丁 QML 轮询该值，实时生效）。"""
        self._config.animation = bool(value)
        logger.info("[event.countdown.anim] 动画开关 -> {}", self._config.animation)
        try:
            self.api.config.save()
        except Exception as e:
            logger.warning("[event.countdown.anim] 保存配置失败: {}", e)

    # ---- 主程序 QML 补丁 ----------------------------------------------------

    def _patch_qml(self) -> None:
        target = _target_qml()
        if not target.exists():
            logger.warning("[event.countdown.anim] 未找到内置组件 QML: {}，跳过补丁", target)
            return

        src = target.read_text(encoding="utf-8", errors="ignore")
        if PATCH_MARK in src:
            logger.info("[event.countdown.anim] 组件 QML 已打过补丁，跳过")
            return

        # 首次补丁前备份原版
        bak = target.with_suffix(".qml.bak")
        if not bak.exists():
            bak.write_text(src, encoding="utf-8")
            logger.info("[event.countdown.anim] 已备份原版 QML: {}", bak)

        patch = Path(__file__).parent / "qml" / "eventCountdown.patch.qml"
        if not patch.exists():
            logger.error("[event.countdown.anim] 缺少补丁模板文件，补丁未应用")
            return
        target.write_text(patch.read_text(encoding="utf-8"), encoding="utf-8")
        logger.info("[event.countdown.anim] 已为事件倒计时组件应用动画开关补丁")

    def _restore_qml(self) -> None:
        target = _target_qml()
        bak = target.with_suffix(".qml.bak")
        if not target.exists() or not bak.exists():
            return
        if PATCH_MARK not in target.read_text(encoding="utf-8", errors="ignore"):
            # 当前文件不是本插件补丁版（可能被主程序升级覆盖），保留现状
            logger.info("[event.countdown.anim] 当前 QML 非补丁版，无需恢复")
            return
        shutil.copyfile(bak, target)
        bak.unlink(missing_ok=True)
        logger.info("[event.countdown.anim] 已恢复主程序原始 QML")

    # ---- 设置页 ------------------------------------------------------------

    def _register_settings_page(self) -> None:
        try:
            settings_qml = str(Path(__file__).parent / "qml" / "settings.qml")
            self.api.ui.register_settings_page(
                qml_path=settings_qml,
                title="事件倒计时动画",
                icon="ic_fluent_weather_sunny_20_regular",
            )
            logger.info("[event.countdown.anim] 设置页注册成功")
        except Exception as e:
            logger.warning("[event.countdown.anim] 注册设置页失败: {}", e)
