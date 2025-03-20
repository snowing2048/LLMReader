from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QScrollArea, QTextBrowser
from PyQt5.QtCore import Qt, QSize, QEvent, QTimer, QRect, QMargins
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush, QFont, QTextOption, QTextDocument, QFontMetrics

class ImprovedChatBubbleWidget(QWidget):
    """改进的聊天气泡组件，用于显示聊天消息"""
    
    def __init__(self, text, is_user=True, parent=None):
        """
        初始化聊天气泡组件
        
        Args:
            text: 消息文本
            is_user: 是否为用户消息，True为用户消息，False为AI消息
            parent: 父组件
        """
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self.initUI()
    
    def initUI(self):
        """初始化UI"""
        # 设置布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        
        # 设置大小策略，允许垂直方向扩展
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        
        # 创建头像标签
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(40, 40)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet(
            "background-color: #444; "
            "border-radius: 20px; "
            "color: white; "
            "font-weight: bold;"
        )
        
        # 设置头像文字
        avatar_text = "用户" if self.is_user else "AI"
        self.avatar_label.setText(avatar_text)
        
        # 创建气泡组件
        self.bubble = ImprovedChatBubble(self.text, self.is_user)
        
        # 根据消息类型调整布局
        if self.is_user:
            main_layout.addStretch(1)
            main_layout.addWidget(self.bubble)
            main_layout.addWidget(self.avatar_label)
        else:
            main_layout.addWidget(self.avatar_label)
            main_layout.addWidget(self.bubble)
            main_layout.addStretch(1)

class ImprovedChatBubble(QWidget):
    """改进的聊天气泡"""
    
    def __init__(self, text, is_user=True, parent=None):
        """
        初始化聊天气泡
        
        Args:
            text: 消息文本
            is_user: 是否为用户消息
            parent: 父组件
        """
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self.doc = QTextDocument()
        self.doc.setHtml(self.text)
        self.initUI()
    
    def initUI(self):
        """初始化UI"""
        # 设置布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 创建文本浏览器，只读模式，支持HTML和链接
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)  # 允许打开外部链接
        self.text_browser.setHtml(self.text)
        self.text_browser.setFrameStyle(QTextBrowser.NoFrame)
        
        # 设置文本浏览器样式
        self.text_browser.setStyleSheet(
            "background-color: transparent; "
            "color: white; "
            "QScrollBar {width:0px; height:0px;}"
        )
        
        # 完全禁用滚动条
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 自动调整大小
        self.text_browser.document().setDocumentMargin(0)
        self.text_browser.setMinimumWidth(200)
        self.text_browser.setMaximumWidth(500)
        
        # 设置文本浏览器大小策略
        self.text_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 启用文本浏览器的自动换行功能
        self.text_browser.setLineWrapMode(QTextBrowser.WidgetWidth)
        self.text_browser.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        
        layout.addWidget(self.text_browser)
        
        # 设置气泡颜色
        self.bubble_color = QColor("#2B5B84") if self.is_user else QColor("#333333")
        
        # 添加文档大小变化的连接，确保气泡大小随内容变化
        self.text_browser.document().contentsChanged.connect(self.adjust_size)
        
        # 初始化时立即调整大小
        QTimer.singleShot(0, self.adjust_size)
    
    def adjust_size(self):
        """根据内容调整气泡大小"""
        # 获取字体度量
        font_metrics = QFontMetrics(self.text_browser.font())
        line_height = font_metrics.lineSpacing()
        
        # 获取实际行数
        line_count = self.text_browser.document().lineCount()
        
        # 计算内容高度（包含边距）
        content_height = line_count * line_height
        
        # 获取文本浏览器的内边距
        margins = self.text_browser.contentsMargins()
        margin_height = margins.top() + margins.bottom()
        
        # 设置最终高度（内容高度+边距+5px余量）
        height = content_height + margin_height + 5
        
        # 设置最小高度保证可视性
        min_height = 30
        self.text_browser.setMinimumHeight(min_height)
        
        # 应用计算高度
        if height > min_height:
            self.text_browser.setFixedHeight(height)
        
        # 强制文本浏览器重新计算内容大小
        self.text_browser.document().adjustSize()
        
        # 更新布局
        self.updateGeometry()
        
        # 确保父组件也更新布局
        parent = self.parent()
        while parent:
            parent.updateGeometry()
            parent = parent.parent()
        
        # 强制更新滚动区域，确保当前气泡可见
        top_level = self.window()
        if hasattr(top_level, 'scroll_area'):
            top_level.scroll_area.ensureWidgetVisible(self)
            # 强制刷新滚动区域
            top_level.scroll_area.update()
    
    def resizeEvent(self, event):
        """大小变化事件"""
        super().resizeEvent(event)
        # 当组件大小变化时，重新调整大小
        QTimer.singleShot(0, self.adjust_size)
    
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        # 当组件显示时，重新调整大小
        QTimer.singleShot(0, self.adjust_size)
    
    def paintEvent(self, event):
        """绘制气泡背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建气泡路径
        path = QPainterPath()
        rect = self.rect()
        radius = 10
        
        # 绘制圆角矩形
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), radius, radius)
        
        # 设置画笔和画刷
        painter.setPen(QPen(self.bubble_color, 1))
        painter.setBrush(QBrush(self.bubble_color))
        
        # 绘制气泡
        painter.drawPath(path)