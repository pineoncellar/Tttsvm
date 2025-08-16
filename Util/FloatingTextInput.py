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
        
        # Windows特定设置：确保窗口总是在最前面，即使在游戏中
        if WINDOWS_AVAILABLE:
            self.root.attributes('-toolwindow', True)  # 不在任务栏显示
            # 设置窗口为系统模态，确保能覆盖全屏游戏
            try:
                hwnd = self.root.winfo_id()
                # 设置窗口样式，使其能够覆盖全屏应用
                ctypes.windll.user32.SetWindowPos(
                    hwnd, -1,  # HWND_TOPMOST
                    0, 0, 0, 0,
                    0x0001 | 0x0002 | 0x0010  # SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
                )
            except:
                pass
        
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
    
    def is_fullscreen_app_active(self):
        """检测当前是否有全屏应用（如游戏）在运行"""
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            # 获取前台窗口
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if hwnd == 0:
                return False
                
            # 获取窗口矩形
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            # 获取屏幕尺寸
            screen_width = ctypes.windll.user32.GetSystemMetrics(0)
            screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            
            # 检查窗口是否占据整个屏幕
            window_width = rect.right - rect.left
            window_height = rect.bottom - rect.top
            
            is_fullscreen = (window_width >= screen_width and 
                           window_height >= screen_height and 
                           rect.left <= 0 and rect.top <= 0)
            
            if is_fullscreen:
                print("🎮 检测到全屏应用程序")
            
            return is_fullscreen
        except:
            return False
    
    def force_focus(self):
        """强制窗口获得焦点"""
        try:
            # 检测是否有全屏应用
            is_game_mode = self.is_fullscreen_app_active()
            
            # 确保窗口可见并置顶
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            
            # Windows 特定的窗口激活 - 针对游戏环境增强
            if WINDOWS_AVAILABLE:
                try:
                    # 获取窗口句柄
                    hwnd = self.root.winfo_id()
                    
                    if is_game_mode:
                        print("🎮 游戏模式 - 使用强制激活策略")
                        # 游戏模式：使用更激进的方法
                        
                        # 模拟 Alt+Tab 来打断游戏的焦点锁定
                        ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)  # Alt down
                        time.sleep(0.02)
                        ctypes.windll.user32.keybd_event(0x09, 0, 0, 0)  # Tab down
                        time.sleep(0.02)
                        ctypes.windll.user32.keybd_event(0x09, 0, 2, 0)  # Tab up
                        time.sleep(0.02)
                        
                        # 强制设置我们的窗口为前台
                        foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
                        foreground_thread = ctypes.windll.user32.GetWindowThreadProcessId(foreground_hwnd, None)
                        current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
                        
                        if foreground_thread != current_thread:
                            ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, True)
                        
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                        ctypes.windll.user32.SetActiveWindow(hwnd)
                        ctypes.windll.user32.BringWindowToTop(hwnd)
                        
                        if foreground_thread != current_thread:
                            ctypes.windll.user32.AttachThreadInput(current_thread, foreground_thread, False)
                        
                        ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)  # Alt up
                        
                        # 强制窗口置顶
                        ctypes.windll.user32.SetWindowPos(
                            hwnd, -1,  # HWND_TOPMOST
                            0, 0, 0, 0,
                            0x0001 | 0x0002  # SWP_NOSIZE | SWP_NOMOVE
                        )
                    else:
                        print("🖥️ 桌面模式 - 使用标准激活策略")
                        # 桌面模式：使用标准方法
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                        ctypes.windll.user32.BringWindowToTop(hwnd)
                        ctypes.windll.user32.SetActiveWindow(hwnd)
                        
                except Exception as e:
                    print(f"Windows API 窗口激活失败: {e}")
            
            # 强制激活窗口 (跨平台方法)
            self.root.focus_force()
            
            if is_game_mode:
                # 游戏模式下使用模态抢夺
                self.root.grab_set()  # 模态窗口，抢夺所有输入
                print("启用模态输入抢夺")
            
            # 延迟设置输入框焦点，确保窗口完全加载
            def set_entry_focus():
                try:
                    if self.entry and self.root:
                        self.entry.focus_set()
                        self.entry.icursor(tk.END)  # 将光标移到输入框末尾
                        # 选中所有现有文本（如果有的话）
                        self.entry.select_range(0, tk.END)
                        # print("输入框焦点设置成功")
                except Exception as e:
                    print(f"设置输入框焦点失败: {e}")
            
            # 根据模式调整重试时间
            if is_game_mode:
                # 游戏模式需要更多时间来抢夺焦点
                self.root.after(10, set_entry_focus)
                self.root.after(50, set_entry_focus)
                self.root.after(100, set_entry_focus)
                self.root.after(200, set_entry_focus)
                self.root.after(400, set_entry_focus)
                self.root.after(800, set_entry_focus)
            else:
                # 桌面模式可以更快设置焦点
                self.root.after(10, set_entry_focus)
                self.root.after(50, set_entry_focus)
                self.root.after(150, set_entry_focus)
            
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
        print("尝试显示悬浮输入窗口...")
        
        if self.is_visible:
            # 如果窗口已经显示，重新获得焦点
            print("窗口已存在，重新获取焦点...")
            if self.root and self.entry:
                self.force_focus()
            return
            
        self.is_visible = True
        print("开始创建新的悬浮窗口...")
        
        # 临时禁用全局热键，避免冲突
        if self.hotkey_manager:
            self.hotkey_manager.pause()
            print("全局热键已暂停")
        
        # 在新线程中创建并显示窗口
        def run_window():
            try:
                self.create_window()
                print("悬浮窗口创建完成，正在设置焦点...")
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
                # 释放模态抢夺（如果有的话）
                try:
                    self.root.grab_release()
                    print("释放模态输入抢夺")
                except:
                    pass
                
                # 隐藏窗口前先取消置顶属性，让系统自然恢复焦点
                self.root.attributes('-topmost', False)
                
                # 给系统一点时间来处理焦点转换
                time.sleep(0.1)
                
                self.root.quit()
                self.root.destroy()
                print("悬浮窗已关闭，焦点应已返回游戏")
            except Exception as e:
                print(f"关闭悬浮窗时出错: {e}")
            self.root = None
            self.entry = None
            
    def is_showing(self):
        """检查悬浮窗是否正在显示"""
        return self.is_visible
