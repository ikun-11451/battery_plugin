from src.plugin_system.apis import storage_api, schedule_api, llm_api
from typing import Optional, List, Dict, Any
import time

class BatteryManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BatteryManager, cls).__new__(cls)
            cls._instance.storage = storage_api.get_local_storage("battery_plugin")
            cls._instance._init_data()
            cls._instance.last_complaint_time = 0  # 初始化上次抱怨时间
            cls._instance.last_dead_reply_time = 0 # 初始化上次没电回复时间
        return cls._instance

    def _init_data(self):
        """初始化默认数据"""
        if self.storage.get("battery_level") is None:
            self.storage.set("battery_level", 100)
        
        if self.storage.get("is_charging") is None:
            self.storage.set("is_charging", False)

        # 默认充电地点关键词
        if self.storage.get("charge_keywords") is None:
            self.storage.set("charge_keywords", ["家", "公司", "办公室", "宿舍", "星巴克", "咖啡馆"])

    @property
    def battery_level(self) -> int:
        return self.storage.get("battery_level", 100)

    @battery_level.setter
    def battery_level(self, value: int):
        # 限制电量在 0-100 之间
        value = max(0, min(100, value))
        self.storage.set("battery_level", value)

    @property
    def is_charging(self) -> bool:
        return self.storage.get("is_charging", False)

    @is_charging.setter
    def is_charging(self, value: bool):
        self.storage.set("is_charging", value)

    def consume(self, amount: int = 1) -> int:
        """消耗电量"""
        if self.is_charging:
            return self.battery_level
        
        current = self.battery_level
        self.battery_level = current - amount
        return self.battery_level

    def charge(self, amount: int = 5) -> int:
        """充电"""
        current = self.battery_level
        self.battery_level = current + amount
        return self.battery_level

    async def check_charging_opportunity(self) -> bool:
        """检查当前日程是否在充电地点"""
        # 获取当前活动
        current_activity = await schedule_api.get_current_activity()
        
        if not current_activity:
            return False

        activity_text = ""
        if isinstance(current_activity, dict):
            activity_text = current_activity.get("activity", "")
        elif isinstance(current_activity, str):
            activity_text = current_activity
            
        if not activity_text:
            return False
        
        # 尝试使用 LLM 判断
        try:
            models = llm_api.get_available_models()
            if models:
                # 获取第一个可用模型
                model_config = list(models.values())[0]
                
                prompt = f"""
                请判断以下地点或活动场景是否通常具备给手机充电的条件（有公共插座或私人电源）。
                地点/活动：{activity_text}
                请仅回答“是”或“否”，不要包含其他内容。
                """
                
                success, content, _, _ = await llm_api.generate_with_model(
                    prompt=prompt,
                    model_config=model_config,
                    request_type="plugin.battery_check",
                    temperature=0.1
                )
                
                if success:
                    # 只要包含"是"就认为是
                    return "是" in content
                else:
                    print("[BatteryPlugin] LLM 调用失败，降级为关键词匹配")
        except Exception as e:
            print(f"[BatteryPlugin] LLM 判断出错: {e}，降级为关键词匹配")

        # 降级方案：关键词匹配
        return self._check_by_keywords(activity_text)

    def _check_by_keywords(self, activity_text: str) -> bool:
        keywords = self.storage.get("charge_keywords", [])
        for keyword in keywords:
            if keyword in activity_text:
                return True
        return False

# 全局单例
battery_manager = BatteryManager()
