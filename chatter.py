from src.plugin_system.base.base_chatter import BaseChatter
from src.common.data_models.message_manager_data_model import StreamContext
from src.plugin_system.base.component_types import ChatType
from src.plugin_system.apis import send_api
from .manager import battery_manager
import random
import time

class BatteryChatter(BaseChatter):
    chatter_name = "battery_chatter"
    chatter_description = "检测电量并寻找充电机会"
    chat_types = [ChatType.PRIVATE, ChatType.GROUP]

    async def execute(self, context: StreamContext) -> dict:
        stream_id = context.stream_id
        
        # 1. 如果正在充电
        if battery_manager.is_charging:
            # 模拟充电过程
            battery_manager.charge(10)
            if battery_manager.battery_level >= 100:
                battery_manager.is_charging = False
                # 移除直接发送消息，改为通过 Prompt 表现
                # await send_api.text_to_stream("手机电充满了，满血复活！⚡️", stream_id)
                return {
                    "success": True,
                    "stream_id": stream_id,
                    "plan_created": False, # 不需要创建计划，只是更新状态
                    "actions_count": 0
                }
            return {
                "success": True,
                "stream_id": stream_id,
                "plan_created": False,
                "actions_count": 0
            }

        # 2. 如果电量低 (低于 30%)
        if battery_manager.battery_level < 30:
            # 检查是否有充电机会
            can_charge = await battery_manager.check_charging_opportunity()
            
            if can_charge:
                battery_manager.is_charging = True
                battery_manager.charge(5) # 开始充电
                # 移除直接发送消息，改为通过 Prompt 表现
                # await send_api.text_to_stream("这里正好有插座，我先给手机充会儿电~ 🔌", stream_id)
                return {
                    "success": True,
                    "stream_id": stream_id,
                    "plan_created": False, # 不需要创建计划，只是更新状态
                    "actions_count": 0
                }
            
            # 如果电量极低 (低于 10%) 且没在充电
            # 移除直接发送抱怨消息，完全依赖 Prompt 注入让 LLM 自己决定是否抱怨
            # if battery_manager.battery_level < 10 and random.random() < 0.3: ...

        return {
            "success": False,
            "stream_id": stream_id,
            "error_message": "No action needed",
            "executed_count": 0
        }
