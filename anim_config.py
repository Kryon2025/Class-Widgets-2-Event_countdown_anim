"""事件倒计时动画开关插件配置模型。

模块名刻意避免用 `config`（多个插件都叫 config.py 时会产生顶层模块名冲突，
主程序按插件加载顺序先注册者胜，后加载的插件 `from config import ...` 会解析到
其他插件的 config.py 导致 ImportError）。此模块名 `anim_config` 全局唯一。
"""

from __future__ import annotations

from ClassWidgets.SDK import ConfigBaseModel


class AnimConfig(ConfigBaseModel):
    """事件倒计时动画开关配置。

    :param animation: 是否启用内置"事件倒计时"组件的数字滚动动画，默认开启
    """

    animation: bool = True
