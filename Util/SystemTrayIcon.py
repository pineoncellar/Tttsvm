from pystray import Icon as PystrayIcon, Menu as PystrayMenu, MenuItem as PystrayMenuItem
from PIL import Image
import sys
import threading


class SystemTrayIcon:
    def __init__(self, image_path='./icon.png', cleanup_callback=None):
        self.icon_image = Image.open(image_path)
        self.cleanup_callback = cleanup_callback
        self.menu = PystrayMenu(
            PystrayMenuItem('exit', action=self.on_exit),
        )
        self.icon = None

    def start(self):
        self.icon = PystrayIcon('Tttsvm', self.icon_image,
                                'Tttsvm', self.menu)
        try:
            # 设置为非守护线程，确保程序能正确退出
            self.icon.run(setup=self._setup)
        except KeyboardInterrupt:
            print("SystemTrayIcon 检测到键盘中断")
            self.on_exit()
        except Exception as e:
            print(f"SystemTrayIcon 运行出错: {e}")
            self.on_exit()

    def _setup(self, icon):
        """图标设置完成后的回调"""
        icon.visible = True

    def on_exit(self):
        print('托盘图标 exit 触发')
        try:
            if self.icon:
                self.icon.stop()
        except:
            pass
        
        # 调用清理回调函数
        if self.cleanup_callback:
            # 在新线程中调用清理函数，避免死锁
            cleanup_thread = threading.Thread(target=self.cleanup_callback, daemon=True)
            cleanup_thread.start()
        else:
            sys.exit(0)

    def stop(self):
        """外部调用停止图标"""
        try:
            if self.icon:
                self.icon.stop()
        except:
            pass