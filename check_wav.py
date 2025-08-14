#!/usr/bin/env python3
"""
检查 WAV 文件格式和内容的工具
"""

import wave
import os
import struct

def check_wav_file(filepath):
    """检查 WAV 文件的详细信息"""
    print(f"检查文件: {filepath}")
    print("=" * 50)
    
    if not os.path.exists(filepath):
        print("❌ 文件不存在")
        return False
    
    file_size = os.path.getsize(filepath)
    print(f"📊 文件大小: {file_size} 字节")
    
    # 检查文件头
    try:
        with open(filepath, 'rb') as f:
            # 读取前44字节（WAV文件头）
            header = f.read(44)
            print(f"📋 文件头长度: {len(header)} 字节")
            
            if len(header) >= 12:
                riff_id = header[0:4].decode('ascii', errors='ignore')
                file_size_header = struct.unpack('<I', header[4:8])[0]
                wave_id = header[8:12].decode('ascii', errors='ignore')
                
                print(f"🎵 RIFF ID: {riff_id}")
                print(f"📏 头部文件大小: {file_size_header}")
                print(f"🌊 WAVE ID: {wave_id}")
                
                if riff_id != 'RIFF' or wave_id != 'WAVE':
                    print("❌ 这不是一个有效的 WAV 文件")
                    return False
            
            # 重置文件指针
            f.seek(0)
            # 读取所有数据检查是否有内容
            all_data = f.read()
            print(f"📊 实际文件内容: {len(all_data)} 字节")
            
            # 检查是否有音频数据（非零字节）
            non_zero_count = sum(1 for byte in all_data if byte != 0)
            print(f"🎚️ 非零字节数: {non_zero_count} / {len(all_data)}")
            
    except Exception as e:
        print(f"❌ 读取文件头失败: {e}")
        return False
    
    # 使用 wave 模块检查
    try:
        with wave.open(filepath, 'rb') as wf:
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            nframes = wf.getnframes()
            
            print(f"🎵 声道数: {channels}")
            print(f"📏 采样宽度: {sampwidth} 字节")
            print(f"⏱️ 采样率: {framerate} Hz")
            print(f"🎼 帧数: {nframes}")
            print(f"⏰ 持续时间: {nframes / framerate:.2f} 秒")
            
            # 读取一些音频数据检查
            frames = wf.readframes(min(1024, nframes))
            if frames:
                print(f"🎚️ 音频数据样本: {len(frames)} 字节")
                # 检查是否全是静音
                import array
                if sampwidth == 2:
                    audio_array = array.array('h', frames)
                    max_amplitude = max(abs(x) for x in audio_array) if audio_array else 0
                    print(f"🔊 最大振幅: {max_amplitude}")
                    if max_amplitude == 0:
                        print("⚠️ 警告: 音频数据全为静音")
                    else:
                        print("✅ 音频数据包含有效信号")
            else:
                print("❌ 无法读取音频数据")
                return False
            
        print("✅ WAV 文件格式检查通过")
        return True
        
    except Exception as e:
        print(f"❌ WAV 文件格式错误: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # 检查 temp 目录中的 WAV 文件
    temp_dir = "./temp"
    wav_files = [f for f in os.listdir(temp_dir) if f.endswith('.wav')]
    
    if wav_files:
        print(f"找到 {len(wav_files)} 个 WAV 文件:")
        for wav_file in wav_files:
            filepath = os.path.join(temp_dir, wav_file)
            check_wav_file(filepath)
            print()
    else:
        print("❌ temp 目录中没有找到 WAV 文件")
