import os
import hashlib
import pyttsx3

def tts_if_not_exists(text, directory):
    # 计算字符串的MD5值
    md5_hash = hashlib.md5(text.encode()).hexdigest()
    filename = f"{md5_hash}.wav"
    filepath = os.path.join(directory, filename)
    # 检查文件是否存在于指定目录中
    if not os.path.exists(filepath):
        # 文件不存在，使用pyttsx3合成wav文件
        engine = pyttsx3.init()
        # 设置输出到文件
        engine.save_to_file(text, filepath)
        # 执行TTS
        engine.runAndWait()
        # 关闭引擎
        engine.stop()

    # 返回文件的绝对路径
    return os.path.abspath(filepath)