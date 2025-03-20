from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QFont, QIcon
import os
from core.logger import logger

class SplashScreen(QSplashScreen):
    def __init__(self):
        # 创建一个美观的背景
        self.width = 500
        self.height = 300
        pixmap = self.create_splash_background()
        super().__init__(pixmap)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # 创建进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, self.height - 50, self.width - 100, 20)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2c3e50;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 150);
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2ecc71);
                border-radius: 5px;
            }
        """)
        
        # 状态信息标签
        self.status_label = QLabel(self)
        self.status_label.setGeometry(50, self.height - 80, self.width - 100, 25)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 12px;
            font-weight: bold;
            background-color: transparent;
        """)
        self.status_label.setText("正在启动...")
        
        # 应用名称标签
        self.app_name_label = QLabel(self)
        self.app_name_label.setGeometry(0, 30, self.width, 40)
        self.app_name_label.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 24, QFont.Bold)
        self.app_name_label.setFont(font)
        self.app_name_label.setStyleSheet("""
            color: #2c3e50;
            background-color: transparent;
        """)
        self.app_name_label.setText("文献阅读器")
        
        # 版本信息
        self.version_label = QLabel(self)
        self.version_label.setGeometry(self.width - 100, self.height - 25, 90, 20)
        self.version_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.version_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 10px;
            background-color: transparent;
        """)
        self.version_label.setText("v1.0.0")
        
        logger.info("启动画面初始化完成")
    
    def create_splash_background(self):
        """创建美观的启动画面背景
        
        Returns:
            QPixmap: 背景图像
        """
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height)
        gradient.setColorAt(0, QColor(236, 240, 241))  # 浅灰色
        gradient.setColorAt(1, QColor(189, 195, 199))  # 深灰色
        
        # 绘制圆角矩形背景
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)
        
        # 添加装饰性元素 - 顶部条纹
        painter.setBrush(QColor(52, 152, 219))  # 蓝色
        painter.drawRoundedRect(0, 0, self.width, 15, 5, 5)
        
        # 加载并绘制Logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.svg")
        if os.path.exists(logo_path):
            logo = QPixmap(logo_path)
            logo_size = min(100, self.width // 4)
            scaled_logo = logo.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(self.width // 2 - scaled_logo.width() // 2, 80, scaled_logo)
        
        painter.end()
        return pixmap
    
    def update_progress(self, progress: int, message: str):
        """更新加载进度和状态信息
        
        Args:
            progress: 进度值(0-100)
            message: 状态信息
        """
        # 更新进度条
        self.progress_bar.setValue(progress)
        
        # 更新状态信息
        self.status_label.setText(message)
        
        # 强制重绘以立即显示更新
        self.repaint()
        logger.debug(f"更新加载进度: {progress}%, {message}")