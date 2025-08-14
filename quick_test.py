#!/usr/bin/env python3
"""
Fish Audio API 快速测试脚本
这个脚本提供一个简化的测试入口，用于快速验证 API 功能
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test import FishAudioTester
from test_config import FISH_API_KEY, REFERENCE_ID, TEST_SETTINGS, TEST_TEXTS


async def quick_test():
    """快速测试 - 只运行基础功能"""
    print("🚀 Fish Audio API 快速测试")
    print("=" * 30)
    
    # 检查配置
    if FISH_API_KEY == "your_api_key_here":
        print("❌ 请先在 test_config.py 中设置 FISH_API_KEY")
        return False
    
    if REFERENCE_ID == "your_reference_id_here":
        print("❌ 请先在 test_config.py 中设置 REFERENCE_ID")
        return False
    
    print("🔧 配置检查通过")
    print(f"🎯 使用音色: {REFERENCE_ID}")
    
    # 创建测试器
    tester = FishAudioTester(FISH_API_KEY)
    
    try:
        print("\n🧪 开始快速连接测试...")
        
        # 简单的连接和基础 TTS 测试
        result = await tester.test_basic_tts(REFERENCE_ID, "Hello, this is a quick test.")
        
        if result:
            print("✅ 快速测试成功！Fish Audio API 工作正常。")
            
            # 保存音频
            if tester.audio_data_received:
                tester.save_audio_data("quick_test.opus")
            
            print("\n💡 要运行完整测试，请使用：python test.py")
            print("💡 要使用交互模式，请使用：python test.py --interactive")
            return True
        else:
            print("❌ 快速测试失败，请检查配置和网络连接")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False


def check_dependencies():
    """检查依赖项"""
    required_modules = ['websockets', 'ormsgpack']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ 缺少必要的依赖项:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\n💡 请运行: pip install " + " ".join(missing_modules))
        return False
    
    return True


if __name__ == "__main__":
    print("🐟 Fish Audio API 快速测试工具\n")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 运行快速测试
    try:
        success = asyncio.run(quick_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
        sys.exit(1)
