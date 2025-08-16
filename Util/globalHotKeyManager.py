from pynput import keyboard
from pynput.keyboard import HotKey
import warnings
import logging


class GlobalHotKeyManager:
    """利用GlobalHotKeys注册全局快捷键,提供注册函数和删除函数"""

    def __init__(self):
        self.hotkeys = {}  # 一个字典，存储已注册的全局快捷键和对应的回调函数
        self.globalHotKeys = None
        self.is_paused = False

    def register(self, keys, callback=None):
        """注册函数,将set包含的按键组合注册为全局快捷键,传入回调函数,当按键组合被触发时执行"""
        # 将按键组合转换为pynput期望的字符串格式
        hotkey_str = self._keys_to_hotkey_string(keys)
        
        if not hotkey_str:
            print(f"错误: 无效的按键组合 {keys}")
            return
            
        print(f"注册热键: {hotkey_str}")
        
        # 存储按键组合和回调函数
        self.hotkeys[hotkey_str] = callback if callback is not None else lambda: print(f'{hotkey_str} is pressed')
        
    def _keys_to_hotkey_string(self, keys):
        """将按键组合转换为pynput期望的字符串格式"""
        parts = []
        
        for key in keys:
            key = key.strip().lower()
            if key.startswith('<') and key.endswith('>'):
                key = key[1:-1]  # 去掉 < >
            
            # 映射修饰键
            if key in ['ctrl', 'control']:
                parts.append('<ctrl>')
            elif key in ['alt']:
                parts.append('<alt>')
            elif key in ['shift']:
                parts.append('<shift>')
            elif key in ['cmd', 'command']:
                parts.append('<cmd>')
            elif key in ['tab']:
                parts.append('<tab>')
            elif key in ['esc', 'escape']:
                parts.append('<esc>')
            elif key in ['enter', 'return']:
                parts.append('<enter>')
            elif key in ['space']:
                parts.append('<space>')
            elif key in ['backspace']:
                parts.append('<backspace>')
            elif key in ['delete', 'del']:
                parts.append('<delete>')
            elif key in ['home']:
                parts.append('<home>')
            elif key in ['end']:
                parts.append('<end>')
            elif key in ['page_up', 'pageup']:
                parts.append('<page_up>')
            elif key in ['page_down', 'pagedown']:
                parts.append('<page_down>')
            elif key.startswith('f') and key[1:].isdigit():
                # 功能键 F1-F12
                fn_num = int(key[1:])
                if 1 <= fn_num <= 12:
                    parts.append(f'<f{fn_num}>')
            elif len(key) == 1:
                # 单个字符键
                parts.append(key)
            else:
                print(f"警告: 无法识别的按键 '{key}'")
                
        if not parts:
            return None
            
        # 按字母顺序排序，确保一致性，但保持修饰键在前
        modifiers = []
        chars = []
        
        for part in parts:
            if part.startswith('<') and part.endswith('>'):
                modifiers.append(part)
            else:
                chars.append(part)
        
        # 修饰键排序
        modifiers.sort()
        chars.sort()
        
        return '+'.join(modifiers + chars)

    def start(self):
        """启动全局热键监听"""
        if not self.hotkeys:
            print("警告: 没有注册任何热键")
            return
            
        # 尝试创建一个新的GlobalHotKeys对象，传入字典
        try:
            print(f"启动全局热键监听，共 {len(self.hotkeys)} 个热键")
            self.globalHotKeys = keyboard.GlobalHotKeys(self.hotkeys)
            self.globalHotKeys.start()
            print("✅ 全局热键启动成功")
        except ValueError as e:
            # 如果出现ValueError异常，说明有些快捷键已经被占用，发出一个警告信息，并记录异常信息
            print(f"❌ 全局热键启动失败: {e}")
            warnings.warn('Some hotkeys are already registered by another program.')
            logging.exception(e)
            return
        except Exception as e:
            print(f"❌ 全局热键启动时发生未知错误: {e}")
            logging.exception(e)
            return

    def delete(self):
        """删除函数,用于删除所有通过注册函数注册的全局快捷键"""
        # 如果有GlobalHotKeys对象，停止它
        if self.globalHotKeys:
            try:
                self.globalHotKeys.stop()
                print("全局热键已停止")
            except Exception as e:
                print(f"停止全局热键时出错: {e}")
        # 清空字典
        self.hotkeys.clear()
        # 将GlobalHotKeys对象设为None
        self.globalHotKeys = None
        
    def pause(self):
        """暂停全局热键监听"""
        if self.globalHotKeys and not self.is_paused:
            try:
                self.globalHotKeys.stop()
                self.is_paused = True
                print("全局热键已暂停")
            except Exception as e:
                print(f"暂停全局热键时出错: {e}")
            
    def resume(self):
        """恢复全局热键监听"""
        if self.is_paused and self.hotkeys:
            try:
                self.globalHotKeys = keyboard.GlobalHotKeys(self.hotkeys)
                self.globalHotKeys.start()
                self.is_paused = False
                print("全局热键已恢复")
            except ValueError as e:
                print(f"恢复全局热键失败: {e}")
                warnings.warn('Some hotkeys are already registered by another program.')
                logging.exception(e)
            except Exception as e:
                print(f"恢复全局热键时发生未知错误: {e}")
                logging.exception(e)