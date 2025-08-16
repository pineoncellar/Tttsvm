"""
管理员权限检查和提升工具
用于确保程序以管理员权限运行，绕过游戏的权限限制
"""

import ctypes
import sys
import os
import subprocess


def is_admin():
    """检查当前程序是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """以管理员权限重新启动程序"""
    if is_admin():
        print("✅ 程序已以管理员权限运行")
        return True
    else:
        print("⚠️ 程序未以管理员权限运行")
        print("🔄 正在尝试以管理员权限重新启动...")
        
        try:
            # 获取当前 Python 解释器和脚本路径
            python_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            
            # 构建命令行参数
            args = [python_exe, script_path] + sys.argv[1:]
            
            # 以管理员权限运行
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                python_exe, 
                ' '.join(f'"{arg}"' for arg in args[1:]),
                None, 
                1
            )
            
            print("✅ 已请求管理员权限，请在 UAC 提示中选择'是'")
            return False  # 当前进程应该退出
            
        except Exception as e:
            print(f"❌ 无法以管理员权限启动: {e}")
            return False


def check_and_elevate():
    """检查并提升权限，如果需要的话"""
    if not is_admin():
        print("🎮 检测到游戏环境，建议以管理员权限运行以确保全局热键正常工作")
        choice = input("是否以管理员权限重新启动？(y/n): ").lower().strip()
        
        if choice in ('y', 'yes', '是'):
            if not run_as_admin():
                sys.exit(0)  # 退出当前进程
        else:
            print("⚠️ 继续以普通权限运行，某些游戏中的热键可能无法工作")
    
    return True


if __name__ == "__main__":
    # 测试权限检查
    if is_admin():
        print("✅ 当前以管理员权限运行")
    else:
        print("❌ 当前以普通权限运行")
        
    check_and_elevate()
