#!/usr/bin/env python3
"""
Fish Audio 服务器测试脚本
"""

import requests
import json
import time
import os

def test_fish_audio_server():
    """测试 Fish Audio 服务器"""
    base_url = "http://127.0.0.1:10087"
    
    print("🧪 Fish Audio 服务器测试")
    print("=" * 40)
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器状态: {data.get('status')}")
            print(f"🕐 时间戳: {data.get('timestamp')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False
    
    # 2. 配置检查
    print("\n2. 配置检查...")
    try:
        response = requests.get(f"{base_url}/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"✅ 模型: {config.get('model')}")
            print(f"🎯 参考ID: {config.get('reference_id')}")
            print(f"⚙️ 设置: {config.get('settings')}")
        else:
            print(f"❌ 配置检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 配置检查错误: {e}")
    
    # 3. TTS 测试
    print("\n3. TTS 功能测试...")
    try:
        # 准备测试数据
        test_data = {
            "text": "Hello, this is a test of Fish Audio TTS server.",
            "language": "EN",
            "file_type": "opus"
        }
        
        print(f"📤 发送测试请求: {test_data['text'][:30]}...")
        
        response = requests.post(
            f"{base_url}/",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                file_path = result.get('file_path')
                print(f"✅ TTS 生成成功!")
                print(f"📁 文件路径: {file_path}")
                
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"📊 文件大小: {file_size} 字节")
                    return True
                else:
                    print(f"❌ 文件不存在: {file_path}")
                    return False
            else:
                error = result.get('error', '未知错误')
                print(f"❌ TTS 生成失败: {error}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TTS 测试错误: {e}")
        return False

def test_tts_integration():
    """测试与 TTS 系统的集成"""
    print("\n🔗 TTS 集成测试")
    print("=" * 40)
    
    try:
        # 导入 TTS 模块
        import sys
        sys.path.append('.')
        from Util.tts import tts_if_not_exists
        
        # 测试 Fish Audio TTS
        print("📝 测试 Fish Audio TTS 集成...")
        
        test_text = "Integration test for Fish Audio TTS."
        output_dir = "./temp"
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        result_path = tts_if_not_exists(test_text, output_dir, 'fish_audio_tts')
        
        if result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ 集成测试成功!")
            print(f"📁 生成文件: {result_path}")
            print(f"📊 文件大小: {file_size} 字节")
            return True
        else:
            print(f"❌ 集成测试失败: 文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 集成测试错误: {e}")
        return False

if __name__ == "__main__":
    print("🐟 Fish Audio 完整测试套件")
    print("=" * 50)
    
    # 服务器功能测试
    server_ok = test_fish_audio_server()
    
    # 集成测试
    if server_ok:
        integration_ok = test_tts_integration()
        
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        print(f"  服务器测试: {'✅ 通过' if server_ok else '❌ 失败'}")
        print(f"  集成测试: {'✅ 通过' if integration_ok else '❌ 失败'}")
        
        if server_ok and integration_ok:
            print("\n🎉 所有测试通过! Fish Audio TTS 服务器运行正常。")
        else:
            print("\n⚠️ 部分测试失败，请检查配置和网络连接。")
    else:
        print("\n💥 服务器测试失败，跳过集成测试。")
        print("💡 请确保:")
        print("   1. Fish Audio 服务器已启动")
        print("   2. test_config.py 中的 API 密钥已配置")
        print("   3. 网络连接正常")
