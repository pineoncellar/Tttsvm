#!/usr/bin/env python3
"""
独立启动 Fish Audio TTS 服务器
"""

import sys
import os
import time

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fish_audio_server import FishAudioServer
    from test_config import FISH_API_KEY, REFERENCE_ID
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保所有依赖都已安装: pip install flask")
    sys.exit(1)

def main():
    print("🐟 Fish Audio TTS 独立服务器")
    print("=" * 40)
    
    # 检查配置
    if FISH_API_KEY == "your_api_key_here":
        print("❌ 请先在 test_config.py 中配置 FISH_API_KEY")
        print("💡 编辑 test_config.py 文件，设置您的 Fish Audio API 密钥")
        sys.exit(1)
    
    if REFERENCE_ID == "your_reference_id_here":
        print("❌ 请先在 test_config.py 中配置 REFERENCE_ID")
        print("💡 编辑 test_config.py 文件，设置您的参考音色ID")
        sys.exit(1)
    
    # 创建并启动服务器
    server = FishAudioServer(port=10087)
    
    try:
        if server.start():
            print("\n🚀 服务器启动成功!")
            print("📋 可用端点:")
            print("   - TTS API: http://127.0.0.1:10087/")
            print("   - 健康检查: http://127.0.0.1:10087/health")
            print("   - 配置信息: http://127.0.0.1:10087/config")
            print("\n💡 测试命令: python test_fish_server.py")
            print("⏹️  按 Ctrl+C 停止服务器")
            
            # 保持服务器运行
            while server.running:
                time.sleep(1)
        else:
            print("❌ 服务器启动失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ 收到停止信号...")
        server.stop()
        print("👋 服务器已停止，再见!")
    except Exception as e:
        print(f"❌ 服务器错误: {e}")
        server.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
