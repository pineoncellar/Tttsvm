#!/usr/bin/env python3
"""
测试 Fish Audio 到 WAV 转换的完整流程
"""

import requests
import json
import os
import tempfile
from audio_converter import convert_opus_to_wav_simple

def test_fish_audio_to_wav():
    """测试完整的 Fish Audio 到 WAV 转换流程"""
    print("🧪 Fish Audio 到 WAV 转换测试")
    print("=" * 50)
    
    # 1. 调用 Fish Audio API 生成 opus 文件
    test_text = "这是一个测试音频文件转换的例子"
    
    print(f"📝 测试文本: {test_text}")
    
    try:
        # 请求生成 WAV 文件
        response = requests.post(
            "http://127.0.0.1:10087/",
            json={
                "text": test_text,
                "language": "ZH",
                "file_type": "wav"
            },
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                wav_file = result.get('file_path')
                print(f"✅ TTS 请求成功!")
                print(f"📁 生成的文件: {wav_file}")
                
                # 检查文件是否存在
                if os.path.exists(wav_file):
                    file_size = os.path.getsize(wav_file)
                    print(f"📊 文件大小: {file_size} 字节")
                    
                    # 检查文件格式
                    print("\n🔍 检查文件格式...")
                    check_audio_file(wav_file)
                    
                    return True
                else:
                    print(f"❌ 文件不存在: {wav_file}")
                    return False
            else:
                print(f"❌ TTS 生成失败: {result.get('error')}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_audio_file(file_path):
    """检查音频文件的详细信息"""
    try:
        import wave
        
        print(f"📋 检查文件: {file_path}")
        
        # 检查文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        print(f"📄 文件类型: {ext}")
        
        if ext == '.wav':
            # 检查 WAV 文件
            try:
                with wave.open(file_path, 'rb') as wf:
                    channels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    framerate = wf.getframerate()
                    nframes = wf.getnframes()
                    
                    print(f"🎵 声道数: {channels}")
                    print(f"📏 采样宽度: {sampwidth} 字节")
                    print(f"⏱️ 采样率: {framerate} Hz")
                    print(f"🎼 帧数: {nframes}")
                    print(f"⏰ 持续时间: {nframes / framerate:.2f} 秒")
                    
                    if nframes > 0:
                        print("✅ WAV 文件格式正确")
                        return True
                    else:
                        print("❌ WAV 文件没有音频数据")
                        return False
                        
            except Exception as e:
                print(f"❌ WAV 文件格式错误: {e}")
                return False
        
        elif ext == '.opus':
            print("🎵 Opus 文件，尝试转换为 WAV...")
            
            # 生成 WAV 文件名
            wav_file = file_path.replace('.opus', '_converted.wav')
            
            if convert_opus_to_wav_simple(file_path, wav_file):
                print(f"✅ 转换成功: {wav_file}")
                # 递归检查转换后的 WAV 文件
                return check_audio_file(wav_file)
            else:
                print("❌ 转换失败")
                return False
        
        else:
            print(f"⚠️ 未知文件类型: {ext}")
            return False
            
    except Exception as e:
        print(f"❌ 文件检查失败: {e}")
        return False

def test_manual_conversion():
    """手动测试 opus 到 wav 转换"""
    print("\n🔧 手动转换测试")
    print("=" * 30)
    
    # 查找现有的 opus 文件
    temp_dir = "./temp"
    opus_files = [f for f in os.listdir(temp_dir) if f.endswith('.opus')]
    
    if opus_files:
        opus_file = os.path.join(temp_dir, opus_files[0])
        wav_file = opus_file.replace('.opus', '_manual_converted.wav')
        
        print(f"📁 源文件: {opus_file}")
        print(f"📁 目标文件: {wav_file}")
        
        if convert_opus_to_wav_simple(opus_file, wav_file):
            print("✅ 手动转换成功")
            check_audio_file(wav_file)
            return True
        else:
            print("❌ 手动转换失败")
            return False
    else:
        print("❌ 没有找到 opus 文件进行测试")
        return False

if __name__ == "__main__":
    print("🎵 Fish Audio WAV 转换完整测试")
    print("=" * 60)
    
    # 测试完整流程
    test1_ok = test_fish_audio_to_wav()
    
    # 测试手动转换
    test2_ok = test_manual_conversion()
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print(f"  完整流程测试: {'✅ 通过' if test1_ok else '❌ 失败'}")
    print(f"  手动转换测试: {'✅ 通过' if test2_ok else '❌ 失败'}")
    
    if test1_ok and test2_ok:
        print("\n🎉 所有测试通过! 音频转换功能正常。")
    else:
        print("\n⚠️ 部分测试失败，需要检查配置。")
