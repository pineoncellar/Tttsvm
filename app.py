import threading
import wave
import os
import sys
from typing import Dict
import pyperclip

from Util.AudioPlayer import AudioPlayer
from Util.globalHotKeyManager import GlobalHotKeyManager
from Util.loadSetting import getConfigDict
from Util.SystemTrayIcon import SystemTrayIcon
from Util.tts import tts_if_not_exists

ap = AudioPlayer()
print('读取音频设备')
# 查看所有设备
# 获取音频输出设备列表
device_dict: Dict[str, int] = ap.get_audio_devices()

def core():
    global device_id, volume,ap
    print(device_id)
    # 读取剪贴板
    text = pyperclip.paste()
    print(f'读取剪贴板:{text}')
    # play_wav('./temp/test_converted.wav', device_id, volume)
    # 查询{text}.wav是否在local目录下出现
    if os.path.exists(f'./local/{text}.wav'):
        print(f'查询到{text}.wav')
        ap.play_audio_on_device(f'./local/{text}.wav', device_id, volume)
    else:
        print(f'未查询到{text}.wav')
        # 合成
        path = tts_if_not_exists(text, './temp')
        ap.play_audio_on_device(path, device_id, volume)

def core_async():
    threading.Thread(target=core, daemon=True).start()

def checkPath():
    """确保工作路径正确"""
    # 获取当前工作路径
    current_work_dir = os.getcwd()
    print(f"当前工作路径：{current_work_dir}")

    # 获取当前文件所在路径
    current_file_dir = os.path.dirname(__file__)
    print(f"文件所在路径：{current_file_dir}")
    # 如果文件所在路径末尾是(_internal),跳转到上一级
    if '_internal' == current_file_dir[-9:]:
        current_file_dir = current_file_dir[:-9]
        print('internal')
        print(f"文件所在路径：{current_file_dir}")

    # 如果工作路径不是文件所在路径，切换到文件所在路径
    if current_work_dir != current_file_dir:
        os.chdir(current_file_dir)
        print("已切换到文件所在路径。")
    # 检查./local目录是否存在
    if not os.path.exists('./local'):
        os.mkdir('./local')
        print("已创建./local目录")
    # 检查./temp目录是否存在
    if not os.path.exists('./temp'):
        os.mkdir('./temp')
        print("已创建./temp目录")


def registerGlobalHotKey():
    global global_hot_key, setting_dict
    # 获取分隔符
    sep = setting_dict['AND']
    keys = set(setting_dict['ACTIVATION'].split(sep))
    global_hot_key.register(keys, core_async)


if __name__ == '__main__':
    # 确保工作路径正确
    checkPath()
    global setting_dict, global_hot_key, device_id, volume
    # 读取设置
    setting_dict = getConfigDict()
    # 注册全局热键
    global_hot_key = GlobalHotKeyManager()
    registerGlobalHotKey()
    global_hot_key.start()
    volume = float(setting_dict['VOLUME'])
    print(f'音量:{volume}')
    # 设置输出设备
    if not setting_dict['DEVICE'] in device_dict:
        raise ValueError(
            f"指定设备:{setting_dict['DEVICE']}不存在,当前设备列表:{device_dict.keys()}")
    device_id = device_dict[setting_dict['DEVICE']]
    # 托盘图标
    sys_icon = SystemTrayIcon()
    # 开启图标,阻塞主线程
    sys_icon.start()
    # 图标关闭,退出程序
    global_hot_key.delete()
    sys.exit(0)
