from src.plugin_system.base.base_prompt import BasePrompt
from src.plugin_system.base.component_types import InjectionRule, InjectionType
from .manager import battery_manager

class BatteryPrompt(BasePrompt):
    prompt_name = "battery_prompt"
    prompt_description = "根据手机电量注入提示词，影响机器人的回复风格"
    
    # 将提示词注入到 planner_prompt (规划提示词) 的末尾
    injection_rules = [
        InjectionRule(
            target_prompt="planner_prompt", 
            injection_type=InjectionType.APPEND, 
            priority=50
        )
    ]

    async def execute(self) -> str:
        level = battery_manager.battery_level
        is_charging = battery_manager.is_charging
        
        prompts = []
        
        if is_charging:
             if level >= 90:
                 prompts.append(f"\n[System Status]: 手机电量即将充满 ({level}%)。你可以表现得开心一点，或者提到准备拔掉电源。")
             else:
                 prompts.append(f"\n[System Status]: 手机正在充电中，当前电量 {level}%。")
        else:
            if level <= 10:
                prompts.append(f"\n[System Status]: ⚠️ 严重警告！手机电量仅剩 {level}%，即将关机！请表现出极度焦虑，回复必须简短，并告诉用户你快没电了，无法继续聊天。")
            elif level <= 20:
                prompts.append(f"\n[System Status]: ⚠️ 警告！手机电量低 ({level}%)。请表现出担忧，并尝试寻找充电机会。")
        
        return "\n".join(prompts)
