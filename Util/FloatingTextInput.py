import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
from typing import Callable, Optional

# Windows 特定的窗口激活支持
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False


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
        
        # Windows特定设置：确保窗口总是在最前面
        if WINDOWS_AVAILABLE:
            self.root.attributes('-toolwindow', True)  # 不在任务栏显示
        
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
        
        # 绑定输入框的额外快捷键
        self.entry.bind('<Control-a>', lambda e: self.entry.select_range(0, tk.END))  # Ctrl+A 全选
        self.entry.bind('<Control-d>', lambda e: self.clear_entry())  # Ctrl+D 清空输入框

        # 绑定窗口焦点事件
        self.root.bind('<FocusOut>', self.on_focus_out)
        
        # 居中显示
        self.center_window()
        
        # 强制窗口获得焦点和置顶
        self.force_focus()
        
    def on_focus_out(self, event):
        """窗口失去焦点时的处理（可选：自动关闭）"""
        # 注释掉自动关闭功能，避免误操作
        # if event.widget == self.root:
        #     self.hide()
        pass
    
    def clear_entry(self):
        """清空输入框"""
        if self.entry:
            self.entry.delete(0, tk.END)
        return 'break'  # 阻止事件继续传播
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def force_focus(self):
        """强制窗口获得焦点"""
        try:
            # 确保窗口可见并置顶
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            
            # Windows 特定的窗口激活
            if WINDOWS_AVAILABLE:
                try:
                    # 获取窗口句柄
                    hwnd = self.root.winfo_id()
                    
                    # 使用 Windows API 强制激活窗口
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    ctypes.windll.user32.BringWindowToTop(hwnd)
                    ctypes.windll.user32.SetActiveWindow(hwnd)
                    
                    # 如果上述方法失败，尝试使用 AttachThreadInput
                    foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
                    if foreground_hwnd != hwnd:
                        foreground_thread = ctypes.windll.user32.GetWindowThreadProcessId(foreground_hwnd, None)
                        current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
                        
                        if foreground_thread != current_thread:
                            ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, True)
                            ctypes.windll.user32.SetForegroundWindow(hwnd)
                            ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, False)
                except Exception as e:
                    print(f"Windows API 窗口激活失败: {e}")
            
            # 强制激活窗口 (跨平台方法)
            self.root.focus_force()
            
            # 延迟设置输入框焦点，确保窗口完全加载
            def set_entry_focus():
                try:
                    if self.entry:
                        self.entry.focus_set()
                        self.entry.icursor(tk.END)  # 将光标移到输入框末尾
                        # 选中所有现有文本（如果有的话）
                        self.entry.select_range(0, tk.END)
                except:
                    pass
            
            # 多次尝试设置焦点，确保成功
            self.root.after(50, set_entry_focus)
            self.root.after(150, set_entry_focus)
            self.root.after(300, set_entry_focus)
            
        except Exception as e:
            print(f"设置窗口焦点时出错: {e}")
        
    def on_confirm(self):
        """确认按钮回调"""
        text = self.entry.get().strip()
        if text:
            self.callback(text)
        # 清空输入框内容，为下次使用做准备
        if self.entry:
            self.entry.delete(0, tk.END)
        self.hide()
        
    def on_cancel(self):
        """取消按钮回调"""
        # 清空输入框内容
        if self.entry:
            self.entry.delete(0, tk.END)
        self.hide()
        
    def show(self):
        """显示悬浮窗"""
        if self.is_visible:
            # 如果窗口已经显示，重新获得焦点
            if self.root and self.entry:
                self.force_focus()
            return
            
        self.is_visible = True
        
        # 临时禁用全局热键，避免冲突
        if self.hotkey_manager:
            self.hotkey_manager.pause()
        
        # 在新线程中创建并显示窗口
        def run_window():
            try:
                self.create_window()
                # 确保窗口在创建后获得焦点
                self.root.after(10, self.force_focus)
                self.root.mainloop()
            except Exception as e:
                print(f"显示悬浮窗时出错: {e}")
                self.hide()
                
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
                # 隐藏窗口前先取消置顶属性，让系统自然恢复焦点
                self.root.attributes('-topmost', False)
                time.sleep(0.05)  # 短暂延迟让系统处理
                
                self.root.quit()
                self.root.destroy()
            except:
                pass
            self.root = None
            self.entry = None
            
    def is_showing(self):
        """检查悬浮窗是否正在显示"""
        return self.is_visible
