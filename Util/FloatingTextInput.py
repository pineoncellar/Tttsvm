import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Callable, Optional


class FloatingTextInput:
    """悬浮文本输入窗口"""
    
    def __init__(self, callback: Callable[[str], None], hotkey_manager=None):
        """
        初始化悬浮窗
        
        Args:
            callback: 当用户输入文本并确认时的回调函数
            hotkey_manager: 热键管理器，用于临时禁用热键
        """
        self.callback = callback
        self.hotkey_manager = hotkey_manager
        self.root = None
        self.entry = None
        self.is_visible = False
        self.window_thread = None
        
    def create_window(self):
        """创建悬浮窗"""
        self.root = tk.Tk()
        self.root.title("TTS 语音输入")
        
        # 设置窗口属性
        self.root.geometry("350x120")
        self.root.attributes('-topmost', True)  # 置顶
        self.root.attributes('-alpha', 0.95)    # 半透明
        self.root.resizable(False, False)
        
        # 设置窗口样式 - 深色主题，适合游戏环境
        self.root.configure(bg='#1e1e1e')
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg='#1e1e1e', padx=15, pady=12)
        main_frame.pack(fill='both', expand=True)
        
        # 创建标签
        label = tk.Label(
            main_frame, 
            text="输入文本:",
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Microsoft YaHei', 10, 'bold')
        )
        label.pack(anchor='w', pady=(0, 8))
        
        # 创建输入框
        self.entry = tk.Entry(
            main_frame,
            font=('Microsoft YaHei', 12),
            bg='#2d2d2d',
            fg='#ffffff',
            insertbackground='#ffffff',
            relief='solid',
            bd=1,
            highlightthickness=2,
            highlightcolor='#0078d4',
            highlightbackground='#404040'
        )
        self.entry.pack(fill='x', pady=(0, 12))
        
        # 创建按钮框架
        button_frame = tk.Frame(main_frame, bg='#1e1e1e')
        button_frame.pack(fill='x')
        
        # 确认按钮
        confirm_btn = tk.Button(
            button_frame,
            text="播放 (Enter)",
            command=self.on_confirm,
            bg='#0078d4',
            fg='white',
            font=('Microsoft YaHei', 9, 'bold'),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2',
            activebackground='#106ebe',
            activeforeground='white'
        )
        confirm_btn.pack(side='left', padx=(0, 8))
        
        # 取消按钮
        cancel_btn = tk.Button(
            button_frame,
            text="取消 (Esc)",
            command=self.on_cancel,
            bg='#424242',
            fg='white',
            font=('Microsoft YaHei', 9),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2',
            activebackground='#555555',
            activeforeground='white'
        )
        cancel_btn.pack(side='left')
        
        # 绑定事件
        self.root.bind('<Return>', lambda e: self.on_confirm())
        self.root.bind('<Escape>', lambda e: self.on_cancel())
        self.root.protocol('WM_DELETE_WINDOW', self.on_cancel)
        
        # 绑定窗口焦点事件
        self.root.bind('<FocusOut>', self.on_focus_out)
        
        # 设置焦点到输入框
        self.root.after(100, lambda: self.entry.focus_set())
        
        # 居中显示
        self.center_window()
        
    def on_focus_out(self, event):
        """窗口失去焦点时的处理（可选：自动关闭）"""
        # 注释掉自动关闭功能，避免误操作
        # if event.widget == self.root:
        #     self.hide()
        pass
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def on_confirm(self):
        """确认按钮回调"""
        text = self.entry.get().strip()
        if text:
            self.callback(text)
        self.hide()
        
    def on_cancel(self):
        """取消按钮回调"""
        self.hide()
        
    def show(self):
        """显示悬浮窗"""
        if self.is_visible:
            return
            
        self.is_visible = True
        
        # 临时禁用全局热键，避免冲突
        if self.hotkey_manager:
            self.hotkey_manager.pause()
        
        # 在新线程中创建并显示窗口
        def run_window():
            self.create_window()
            self.root.mainloop()
            
        self.window_thread = threading.Thread(target=run_window, daemon=True)
        self.window_thread.start()
        
    def hide(self):
        """隐藏悬浮窗"""
        if not self.is_visible:
            return
            
        self.is_visible = False
        
        # 重新启用全局热键
        if self.hotkey_manager:
            self.hotkey_manager.resume()
        
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            self.root = None
            self.entry = None
            
    def is_showing(self):
        """检查悬浮窗是否正在显示"""
        return self.is_visible
