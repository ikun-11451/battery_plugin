from src.plugin_system import BasePlugin, register_plugin
from src.plugin_system.base.config_types import ConfigField
from src.plugin_system.base.component_types import PermissionNodeField
from .manager import battery_manager
from .handlers import BatteryCheckHandler, BatteryConsumeHandler
from .chatter import BatteryChatter
from .command import BatteryCommand
from .prompt import BatteryPrompt

@register_plugin
class BatteryPlugin(BasePlugin):
    plugin_name = "battery_plugin"
    plugin_description = "手机电量模拟插件，回复消耗电量，特定地点自动充电。"
    plugin_version = "1.0.0"
    plugin_author = "ikun两年半 <https://github.com/ikun-11451>"

    enable_plugin = True
    config_file_name = "config.toml"
    
    permission_nodes = [
        PermissionNodeField(
            node_name="manage",
            description="允许管理电池状态（充电、停止充电、设置电量）"
        )
    ]
    
    # 定义配置模式，系统会自动生成 config.toml
    config_schema = {
        "battery": {
            "initial_level": ConfigField(type=int, default=100, description="初始电量"),
            "consume_per_reply": ConfigField(type=int, default=1, description="每次回复消耗电量"),
            "charge_speed": ConfigField(type=int, default=5, description="每次充电增加电量"),
        },
        "keywords": {
            "charge_locations": ConfigField(
                type=list, 
                default=["家", "公司", "办公室", "宿舍", "星巴克", "咖啡馆"], 
                description="由llm自动判断，llm无法调用降级到此方案，允许充电的地点关键词"
            )
        }
    }

    def get_plugin_components(self):
        return [
            (BatteryCheckHandler.get_handler_info(), BatteryCheckHandler),
            (BatteryConsumeHandler.get_handler_info(), BatteryConsumeHandler),
            (BatteryChatter.get_chatter_info(), BatteryChatter),
            (BatteryCommand.get_plus_command_info(), BatteryCommand),
            (BatteryPrompt.get_prompt_info(), BatteryPrompt),
        ]

    async def on_plugin_loaded(self):
        # 从配置中加载初始设置
        initial_level = self.get_config("battery.initial_level", 100)
        charge_keywords = self.get_config("keywords.charge_locations", [])
        
        # 更新管理器配置
        # 注意：这里简单的覆盖可能不完美，实际应考虑 storage 和 config 的优先级
        # 但为了演示，我们假设 config 优先于默认值
        if battery_manager.storage.get("charge_keywords") is None:
             battery_manager.storage.set("charge_keywords", charge_keywords)

        print(f"[{self.plugin_name}] 插件已加载，当前电量: {battery_manager.battery_level}%")
