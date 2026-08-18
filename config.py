"""事件倒计时动画开关插件配置模型。"""

from __future__ import annotations

from ClassWidgets.SDK import ConfigBaseModel


class AnimConfig(ConfigBaseModel):
    """事件倒计时动画开关配置。

    :param animation: 是否启用内置"事件倒计时"组件的数字滚动动画，默认开启
    """

    animation: bool = True
