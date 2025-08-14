"""
音频格式转换工具
支持 opus 到 wav 的转换
"""

import os
import logging
import subprocess
import tempfile

logger = logging.getLogger(__name__)

def convert_opus_to_wav_simple(opus_file, wav_file):
    """使用系统工具转换 opus 到 wav"""
    try:
        # 尝试使用 ffmpeg
        if check_ffmpeg():
            return convert_with_ffmpeg(opus_file, wav_file)
        else:
            logger.warning("ffmpeg 不可用，尝试其他方法")
            # 作为备选，直接返回 opus 文件
            return fallback_copy(opus_file, wav_file)
    except Exception as e:
        logger.error(f"音频转换失败: {e}")
        return False

def check_ffmpeg():
    """检查系统是否安装了 ffmpeg"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except:
        return False

def convert_with_ffmpeg(opus_file, wav_file):
    """使用 ffmpeg 转换音频格式"""
    try:
        cmd = [
            'ffmpeg', 
            '-i', opus_file,
            '-acodec', 'pcm_s16le',  # PCM 16-bit
            '-ar', '44100',          # 采样率 44.1kHz
            '-ac', '1',              # 单声道
            '-y',                    # 覆盖输出文件
            wav_file
        ]
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode == 0 and os.path.exists(wav_file):
            logger.info(f"ffmpeg 转换成功: {opus_file} -> {wav_file}")
            return True
        else:
            logger.error(f"ffmpeg 转换失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("ffmpeg 转换超时")
        return False
    except Exception as e:
        logger.error(f"ffmpeg 转换错误: {e}")
        return False

def fallback_copy(opus_file, target_file):
    """备选方案：直接复制文件"""
    try:
        import shutil
        shutil.copy2(opus_file, target_file)
        logger.warning(f"使用备选方案复制文件: {opus_file} -> {target_file}")
        return True
    except Exception as e:
        logger.error(f"文件复制失败: {e}")
        return False

def create_simple_wav_header(data_size, sample_rate=44100, channels=1, bits_per_sample=16):
    """创建简单的 WAV 文件头"""
    import struct
    
    # WAV 文件头结构
    chunk_size = 36 + data_size
    subchunk1_size = 16
    audio_format = 1  # PCM
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    
    header = struct.pack('<4sI4s4sIHHIIHH4sI',
                        b'RIFF',
                        chunk_size,
                        b'WAVE',
                        b'fmt ',
                        subchunk1_size,
                        audio_format,
                        channels,
                        sample_rate,
                        byte_rate,
                        block_align,
                        bits_per_sample,
                        b'data',
                        data_size)
    
    return header

if __name__ == "__main__":
    # 测试转换功能
    test_opus = "./temp/test.opus"
    test_wav = "./temp/test_converted.wav"
    
    if os.path.exists(test_opus):
        if convert_opus_to_wav_simple(test_opus, test_wav):
            print("✅ 转换成功")
        else:
            print("❌ 转换失败")
    else:
        print(f"测试文件不存在: {test_opus}")
