from src.plugin_system.base.plugin_metadata import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="Battery Plugin",
    description="手机电量模拟插件，回复消耗电量，特定地点自动充电。",
    usage="插件加载后自动运行，使用 /battery 查看状态",
    version="1.0.0",
    author="ikun两年半喵",
    license="GPL-3.0",
    repository_url="https://github.com/ikun-11451/battery_plugin/",
    keywords=["battery", "simulation", "roleplay"],
    categories=["娱乐", "角色扮演"],
    extra={
        "is_built_in": False,
        "plugin_type": "user",
    },
)
