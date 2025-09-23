#!/usr/bin/env python3
"""
Dragon机器人Prompt管理工具
用于动态调整和测试不同的prompt配置
"""

import sys
import os

def print_help():
    """显示帮助信息"""
    print("🎯 Dragon机器人Prompt管理工具")
    print("=" * 50)
    print("用法:")
    print("  python prompt_manager.py <命令> [参数]")
    print()
    print("命令:")
    print("  show            - 显示当前prompt配置")
    print("  test <role>     - 测试指定角色配置")
    print("  edit            - 编辑prompt配置文件")
    print("  backup          - 备份当前配置")
    print("  restore <file>  - 恢复配置")
    print("  validate        - 验证配置文件")
    print()
    print("示例:")
    print("  python prompt_manager.py show")
    print("  python prompt_manager.py test friendly")
    print("  python prompt_manager.py edit")

def show_current_config():
    """显示当前配置"""
    try:
        from dragon_prompts_config import DragonRobotPrompts
        prompts = DragonRobotPrompts()
        
        print("🎯 当前Prompt配置:")
        print("=" * 50)
        
        print("\n📋 系统角色:")
        for role_name, role_content in prompts.system_roles.items():
            print(f"  • {role_name}: {role_content[:100]}...")
        
        print("\n🎭 说话风格:")
        for style_name, style_content in prompts.speaking_styles.items():
            print(f"  • {style_name}: {style_content[:80]}...")
        
        print("\n🎬 应用场景:")
        for scenario_name in prompts.scenario_prompts.keys():
            print(f"  • {scenario_name}")
        
        print("\n🤖 机器人确认模板:")
        for template_name in prompts.robot_confirmation_templates.keys():
            print(f"  • {template_name}")
            
        print("\n🧠 知识库增强模板:")
        for template_name in prompts.knowledge_enhancement_templates.keys():
            print(f"  • {template_name}")
        
    except ImportError:
        print("❌ 无法导入dragon_prompts_config模块")
    except Exception as e:
        print(f"❌ 显示配置失败: {e}")

def test_role_config(role_name):
    """测试指定角色配置"""
    try:
        from dragon_prompts_config import DragonRobotPrompts
        prompts = DragonRobotPrompts()
        
        print(f"🧪 测试角色配置: {role_name}")
        print("=" * 50)
        
        if role_name not in prompts.system_roles:
            print(f"❌ 角色 '{role_name}' 不存在")
            print("可用角色:", list(prompts.system_roles.keys()))
            return
        
        role_content = prompts.get_system_role(role_name)
        print(f"✅ 角色内容:\n{role_content}")
        
        # 显示相关的说话风格
        print(f"\n🎭 建议的说话风格:")
        if role_name == "friendly":
            style = prompts.speaking_styles.get("warm", "默认风格")
            print(f"  推荐: warm - {style}")
        elif role_name == "technical":
            style = prompts.speaking_styles.get("professional", "默认风格")
            print(f"  推荐: professional - {style}")
        else:
            print("  使用默认风格")
            
    except ImportError:
        print("❌ 无法导入dragon_prompts_config模块")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def edit_config():
    """编辑配置文件"""
    config_file = "dragon_prompts_config.py"
    
    if not os.path.exists(config_file):
        print(f"❌ 配置文件 {config_file} 不存在")
        return
    
    # 尝试使用不同的编辑器
    editors = ["code", "nano", "vim", "gedit"]
    
    for editor in editors:
        try:
            os.system(f"{editor} {config_file}")
            print(f"✅ 使用 {editor} 打开配置文件")
            print("💡 修改后请使用 'validate' 命令验证配置")
            return
        except:
            continue
    
    print("❌ 无法找到合适的编辑器")
    print(f"请手动编辑文件: {config_file}")

def backup_config():
    """备份配置"""
    import shutil
    from datetime import datetime
    
    config_file = "dragon_prompts_config.py"
    if not os.path.exists(config_file):
        print(f"❌ 配置文件 {config_file} 不存在")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"dragon_prompts_config_backup_{timestamp}.py"
    
    try:
        shutil.copy2(config_file, backup_file)
        print(f"✅ 配置已备份到: {backup_file}")
    except Exception as e:
        print(f"❌ 备份失败: {e}")

def restore_config(backup_file):
    """恢复配置"""
    import shutil
    
    if not os.path.exists(backup_file):
        print(f"❌ 备份文件 {backup_file} 不存在")
        return
    
    config_file = "dragon_prompts_config.py"
    
    try:
        # 先备份当前配置
        if os.path.exists(config_file):
            backup_config()
        
        # 恢复配置
        shutil.copy2(backup_file, config_file)
        print(f"✅ 配置已从 {backup_file} 恢复")
        print("💡 请使用 'validate' 命令验证配置")
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")

def validate_config():
    """验证配置文件"""
    try:
        # 尝试导入配置模块
        import importlib.util
        spec = importlib.util.spec_from_file_location("dragon_prompts_config", "dragon_prompts_config.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 实例化配置类
        prompts = module.DragonRobotPrompts()
        
        print("✅ 配置文件语法正确")
        
        # 检查必要的属性
        required_attrs = [
            'system_roles', 'speaking_styles', 'robot_confirmation_templates',
            'knowledge_enhancement_templates', 'conversation_templates', 'scenario_prompts'
        ]
        
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(prompts, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"⚠️ 缺少必要属性: {missing_attrs}")
        else:
            print("✅ 所有必要属性都存在")
        
        # 检查默认角色
        if 'default' not in prompts.system_roles:
            print("⚠️ 缺少默认角色 'default'")
        else:
            print("✅ 默认角色存在")
        
        print("✅ 配置验证完成")
        
    except SyntaxError as e:
        print(f"❌ 配置文件语法错误: {e}")
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "show":
        show_current_config()
    elif command == "test":
        if len(sys.argv) < 3:
            print("❌ 请指定要测试的角色名称")
            print("用法: python prompt_manager.py test <role_name>")
        else:
            test_role_config(sys.argv[2])
    elif command == "edit":
        edit_config()
    elif command == "backup":
        backup_config()
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ 请指定要恢复的备份文件")
            print("用法: python prompt_manager.py restore <backup_file>")
        else:
            restore_config(sys.argv[2])
    elif command == "validate":
        validate_config()
    elif command in ["help", "-h", "--help"]:
        print_help()
    else:
        print(f"❌ 未知命令: {command}")
        print_help()

if __name__ == "__main__":
    main()
