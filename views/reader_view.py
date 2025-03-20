# views/reader_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextBrowser, QSlider, QMenu, QAction, QMessageBox, QInputDialog, QDialog, QTextEdit, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor
from core.logger import logger
from core.event_bus import EventBus
from llm.llm_handler import LLMClient

class ReaderView(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.event_bus = EventBus()
        self.zoom_level = 1.0  # 默认缩放级别为100%
        logger.info("初始化阅读器视图")
        self.init_ui()
        
        # 订阅事件
        self.event_bus.subscribe('pdf_model_updated', self._on_pdf_model_updated)
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 添加缩放控制组件
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(2)  # 设置控件之间的间距为2像素
        
        # 减小缩放按钮
        self.zoom_out_btn = QPushButton('-')
        self.zoom_out_btn.setFixedWidth(30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        nav_layout.addWidget(self.zoom_out_btn)
        
        # 缩放滑动条
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(50)  # 最小缩放比例50%
        self.zoom_slider.setMaximum(200)  # 最大缩放比例200%
        self.zoom_slider.setValue(100)  # 默认缩放比例100%
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.valueChanged.connect(self.slider_zoom_changed)
        nav_layout.addWidget(self.zoom_slider)
        
        # 增加缩放按钮
        self.zoom_in_btn = QPushButton('+')
        self.zoom_in_btn.setFixedWidth(30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        nav_layout.addWidget(self.zoom_in_btn)
        
        # 显示当前缩放比例的标签
        self.zoom_level_label = QLabel('100%')
        self.zoom_level_label.setFixedWidth(60)
        nav_layout.addWidget(self.zoom_level_label)
        
        # 添加页面导航按钮
        self.prev_page_btn = QPushButton('上一页')
        self.prev_page_btn.clicked.connect(self.prev_page)
        nav_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel('0/0')
        nav_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton('下一页')
        self.next_page_btn.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_page_btn)
        
        # 添加弹性空间，使控件靠左对齐
        nav_layout.addStretch(1)
        
        layout.addLayout(nav_layout)
        
        # 文本显示区域
        self.text_browser = QTextBrowser()
        # 设置自定义上下文菜单策略
        self.text_browser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_browser.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.text_browser)
        
        # 添加键盘事件过滤器
        self.installEventFilter(self)
        # 标记是否正在使用Ctrl+滚轮缩放
        self.is_ctrl_zooming = False
    
    def set_controller(self, controller):
        """设置控制器
        
        Args:
            controller: 阅读器控制器
        """
        self.controller = controller
    
    def _on_pdf_model_updated(self, data):
        """处理PDF模型更新事件
        
        Args:
            data: 事件数据
        """
        # 更新页码显示
        current_page = data.get('current_page', 0)
        total_pages = data.get('total_pages', 0)
        self.page_label.setText(f'{current_page + 1}/{total_pages}')
        
        # 更新缩放级别
        zoom_level = data.get('zoom_level', 1.0)
        self.zoom_level = zoom_level
        self.zoom_slider.setValue(int(zoom_level * 100))
        self.zoom_level_label.setText(f'{int(zoom_level * 100)}%')
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理键盘事件
        
        Args:
            obj: 事件对象
            event: 事件
            
        Returns:
            bool: 是否处理了事件
        """
        if event.type() == event.KeyPress and event.key() == Qt.Key_Control:
            self.is_ctrl_zooming = True
        elif event.type() == event.KeyRelease and event.key() == Qt.Key_Control:
            self.is_ctrl_zooming = False
            # Ctrl键释放时，将当前缩放级别写入配置文件
            if hasattr(self.window(), 'config_manager'):
                self.window().config_manager.zoom_level = self.zoom_level
        return super().eventFilter(obj, event)
    
    def wheelEvent(self, event):
        """滚轮事件，处理Ctrl+滚轮缩放
        
        Args:
            event: 滚轮事件
        """
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in(save_config=False)
            else:
                self.zoom_out(save_config=False)
            event.accept()
        else:
            event.ignore()
    
    def zoom_in(self, save_config=True):
        """放大
        
        Args:
            save_config: 是否保存配置
        """
        if self.controller:
            new_zoom = min(self.zoom_level + 0.1, 2.0)
            self.controller.set_zoom_level(new_zoom)
            if save_config and not self.is_ctrl_zooming and hasattr(self.window(), 'config_manager'):
                self.window().config_manager.zoom_level = new_zoom
    
    def zoom_out(self, save_config=True):
        """缩小
        
        Args:
            save_config: 是否保存配置
        """
        if self.controller:
            new_zoom = max(self.zoom_level - 0.1, 0.5)
            self.controller.set_zoom_level(new_zoom)
            if save_config and not self.is_ctrl_zooming and hasattr(self.window(), 'config_manager'):
                self.window().config_manager.zoom_level = new_zoom
    
    def slider_zoom_changed(self, value):
        """滑动条缩放级别变化
        
        Args:
            value: 缩放值
        """
        if self.controller:
            new_zoom = value / 100.0
            self.controller.set_zoom_level(new_zoom)
    
    def next_page(self):
        """下一页"""
        if self.controller:
            page_data = self.controller.next_page()
            if page_data and 'text' in page_data:
                self.text_browser.setText(page_data['text'])
    
    def prev_page(self):
        """上一页"""
        if self.controller:
            page_data = self.controller.prev_page()
            if page_data and 'text' in page_data:
                self.text_browser.setText(page_data['text'])
    
    def show_context_menu(self, position):
        """显示上下文菜单
        
        Args:
            position: 鼠标位置
        """
        menu = QMenu()
        
        copy_action = QAction('复制', self)
        copy_action.triggered.connect(self.copy_selected_text)
        menu.addAction(copy_action)
        
        translate_action = QAction('翻译选中文本', self)
        translate_action.triggered.connect(self.translate_selected_text)
        menu.addAction(translate_action)
        
        menu.exec_(self.text_browser.mapToGlobal(position))
    
    def copy_selected_text(self):
        """复制选中的文本"""
        self.text_browser.copy()
    
    def translate_selected_text(self):
        """翻译选中的文本"""
        # 获取选中的文本
        selected_text = self.text_browser.textCursor().selectedText()
        if not selected_text:
            QMessageBox.warning(self, '翻译失败', '请先选择要翻译的文本。')
            return
        
        # 选择目标语言
        languages = ['英语', '中文', '日语', '法语', '德语', '西班牙语', '俄语']
        target_lang, ok = QInputDialog.getItem(self, '选择目标语言', 
                                            '请选择要翻译成的语言:', languages, 0, False)
        if not ok or not target_lang:
            return
        
        # 获取主窗口
        main_window = self.window()
        if not main_window or not hasattr(main_window, 'config_manager'):
            QMessageBox.warning(self, '翻译失败', '无法访问配置管理器。')
            return
        
        try:
            # 构建翻译提示
            prompt = f"请将以下文本翻译成{target_lang}，只返回翻译结果，不要包含原文或解释：\n\n{selected_text}"
            
            # 获取API密钥
            api_key = main_window.config_manager.api_key
            if not api_key:
                QMessageBox.warning(self, '翻译失败', '请先在设置中配置API密钥。')
                return
            
            # 创建LLM客户端
            llm_client = LLMClient(api_key=api_key)
            
            # 显示等待提示
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # 发送翻译请求
            messages = [{"role": "user", "content": prompt}]
            response = llm_client.chat_completion(messages, temperature=0.3)
            
            # 恢复光标
            QApplication.restoreOverrideCursor()
            
            # 提取翻译结果
            if response and 'choices' in response and len(response['choices']) > 0:
                translation = response['choices'][0]['message']['content'].strip()
                
                # 显示翻译结果
                dialog = QDialog(self)
                dialog.setWindowTitle('翻译结果')
                dialog.resize(500, 300)
                
                layout = QVBoxLayout(dialog)
                
                result_text = QTextEdit()
                result_text.setReadOnly(True)
                result_text.setText(translation)
                layout.addWidget(result_text)
                
                copy_btn = QPushButton('复制结果')
                copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(translation))
                layout.addWidget(copy_btn)
                
                dialog.setLayout(layout)
                dialog.exec_()
            else:
                QMessageBox.warning(self, '翻译失败', '无法获取翻译结果，请稍后再试。')
        
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, '翻译失败', f'翻译过程中发生错误: {str(e)}')
            import traceback
            traceback.print_exc()