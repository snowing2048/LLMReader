import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from gui.main_window import MainWindow
from gui.splash_screen import SplashScreen
from core.preload_manager import PreloadManager
from core.logger import logger

def main():
    # 记录应用程序启动日志
    logger.info("应用程序启动")
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "logo.svg")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
        logger.info(f"设置应用程序图标: {icon_path}")
    
    # 创建并显示启动画面
    splash = SplashScreen()
    splash.show()
    
    # 创建预加载管理器
    preload_manager = PreloadManager()
    
    # 连接信号
    preload_manager.progress_updated.connect(splash.update_progress)
    
    def on_preload_complete():
        # 创建主窗口
        main_window = MainWindow()
        main_window.show()
        # 关闭启动画面
        splash.finish(main_window)
    
    # 连接预加载完成信号
    preload_manager.preload_completed.connect(on_preload_complete)
    
    # 使用定时器延迟开始预加载，确保启动画面显示
    QTimer.singleShot(100, preload_manager.start_preload)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()