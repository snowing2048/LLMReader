from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QTextEdit, QPushButton, QFrame, QSizePolicy, QLabel, QTextBrowser
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QTextDocument
from openai import OpenAI
from core.logger import logger
from datetime import datetime

class ChatListPanel(QWidget):
    """列表式聊天面板，用于显示聊天消息"""
    
    def __init__(self):
        super().__init__()
        logger.debug("初始化聊天列表面板")
        self.client = None  # 延迟初始化OpenAI客户端
        self.api_key = None  # 存储API密钥
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 聊天历史区域 - 使用滚动区域和垂直布局
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置滚动区域的最小高度，确保滚动条能够正常显示
        self.scroll_area.setMinimumHeight(300)
        
        # 创建内容容器
        self.chat_container = QWidget()
        self.chat_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setContentsMargins(5, 5, 5, 5)
        
        # 设置滚动区域的内容
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area, 3)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.input_edit = QTextEdit()
        self.input_edit.setStyleSheet(
            "background-color: #333; "
            "color: white; "
            "border-radius: 5px;"
        )
        self.send_btn = QPushButton('发送')
        self.send_btn.setStyleSheet(
            "background-color: #2B5B84; "
            "color: white; "
            "border-radius: 5px; "
            "padding: 5px;"
        )
        input_layout.addWidget(self.input_edit, 4)
        input_layout.addWidget(self.send_btn, 1)
        layout.addLayout(input_layout)
        
        # 连接信号
        self.send_btn.clicked.connect(self.send_message)
        
    def send_message(self):
        question = self.input_edit.toPlainText()
        if not question:
            return

        logger.info(f"发送用户消息，长度: {len(question)}")
        
        # 显示用户消息
        user_message = ChatMessagePanel(question, is_user=True)
        self.chat_layout.addWidget(user_message)
        self.input_edit.clear()
        
        # 滚动到底部
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

        # 检查API密钥是否已设置
        if not self.api_key:
            logger.error("未设置API密钥，无法调用OpenAI API")
            error_message = '错误: 未设置API密钥，请在设置中配置OpenAI API密钥'
            ai_message = ChatMessagePanel(error_message, is_user=False)
            self.chat_layout.addWidget(ai_message)
            return
            
        # 确保客户端已初始化
        if not self.client:
            # 获取主窗口
            main_window = self.window()
            api_url = ''
            
            # 如果可以访问配置管理器，获取AI对话专用URL
            if main_window and hasattr(main_window, 'config_manager'):
                chat_config = main_window.config_manager.chat_llm_config
                api_url = chat_config.get('api_url', '')
            
            # 初始化客户端
            self.client = OpenAI(api_key=self.api_key, base_url=api_url if api_url else None)
            
        # 调用OpenAI API
        try:
            logger.info("开始调用OpenAI API")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}]
            )
            answer = response.choices[0].message.content
            logger.info(f"成功接收到API响应，响应长度: {len(answer)}")
            
            ai_message = ChatMessagePanel(answer, is_user=False)
            self.chat_layout.addWidget(ai_message)
            
            # 滚动到底部
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )
        except Exception as e:
            logger.error(f"调用OpenAI API失败: {str(e)}")
            error_message = f'错误: {str(e)}'
            ai_message = ChatMessagePanel(error_message, is_user=False)
            self.chat_layout.addWidget(ai_message)
            
            # 滚动到底部
            self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            )
            
    def set_api_key(self, key, api_url=None):
        self.api_key = key
        self.api_url = api_url
        # 重置客户端，将在下次发送消息时使用新的API密钥和URL初始化
        self.client = None
        logger.info("已设置OpenAI API密钥和URL")


class ChatMessagePanel(QWidget):
    """聊天消息面板，用于显示单条聊天消息，包含发言人名称和完整显示的消息内容"""
    
    def __init__(self, text, is_user=True, parent=None):
        """
        初始化聊天消息面板
        
        Args:
            text: 消息文本
            is_user: 是否为用户消息，True为用户消息，False为AI消息
            parent: 父组件
        """
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        logger.debug(f"创建{'用户' if is_user else 'AI'}消息面板 - 文本长度: {len(text)}")
        self.initUI()
    
    def initUI(self):
        """初始化UI"""
        # 设置布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(3, 2, 3, 2)  # 减小整体边距
        main_layout.setAlignment(Qt.AlignTop)  # 确保内容顶部对齐
        
        # 设置大小策略，允许垂直方向扩展
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        
        # 创建标题行（显示用户/AI标识）
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignLeft)  # 确保标题左对齐
        header_layout.setContentsMargins(0, 0, 0, 0)  # 减小标题区域边距
        
        # 创建标题标签
        self.title_label = QLabel()
        self.title_label.setStyleSheet(
            "color: #CCCCCC; "
            "font-weight: bold;"
        )
        
        # 设置标题文字
        title_text = "用户" if self.is_user else "AI"
        self.title_label.setText(title_text)
        
        # 添加标题到布局
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)
        
        # 创建内容区域
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)  # 减小内容区域边距
        content_layout.setAlignment(Qt.AlignTop)  # 确保内容顶部对齐
        
        # 使用QTextBrowser替代QTextEdit，更适合只读文本显示
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)  # 允许打开外部链接
        
        # 记录文本内容信息
        text_length = len(self.text)
        line_count = self.text.count('\n') + 1
        logger.debug(f"文本浏览器初始化 - 文本长度: {text_length}, 估计行数: {line_count}")
        
        # 设置文本内容
        self.text_browser.setText(self.text)
        self.text_browser.setFrameStyle(QTextBrowser.NoFrame)
        
        # 设置文本浏览器样式
        self.text_browser.setStyleSheet(
            "background-color: #222222; "
            "color: white; "
            "border-radius: 5px; "
            "padding: 3px; "  # 减小内部填充
            "QScrollBar {width:0px; height:0px;}"
        )
        
        # 设置文本浏览器大小策略
        self.text_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        
        # 设置文本浏览器只能选择文本，不能编辑
        self.text_browser.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        
        # 启用文本浏览器的自动换行功能
        self.text_browser.setLineWrapMode(QTextBrowser.WidgetWidth)
        
        # 完全禁用滚动条
        self.text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置初始最小高度，基于文本行数估算
        initial_height = max(80, line_count * 18 + 10)  # 减小每行高度和边距
        logger.debug(f"设置初始最小高度: {initial_height}")
        self.text_browser.setMinimumHeight(initial_height)
        
        # 添加文本浏览器到布局
        content_layout.addWidget(self.text_browser)
        main_layout.addLayout(content_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #555555; height: 1px; margin: 1px 0px;")  # 减小分隔线边距
        main_layout.addWidget(separator)
        
        # 自动调整文本浏览器高度
        logger.debug("安排初始高度调整")
        QTimer.singleShot(0, self.adjust_text_browser_height)
        self.text_browser.document().contentsChanged.connect(self.adjust_text_browser_height)
        
    def adjust_text_browser_height(self):
        """调整文本浏览器高度以适应内容，确保完全显示所有文本"""
        # 获取文档
        document = self.text_browser.document()
        
        # 获取文档大小
        doc_size = document.size().toSize()
        
        # 获取文本块数量（大致对应行数）
        block_count = document.blockCount()
        
        # 获取文档边距
        margins = self.text_browser.contentsMargins()
        margin_height = margins.top() + margins.bottom()
        
        # 记录文档信息
        logger.debug(f"文档信息 - 大小: {doc_size.width()}x{doc_size.height()}, 文本块数: {block_count}, 边距高度: {margin_height}")
        
        # 检查文档高度是否为0，这可能表示文档尚未完全渲染
        if doc_size.height() <= 0:
            logger.warning(f"文档高度异常: {doc_size.height()}，可能尚未完全渲染，使用文本块数量估算高度")
            # 使用文本块数量估算高度，每个块平均18像素高
            estimated_height = block_count * 18 + margin_height + 4  # 减小额外空间
            logger.debug(f"估算高度 - 文本块数: {block_count}, 每块高度: 18, 边距: {margin_height}, 额外空间: 4, 总计: {estimated_height}")
            required_height = max(80, estimated_height)  # 减小最小高度
        else:
            # 计算文本浏览器所需的高度
            # 基础高度 + 文本块间距 + 额外空间确保完全显示
            required_height = doc_size.height() + (block_count * 1) + margin_height + 4  # 减小块间距和额外空间
            logger.debug(f"高度计算 - 文档高度: {doc_size.height()}, 块间距: {block_count * 1}, 边距: {margin_height}, 额外空间: 4, 总计: {required_height}")
        
        # 获取当前高度
        current_height = self.text_browser.height()
        logger.debug(f"高度调整 - 当前高度: {current_height}, 计算高度: {required_height}, 差值: {required_height - current_height}")
        
        # 设置文本浏览器高度
        self.text_browser.setMinimumHeight(required_height)
        self.text_browser.setFixedHeight(required_height)  # 固定高度，确保完全显示
        
        # 强制更新布局
        self.updateGeometry()
        
        # 确保父组件也更新布局
        parent = self.parent()
        if parent:
            parent.updateGeometry()
            
        # 记录调整后的实际高度
        actual_height = self.text_browser.height()
        logger.debug(f"高度调整完成 - 最终高度: {actual_height}, 是否匹配计算高度: {actual_height == required_height}")
        
        # 如果文档高度为0，安排一个延迟调用以在文档渲染后重新计算高度
        if doc_size.height() <= 0:
            logger.debug("安排延迟调用以在文档渲染后重新计算高度")
            QTimer.singleShot(100, self.adjust_text_browser_height)