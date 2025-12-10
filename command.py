from src.plugin_system import PlusCommand, CommandArgs
from src.plugin_system.utils.permission_decorators import PermissionChecker
from .manager import battery_manager

class BatteryCommand(PlusCommand):
    command_name = "battery"
    command_description = "手机电量管理命令"
    
    async def execute(self, args: CommandArgs) -> tuple[bool, str | None, bool]:
        # 兼容性修复：args.get_first 可能是一个属性而不是方法
        subcommand = args.get_first
        if callable(subcommand):
            subcommand = subcommand()
        
        if subcommand == "status" or subcommand is None:
            status = "正在充电 ⚡️" if battery_manager.is_charging else "未充电"
            msg = f"📱 当前电量: {battery_manager.battery_level}%\n🔌 状态: {status}"
            await self.send_text(msg)
            return True, "查询成功", True
            
        elif subcommand == "charge":
            if not await PermissionChecker.ensure_permission(self.stream_id, "plugins.battery_plugin.manage"):
                return True, None, True
            battery_manager.is_charging = True
            await self.send_text("已连接电源，开始充电！🔌")
            return True, "开始充电", True
            
        elif subcommand == "stop":
            if not await PermissionChecker.ensure_permission(self.stream_id, "plugins.battery_plugin.manage"):
                return True, None, True
            battery_manager.is_charging = False
            await self.send_text("已拔掉电源。")
            return True, "停止充电", True

        elif subcommand == "set":
            if not await PermissionChecker.ensure_permission(self.stream_id, "plugins.battery_plugin.manage"):
                return True, None, True
            # 获取参数列表以支持 set <level>
            arg_list = []
            if hasattr(args, "get_args"):
                val = args.get_args
                arg_list = val() if callable(val) else val
            
            # 获取第二个参数 (index 1)
            level_str = arg_list[1] if arg_list and len(arg_list) > 1 else None

            if not level_str:
                return False, "请指定电量值", True
            try:
                level = int(level_str)
                battery_manager.battery_level = level
                # 获取实际设置后的值（会被限制在 0-100）
                actual_level = battery_manager.battery_level
                await self.send_text(f"电量已设置为 {actual_level}%")
                return True, "设置成功", True
            except ValueError:
                return False, "无效的电量值", True
                
        return False, "未知子命令。可用命令: status, charge, stop, set <level>", True
