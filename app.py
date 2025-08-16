import threading
import time
import os
import sys
import signal
import atexit
from typing import Dict
import pyperclip

from Util.AudioPlayer import AudioPlayer
from Util.EnhancedHotKeyManager import EnhancedGlobalHotKeyManager
from Util.loadSetting import getConfigDict
from Util.SystemTrayIcon import SystemTrayIcon
from Util.tts import tts_if_not_exists
from Util.FloatingTextInput import FloatingTextInput
from Util.admin_utils import is_admin

# 导入 Fish Audio 服务器
try:
    from Util.fish_audio_server import start_fish_audio_server, stop_fish_audio_server
    FISH_AUDIO_AVAILABLE = True
except ImportError:
    FISH_AUDIO_AVAILABLE = False
    print("WARN: Fish Audio 服务器模块不可用")

ap = AudioPlayer()
print('读取音频设备')
# 查看所有设备
# 获取音频输出设备列表
device_dict: Dict[str, int] = ap.get_audio_devices()

def core():
    global device_id, volume, ap, tts_engine
    print(device_id)
    # 读取剪贴板
    if setting_dict['ACTIVATION'] == "<ctrl>+x":
        time.sleep(0.1)
    text = pyperclip.paste()
    print(f'读取剪贴板:{text}')
    process_text_to_speech(text)

def process_text_to_speech(text):
    """处理文本转语音的核心逻辑"""
    global device_id, volume, ap, tts_engine
    # play_wav('./temp/test_converted.wav', device_id, volume)
    # 查询{text}.wav是否在local目录下出现
    if os.path.exists(f'./local/{text}.wav'):
        print(f'查询到{text}.wav')
        ap.play_audio_on_device(f'./local/{text}.wav', device_id, volume)
        print('播放完成')
    else:
        print(f'未查询到{text}.wav')
        # 合成
        path = tts_if_not_exists(text, './temp', tts_engine)
        print(f'音频合成{path}')
        ap.play_audio_on_device(path, device_id, volume)
        print('播放完成')

def core_async():
    threading.Thread(target=core, daemon=True).start()

def floating_input_callback(text):
    """悬浮窗输入回调函数"""
    print(f'悬浮窗输入:{text}')
    threading.Thread(target=lambda: process_text_to_speech(text), daemon=True).start()

def show_floating_input():
    """显示悬浮输入窗口"""
    global floating_input
    if not floating_input.is_showing():
        floating_input.show()

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
    # 注册剪贴板读取热键
    keys = set(setting_dict['ACTIVATION'].split(sep))
    global_hot_key.register(keys, core_async)
    
    # 注册悬浮窗热键
    if 'FLOATING_INPUT' in setting_dict:
        floating_keys = set(setting_dict['FLOATING_INPUT'].split(sep))
        global_hot_key.register(floating_keys, show_floating_input)

def start_fish_audio_service():
    """启动 Fish Audio 服务"""
    global tts_engine
    if FISH_AUDIO_AVAILABLE and tts_engine == 'fish_audio_tts':
        print("正在启动 Fish Audio TTS 服务器...")
        if start_fish_audio_server():
            print("✅ Fish Audio TTS 服务器启动成功")
            return True
        else:
            print("❌ Fish Audio TTS 服务器启动失败，将使用默认 TTS 引擎")
            tts_engine = 'pyttsx3_tts'  # 回退到默认引擎
            return False
    return True

def stop_fish_audio_service():
    """停止 Fish Audio 服务"""
    if FISH_AUDIO_AVAILABLE:
        print("正在停止 Fish Audio TTS 服务器...")
        stop_fish_audio_server()
        print("Fish Audio TTS 服务器已停止")


# 全局变量用于控制程序状态
is_running = True
cleanup_called = False

def cleanup_and_exit():
    """清理资源并退出程序"""
    global cleanup_called
    if cleanup_called:
        return
    cleanup_called = True
    
    print("\n正在清理资源...")
    try:
        stop_fish_audio_service()
        if 'floating_input' in globals() and floating_input:
            floating_input.hide()
        if 'global_hot_key' in globals() and global_hot_key:
            global_hot_key.delete()
        if 'sys_icon' in globals() and sys_icon:
            try:
                sys_icon.icon.stop()
            except:
                pass
        print("资源清理完成")
    except Exception as e:
        print(f"清理资源时出错: {e}")
    finally:
        print("程序已退出")
        # 强制退出，确保程序一定会终止
        os._exit(0)


def signal_handler(signum, frame):
    """信号处理函数，处理 Ctrl+C 等中断信号"""
    global is_running
    print(f"\n收到信号 {signum}，正在退出程序...")
    is_running = False
    cleanup_and_exit()


def exit_handler():
    """程序退出时的清理函数"""
    global is_running
    if is_running:
        print("\n程序正在退出...")
        cleanup_and_exit()


if __name__ == '__main__':
    # 注册退出处理器
    atexit.register(exit_handler)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    if hasattr(signal, 'SIGBREAK'):  # Windows
        signal.signal(signal.SIGBREAK, signal_handler)  # Ctrl+Break
    signal.signal(signal.SIGTERM, signal_handler)  # 终止信号
    
    try:
        # 检查管理员权限
        admin_status = "✅ 管理员权限" if is_admin() else "⚠️ 普通权限"
        print(f"权限状态: {admin_status}")
        
        # 确保工作路径正确
        checkPath()
        global setting_dict, global_hot_key, device_id, volume, tts_engine, sys_icon, floating_input
        # 读取设置
        setting_dict = getConfigDict()
        # 注册全局热键
        global_hot_key = EnhancedGlobalHotKeyManager()
        registerGlobalHotKey()
        global_hot_key.start()
        volume = float(setting_dict['VOLUME'])
        print(f'音量:{volume}')
        # 设置输出设备
        if not setting_dict['DEVICE'] in device_dict:
            raise ValueError(
                f"指定设备:{setting_dict['DEVICE']}不存在,当前设备列表:{device_dict.keys()}")
        device_id = device_dict[setting_dict['DEVICE']]
        tts_engine = setting_dict['TTS_ENGINE']
        
        # 初始化悬浮输入窗口
        floating_input = FloatingTextInput(floating_input_callback, global_hot_key)
        
        # 启动 Fish Audio 服务（如果需要）
        start_fish_audio_service()
        
        print("程序已启动，按 Ctrl+C 或 Ctrl+Break 退出")
        print(f"剪贴板读取热键: {setting_dict['ACTIVATION']}")
        if 'FLOATING_INPUT' in setting_dict:
            print(f"悬浮窗输入热键: {setting_dict['FLOATING_INPUT']}")
        
        # 创建托盘图标，传递清理回调函数
        sys_icon = SystemTrayIcon(cleanup_callback=cleanup_and_exit)
        
        # 在单独的线程中运行托盘图标，避免阻塞主线程
        icon_thread = threading.Thread(target=sys_icon.start, daemon=False)
        icon_thread.start()
        
        # 主线程保持运行，监听键盘中断
        try:
            while is_running and icon_thread.is_alive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n主线程检测到键盘中断...")
            is_running = False
            cleanup_and_exit()
            
    except KeyboardInterrupt:
        # 捕获键盘中断
        print("\n检测到键盘中断...")
        is_running = False
        cleanup_and_exit()
    except Exception as e:
        # 捕获其他异常
        print(f"程序运行时出错: {e}")
        is_running = False
        cleanup_and_exit()
