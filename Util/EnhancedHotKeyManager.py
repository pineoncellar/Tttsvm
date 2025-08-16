"""
增强版全局热键管理器
在原有pynput基础上添加更好的错误处理和兼容性
"""

from Util.globalHotKeyManager import GlobalHotKeyManager
from Util.admin_utils import is_admin


class EnhancedGlobalHotKeyManager:
    """增强版全局热键管理器，基于pynput实现"""
    
    def __init__(self):
        self.hotkey_manager = GlobalHotKeyManager()
        self.is_initialized = False
        
    def register(self, keys, callback):
        """注册热键"""
        try:
            self.hotkey_manager.register(keys, callback)
        except Exception as e:
            print(f"❌ 注册热键失败: {e}")
            
    def start(self):
        """启动热键监听"""
        try:
            # 检查权限状态
            if not is_admin():
                print("💡 提示: 以管理员权限运行可获得更好的游戏兼容性")
            
            self.hotkey_manager.start()
            self.is_initialized = True
            print("✅ 全局热键启动成功")
            
        except Exception as e:
            print(f"❌ 启动热键管理器失败: {e}")
            
    def pause(self):
        """暂停热键监听"""
        if self.is_initialized:
            self.hotkey_manager.pause()
            
    def resume(self):
        """恢复热键监听"""
        if self.is_initialized:
            self.hotkey_manager.resume()
            
    def delete(self):
        """删除所有热键"""
        if self.is_initialized:
            self.hotkey_manager.delete()
            self.is_initialized = False
