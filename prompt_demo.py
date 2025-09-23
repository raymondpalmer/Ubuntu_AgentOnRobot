#!/usr/bin/env python3
"""
Dragon机器人Prompt配置演示脚本
展示如何使用和自定义prompt系统
"""

import sys
import asyncio
from dragon_prompts_config import DragonRobotPrompts

def demo_basic_usage():
    """演示基本使用方法"""
    print("🎯 Dragon机器人Prompt系统演示")
    print("=" * 60)
    
    # 创建配置实例
    prompts = DragonRobotPrompts()
    
    # 1. 显示所有可用选项
    print("\n📋 可用配置选项:")
    print(f"   角色: {prompts.get_available_roles()}")
    print(f"   风格: {prompts.get_available_styles()}")
    print(f"   场景: {prompts.get_available_scenarios()}")
    
    # 2. 获取不同配置
    print("\n🎭 不同角色配置对比:")
    for role in ["default", "friendly", "professional"]:
        config = prompts.get_session_config(scenario="default", style="natural")
        config["system_role"] = prompts.get_system_role(role)
        print(f"\n   {role}角色 (前100字符):")
        print(f"   {config['system_role'][:100]}...")
    
    # 3. 场景配置演示
    print("\n🎬 不同场景配置:")
    for scenario in ["industrial", "home", "education"]:
        config = prompts.get_session_config(scenario=scenario)
        print(f"\n   {scenario}场景:")
        print(f"   系统角色: {config['system_role'][:80]}...")
        print(f"   问候语: {config['greeting']}")

def demo_customization():
    """演示自定义功能"""
    print("\n\n🛠️ 自定义功能演示")
    print("=" * 60)
    
    prompts = DragonRobotPrompts()
    
    # 1. 添加自定义角色
    custom_role = """你是Dragon机器人的幽默助手：
- 用轻松幽默的方式回应用户
- 适当使用俏皮话和比喻
- 让严肃的机器人控制变得有趣
- 保持专业性的同时增加趣味性"""
    
    success = prompts.add_custom_role("humorous", custom_role)
    print(f"✅ 添加自定义角色 'humorous': {success}")
    
    # 2. 测试自定义角色
    test_config = prompts.get_session_config()
    test_config["system_role"] = prompts.get_system_role("humorous")
    print(f"\n🎭 自定义角色内容:")
    print(f"   {test_config['system_role']}")
    
    # 3. 修改现有角色
    original_friendly = prompts.get_system_role("friendly")
    modified_friendly = original_friendly + "\n- 总是以积极乐观的态度回应"
    
    prompts.customize_prompt("friendly", modified_friendly)
    print(f"\n🔧 修改现有角色 'friendly' 成功")
    print(f"   修改后内容 (后50字符): ...{prompts.get_system_role('friendly')[-50:]}")

def demo_templates():
    """演示模板使用"""
    print("\n\n📝 模板系统演示")
    print("=" * 60)
    
    prompts = DragonRobotPrompts()
    
    # 1. 机器人确认模板
    print("🤖 机器人确认模板:")
    action_msg = prompts.robot_confirmation_templates["action_success"].format(
        user_command="机器人前进",
        action="前进"
    )
    print(f"   {action_msg}")
    
    # 2. 知识库增强模板
    print("\n🧠 知识库增强模板:")
    knowledge_msg = prompts.knowledge_enhancement_templates["with_context"].format(
        context="根据操作手册，机器人前进速度为0.5m/s",
        user_question="机器人的前进速度是多少？"
    )
    print(f"   {knowledge_msg}")
    
    # 3. 对话模板
    print(f"\n💬 对话模板:")
    print(f"   问候: {prompts.conversation_templates['greeting']}")
    print(f"   告别: {prompts.conversation_templates['farewell']}")

async def demo_integration():
    """演示与主系统的集成"""
    print("\n\n🔗 主系统集成演示")
    print("=" * 60)
    
    try:
        # 避免音频系统初始化
        print("📡 模拟主系统初始化...")
        
        # 直接演示prompt加载
        from dragon_prompts_config import DragonRobotPrompts
        prompts = DragonRobotPrompts()
        
        print("✅ Prompt配置加载成功")
        print(f"📊 配置统计:")
        print(f"   - 系统角色: {len(prompts.system_roles)} 个")
        print(f"   - 说话风格: {len(prompts.speaking_styles)} 个")
        print(f"   - 应用场景: {len(prompts.scenario_prompts)} 个")
        print(f"   - 确认模板: {len(prompts.robot_confirmation_templates)} 个")
        print(f"   - 知识库模板: {len(prompts.knowledge_enhancement_templates)} 个")
        
        # 模拟实际使用
        print(f"\n🎬 模拟实际使用场景:")
        
        # 场景1：机器人控制确认
        robot_msg = prompts.robot_confirmation_templates["simple_confirm"].format(
            action="左转"
        )
        print(f"   机器人控制: {robot_msg}")
        
        # 场景2：知识库回答
        if "no_context" in prompts.knowledge_enhancement_templates:
            kb_msg = prompts.knowledge_enhancement_templates["no_context"].format(
                user_question="今天天气怎么样？"
            )
            print(f"   知识库回答: {kb_msg[:100]}...")
        
        print("✅ 系统集成演示完成")
        
    except Exception as e:
        print(f"❌ 集成演示失败: {e}")

def interactive_demo():
    """交互式演示"""
    print("\n\n🎮 交互式演示")
    print("=" * 60)
    
    prompts = DragonRobotPrompts()
    
    while True:
        print("\n请选择操作:")
        print("1. 查看角色配置")
        print("2. 测试场景配置") 
        print("3. 自定义角色")
        print("4. 查看模板")
        print("0. 退出")
        
        try:
            choice = input("\n输入选择 (0-4): ").strip()
            
            if choice == "0":
                print("👋 演示结束")
                break
            elif choice == "1":
                role_name = input("输入角色名称 (default/friendly/professional/technical): ").strip()
                if role_name in prompts.get_available_roles():
                    role_content = prompts.get_system_role(role_name)
                    print(f"\n📋 {role_name} 角色配置:")
                    print(f"{role_content}")
                else:
                    print(f"❌ 角色 '{role_name}' 不存在")
                    
            elif choice == "2":
                scenario = input("输入场景名称 (industrial/home/education): ").strip()
                if scenario in prompts.get_available_scenarios():
                    config = prompts.get_session_config(scenario=scenario)
                    print(f"\n🎬 {scenario} 场景配置:")
                    print(f"系统角色: {config['system_role'][:200]}...")
                    print(f"问候语: {config['greeting']}")
                else:
                    print(f"❌ 场景 '{scenario}' 不存在")
                    
            elif choice == "3":
                role_name = input("输入新角色名称: ").strip()
                role_content = input("输入角色描述: ").strip()
                if role_name and role_content:
                    success = prompts.add_custom_role(role_name, role_content)
                    print(f"✅ 自定义角色 '{role_name}' 添加成功: {success}")
                else:
                    print("❌ 角色名称和描述不能为空")
                    
            elif choice == "4":
                print("\n📝 可用模板:")
                print("机器人确认模板:", list(prompts.robot_confirmation_templates.keys()))
                print("知识库模板:", list(prompts.knowledge_enhancement_templates.keys()))
                print("对话模板:", list(prompts.conversation_templates.keys()))
                
            else:
                print("❌ 无效选择")
                
        except KeyboardInterrupt:
            print("\n👋 演示结束")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        # 运行所有演示
        demo_basic_usage()
        demo_customization()
        demo_templates()
        asyncio.run(demo_integration())
        
        print("\n" + "=" * 60)
        print("🎯 演示完成！")
        print("\n💡 提示:")
        print("   - 运行 'python3 prompt_demo.py interactive' 进入交互模式")
        print("   - 使用 'python3 prompt_manager.py' 管理配置")
        print("   - 查看 'PROMPT_CUSTOMIZATION_GUIDE.md' 了解详细用法")

if __name__ == "__main__":
    main()
