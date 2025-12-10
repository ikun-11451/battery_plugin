from src.plugin_system import BaseEventHandler, EventType
from src.plugin_system.base.base_event import HandlerResult
from src.plugin_system.apis import send_api
from .manager import battery_manager
import time

class BatteryCheckHandler(BaseEventHandler):
    handler_name = "battery_check_handler"
    handler_description = "检查电量是否充足，没电则阻止发送"
    weight = 999  # 高优先级，确保在发送前拦截
    init_subscribe = [EventType.ON_MESSAGE] # 改为 ON_MESSAGE，在消息处理前拦截

    async def execute(self, params: dict) -> HandlerResult:
        # 获取消息内容，兼容字符串和对象
        message_obj = params.get("message", "")
        msg_text = ""
        
        if isinstance(message_obj, str):
            msg_text = message_obj
        else:
            # 尝试从对象中获取内容，常见字段名
            for attr in ["content", "message", "text", "msg"]:
                if hasattr(message_obj, attr):
                    msg_text = getattr(message_obj, attr)
                    break
            # 如果还没找到，尝试转字符串
            if not msg_text:
                msg_text = str(message_obj)

        # 如果是 battery 命令，放行
        if msg_text.strip().startswith("/battery"):
             return HandlerResult(success=True, continue_process=True, handler_name=self.handler_name)

        if battery_manager.battery_level <= 0:
            # 没电了，阻止后续流程
            print("[BatteryPlugin] 手机没电了，拦截消息！")
            
            # 检查冷却时间 (300秒 = 5分钟)
            current_time = time.time()
            if current_time - battery_manager.last_dead_reply_time > 300:
                # 获取 stream_id
                stream_id = params.get("stream_id")
                bot_name = params.get("bot_name", "我")
                
                if stream_id:
                    # 直接发送没电提示
                    msg = f"{bot_name}的手机没电了，请等一下..."
                    await send_api.text_to_stream(msg, stream_id)
                    battery_manager.last_dead_reply_time = current_time
                    print(f"[BatteryPlugin] 已发送没电提示: {msg}")

            return HandlerResult(
                success=False,
                continue_process=False,  # 阻断后续流程
                message="手机没电了",
                handler_name=self.handler_name
            )
        
        return HandlerResult(
            success=True,
            continue_process=True,
            handler_name=self.handler_name
        )

class BatteryConsumeHandler(BaseEventHandler):
    handler_name = "battery_consume_handler"
    handler_description = "发送消息后消耗电量"
    weight = 10
    init_subscribe = [EventType.AFTER_SEND]

    async def execute(self, params: dict) -> HandlerResult:
        # 消耗 1% 电量
        new_level = battery_manager.consume(1)
        # print(f"[BatteryPlugin] 发送消息消耗电量，剩余: {new_level}%")
        
        return HandlerResult(
            success=True,
            continue_process=True,
            handler_name=self.handler_name
        )
