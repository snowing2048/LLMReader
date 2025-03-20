from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush, QFont, QTextOption

class ChatBubbleWidget(QWidget):
    """聊天气泡组件，用于显示聊天消息"""
    
    def __init__(self, text, is_user=True, parent=None):
        """初始化聊天气泡组件
        
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
        self.bubble = ChatBubble(self.text, self.is_user)
        
        # 根据消息类型调整布局
        if self.is_user:
            main_layout.addStretch(1)
            main_layout.addWidget(self.bubble)
            main_layout.addWidget(self.avatar_label)
        else:
            main_layout.addWidget(self.avatar_label)
            main_layout.addWidget(self.bubble)
            main_layout.addStretch(1)

class ChatBubble(QWidget):
    """聊天气泡"""
    
    def __init__(self, text, is_user=True, parent=None):
        """初始化聊天气泡
        
        Args:
            text: 消息文本
            is_user: 是否为用户消息
            parent: 父组件
        """
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self.initUI()
    
    def initUI(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 创建文本编辑器，只读模式
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(self.text)
        self.text_edit.setFrameStyle(QTextEdit.NoFrame)
        self.text_edit.setAcceptRichText(True)
        
        # 设置文本编辑器样式
        self.text_edit.setStyleSheet(
            "background-color: transparent; "
            "color: white;"
        )
        
        # 完全禁用滚动条
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 确保滚动条不会显示
        self.text_edit.setStyleSheet(
            "background-color: transparent; "
            "color: white; "
            "QScrollBar {width:0px; height:0px;}"
        )
        
        # 自动调整大小
        self.text_edit.document().setDocumentMargin(0)
        self.text_edit.setMinimumWidth(200)
        self.text_edit.setMaximumWidth(500)
        
        # 设置文本编辑器大小策略，确保完全展开
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        
        # 设置文本编辑器只能选择文本，不能编辑
        self.text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        
        # 启用文本编辑器的自动换行功能
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        # 强制启用自动换行
        self.text_edit.setLineWrapColumnOrWidth(self.text_edit.width())
        
        layout.addWidget(self.text_edit)
        
        # 设置气泡颜色
        self.bubble_color = QColor("#2B5B84") if self.is_user else QColor("#333333")
        
        # 添加文档大小变化的连接，确保气泡大小随内容变化
        self.text_edit.document().contentsChanged.connect(self.adjust_size)
        
        # 初始化时立即调整大小
        self.adjust_size()
    
    def adjust_size(self):
        """根据内容调整气泡大小"""
        # 获取文档实际大小
        doc_size = self.text_edit.document().size()
        # 设置足够的高度以显示所有内容，增加更多额外空间确保完全显示
        height = int(doc_size.height()) + 50
        self.text_edit.setFixedHeight(height)
        
        # 强制文本编辑器重新计算内容大小
        self.text_edit.document().adjustSize()
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
    
    def paintEvent(self, event):
        """绘制气泡背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建气泡路径
        path = QPainterPath()
        rect = self.rect()
        radius = 10
        
        # 绘制圆角矩形 - 将QRect转换为QRectF
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), radius, radius)
        
        # 设置画笔和画刷
        painter.setPen(QPen(self.bubble_color, 1))
        painter.setBrush(QBrush(self.bubble_color))
        
        # 绘制气泡
        painter.drawPath(path)