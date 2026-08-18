import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Plugins


PluginPage {
    id: root
    pluginId: "com.event.countdown.anim"
    title: "事件倒计时动画"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        SettingCard {
            Layout.fillWidth: true
            title: "动画效果"
            description: "开启后内置“事件倒计时”组件的分钟/秒数字带滚动动画；关闭后静态显示。"

            Switch {
                checked: backend ? backend.getAnimation() : true
                onCheckedChanged: {
                    if (backend) backend.setAnimation(checked)
                }
            }
        }

        SettingCard {
            Layout.fillWidth: true
            title: "说明"
            description: "本插件为内置“事件倒计时”组件（剩余时间）添加动画开关。\n安装后如组件未立即生效，请重启 Class Widgets 2；卸载插件后组件恢复原始样式。"
        }
    }
}
