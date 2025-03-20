from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QWidget, QLabel, QLineEdit, QPushButton, 
                             QGroupBox, QFormLayout, QDialogButtonBox,
                             QRadioButton, QButtonGroup, QComboBox)
from PyQt5.QtCore import Qt
from core.logger import logger

class SettingsDialog(QDialog):
    """设置对话框，提供应用程序的各种设置选项"""
    
    def __init__(self, parent=None):
        """初始化设置对话框
        
        Args:
            parent: 父窗口实例
        """
        super().__init__(parent)
        logger.debug("初始化设置对话框")
        self.parent = parent
        self.setWindowTitle('设置')
        self.resize(600, 400)  # 设置一个合适的初始大小
        
        # 创建布局
        self.create_layout()
        
        # 加载当前设置
        self.load_settings()
    
    def create_layout(self):
        """创建对话框布局"""
        # 主布局
        main_layout = QHBoxLayout(self)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)  # 标签位于顶部
        
        # 创建各个设置页
        self.create_general_tab()
        self.create_api_tab()
        self.create_display_tab()
        
        # 添加确定和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 垂直布局放置搜索框、标签页和按钮
        layout = QVBoxLayout()
        
        # 添加搜索框
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索设置...')
        self.search_button = QPushButton('搜索')
        self.search_button.clicked.connect(self.search_settings)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        layout.addWidget(self.tab_widget)
        layout.addWidget(button_box)
        
        main_layout.addLayout(layout)
        self.setLayout(main_layout)
        logger.debug("设置对话框布局创建完成")
        
    def search_settings(self):
        """搜索设置项
        
        此方法将在未来实现搜索功能
        """
        # 搜索逻辑将在未来实现
        search_text = self.search_input.text()
        logger.debug(f"搜索设置: {search_text}")
        pass
    
    def create_general_tab(self):
        """创建常规设置标签页"""
        general_tab = QWidget()
        layout = QVBoxLayout(general_tab)
        
        # 文献库设置组
        library_group = QGroupBox('文献库设置')
        library_layout = QFormLayout()
        
        # 这里可以添加文献库相关设置
        # 例如默认文献库路径等
        
        library_group.setLayout(library_layout)
        layout.addWidget(library_group)
        
        # 添加其他常规设置组
        # ...
        
        layout.addStretch(1)  # 添加弹性空间
        general_tab.setLayout(layout)
        
        self.tab_widget.addTab(general_tab, '常规')
        logger.debug("常规设置标签页创建完成")
    
    def create_api_tab(self):
        """创建API设置标签页"""
        api_tab = QWidget()
        layout = QVBoxLayout(api_tab)
        
        # 通用API密钥设置组（向后兼容）
        general_api_group = QGroupBox('通用API设置')
        general_api_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        general_api_layout.addRow('OpenAI API密钥:', self.api_key_input)
        
        general_api_group.setLayout(general_api_layout)
        layout.addWidget(general_api_group)
        
        # 文本整理API设置组
        format_api_group = QGroupBox('文本整理API设置')
        format_api_layout = QFormLayout()
        
        self.format_api_key_input = QLineEdit()
        self.format_api_url_input = QLineEdit()
        format_api_layout.addRow('API密钥:', self.format_api_key_input)
        format_api_layout.addRow('API URL:', self.format_api_url_input)
        
        format_api_group.setLayout(format_api_layout)
        layout.addWidget(format_api_group)
        
        # 翻译API设置组
        translate_api_group = QGroupBox('翻译API设置')
        translate_api_layout = QFormLayout()
        
        self.translate_api_key_input = QLineEdit()
        self.translate_api_url_input = QLineEdit()
        translate_api_layout.addRow('API密钥:', self.translate_api_key_input)
        translate_api_layout.addRow('API URL:', self.translate_api_url_input)
        
        translate_api_group.setLayout(translate_api_layout)
        layout.addWidget(translate_api_group)
        
        # AI对话API设置组
        chat_api_group = QGroupBox('AI对话API设置')
        chat_api_layout = QFormLayout()
        
        self.chat_api_key_input = QLineEdit()
        self.chat_api_url_input = QLineEdit()
        chat_api_layout.addRow('API密钥:', self.chat_api_key_input)
        chat_api_layout.addRow('API URL:', self.chat_api_url_input)
        
        chat_api_group.setLayout(chat_api_layout)
        layout.addWidget(chat_api_group)
        
        layout.addStretch(1)  # 添加弹性空间
        api_tab.setLayout(layout)
        
        self.tab_widget.addTab(api_tab, 'API设置')
        logger.debug("API设置标签页创建完成")
    
    def create_display_tab(self):
        """创建显示设置标签页"""
        display_tab = QWidget()
        layout = QVBoxLayout(display_tab)
        
        # 显示设置组
        display_group = QGroupBox('显示设置')
        display_layout = QVBoxLayout()
        
        # 主题设置
        theme_group = QGroupBox('主题设置')
        theme_layout = QVBoxLayout()
        
        # 创建主题选择的单选按钮组
        self.theme_button_group = QButtonGroup(self)
        
        self.auto_theme_radio = QRadioButton('自动（跟随系统）')
        self.light_theme_radio = QRadioButton('亮色主题')
        self.dark_theme_radio = QRadioButton('暗色主题')
        
        self.theme_button_group.addButton(self.auto_theme_radio)
        self.theme_button_group.addButton(self.light_theme_radio)
        self.theme_button_group.addButton(self.dark_theme_radio)
        
        theme_layout.addWidget(self.auto_theme_radio)
        theme_layout.addWidget(self.light_theme_radio)
        theme_layout.addWidget(self.dark_theme_radio)
        
        theme_group.setLayout(theme_layout)
        display_layout.addWidget(theme_group)
        
        # 字体样式设置
        font_group = QGroupBox('字体样式设置')
        font_layout = QFormLayout()
        
        # 字体系列选择
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(['Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong', 'Arial', 'Times New Roman'])
        self.font_family_combo.currentTextChanged.connect(self.on_font_family_changed)
        font_layout.addRow('字体系列:', self.font_family_combo)
        
        # 字重选择
        self.font_weight_combo = QComboBox()
        self.font_weight_combo.addItems(['正常', '粗体'])
        self.font_weight_combo.currentTextChanged.connect(self.on_font_weight_changed)
        font_layout.addRow('字重:', self.font_weight_combo)
        
        # 字间距选择
        self.letter_spacing_combo = QComboBox()
        self.letter_spacing_combo.addItems(['正常', '宽松', '紧凑'])
        self.letter_spacing_combo.currentTextChanged.connect(self.on_letter_spacing_changed)
        font_layout.addRow('字间距:', self.letter_spacing_combo)
        
        font_group.setLayout(font_layout)
        display_layout.addWidget(font_group)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # 添加其他显示设置组
        # ...
        
        layout.addStretch(1)  # 添加弹性空间
        display_tab.setLayout(layout)
        
        self.tab_widget.addTab(display_tab, '显示')
        logger.debug("显示设置标签页创建完成")
    
    def load_settings(self):
        """从配置加载当前设置"""
        logger.debug("开始加载设置")
        from core.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        
        # 加载主题设置
        current_mode = theme_manager.config_manager.theme_mode
        if current_mode == 'auto':
            self.auto_theme_radio.setChecked(True)
        elif current_mode == 'light':
            self.light_theme_radio.setChecked(True)
        else:
            self.dark_theme_radio.setChecked(True)
            
        # 连接主题切换信号
        self.theme_button_group.buttonClicked.connect(self.on_theme_changed)
        
        # 加载字体样式设置
        if self.parent and hasattr(self.parent, 'config_manager'):
            # 加载字体设置
            self.font_family_combo.setCurrentText(self.parent.config_manager.font_family)
            self.font_weight_combo.setCurrentText('粗体' if self.parent.config_manager.font_weight == 'bold' else '正常')
            letter_spacing_map = {'normal': '正常', 'wide': '宽松', 'narrow': '紧凑'}
            self.letter_spacing_combo.setCurrentText(letter_spacing_map[self.parent.config_manager.letter_spacing])
            
            # 加载API密钥
            if hasattr(self.parent.config_manager, 'api_key'):
                self.api_key_input.setText(self.parent.config_manager.api_key)
                logger.debug("已加载通用API密钥设置")
            
            # 加载三套LLM配置
            # 文本整理配置
            format_config = self.parent.config_manager.format_llm_config
            self.format_api_key_input.setText(format_config.get('api_key', ''))
            self.format_api_url_input.setText(format_config.get('api_url', ''))
            logger.debug("已加载文本整理API设置")
            
            # 翻译配置
            translate_config = self.parent.config_manager.translate_llm_config
            self.translate_api_key_input.setText(translate_config.get('api_key', ''))
            self.translate_api_url_input.setText(translate_config.get('api_url', ''))
            logger.debug("已加载翻译API设置")
            
            # AI对话配置
            chat_config = self.parent.config_manager.chat_llm_config
            self.chat_api_key_input.setText(chat_config.get('api_key', ''))
            self.chat_api_url_input.setText(chat_config.get('api_url', ''))
            logger.debug("已加载AI对话API设置")
        
        logger.debug("设置加载完成")
    
    def on_font_family_changed(self, value):
        """处理字体系列变化"""
        self.parent.config_manager.font_family = value
        self.parent.theme_manager.apply_theme(self.parent.theme_manager.get_current_theme())
    
    def on_font_weight_changed(self, value):
        """处理字重变化"""
        self.parent.config_manager.font_weight = 'bold' if value == '粗体' else 'normal'
        self.parent.theme_manager.apply_theme(self.parent.theme_manager.get_current_theme())
    
    def on_letter_spacing_changed(self, value):
        """处理字间距变化
        
        Args:
            value: 新的字间距值
        """
        logger.debug(f"字间距变化: {value}")
        # 将UI选项转换为配置值
        letter_spacing = {
            '正常': 'normal',
            '宽松': 'wide',
            '紧凑': 'narrow'
        }.get(value, 'normal')
        
        # 更新配置
        self.parent.config_manager.letter_spacing = letter_spacing
        
        # 应用新的主题样式
        self.parent.theme_manager.apply_theme(self.parent.theme_manager.get_current_theme())
        logger.debug(f"应用字间距设置: {letter_spacing}")
    
    def on_theme_changed(self, button):
        """处理主题切换
        
        Args:
            button: 被点击的单选按钮
        """
        if self.parent and hasattr(self.parent, 'theme_manager'):
            # 使用父窗口的theme_manager实例
            if button == self.auto_theme_radio:
                self.parent.theme_manager.set_theme_mode('auto')
            elif button == self.light_theme_radio:
                self.parent.theme_manager.set_theme_mode('light')
            else:
                self.parent.theme_manager.set_theme_mode('dark')
            logger.debug(f"主题已切换到: {self.parent.theme_manager.get_current_theme()}")
        else:
            # 如果没有父窗口，使用单例模式的ThemeManager
            from core.theme_manager import ThemeManager
            theme_manager = ThemeManager()
            
            if button == self.auto_theme_radio:
                theme_manager.set_theme_mode('auto')
            elif button == self.light_theme_radio:
                theme_manager.set_theme_mode('light')
            else:
                theme_manager.set_theme_mode('dark')
            logger.debug(f"主题已切换到: {theme_manager.get_current_theme()}")
    
    def accept(self):
        """点击确定按钮时保存设置"""
        logger.info("保存设置")
        if self.parent and hasattr(self.parent, 'config_manager'):
            # 保存通用API密钥（向后兼容）
            api_key = self.api_key_input.text()
            self.parent.config_manager.api_key = api_key
            logger.debug("已保存通用API密钥设置")
            
            # 保存三套LLM配置
            # 文本整理配置
            format_config = {
                'api_key': self.format_api_key_input.text(),
                'api_url': self.format_api_url_input.text()
            }
            self.parent.config_manager.format_llm_config = format_config
            logger.debug("已保存文本整理API设置")
            
            # 翻译配置
            translate_config = {
                'api_key': self.translate_api_key_input.text(),
                'api_url': self.translate_api_url_input.text()
            }
            self.parent.config_manager.translate_llm_config = translate_config
            logger.debug("已保存翻译API设置")
            
            # AI对话配置
            chat_config = {
                'api_key': self.chat_api_key_input.text(),
                'api_url': self.chat_api_url_input.text()
            }
            self.parent.config_manager.chat_llm_config = chat_config
            logger.debug("已保存AI对话API设置")
            
            # 如果有chat_panel，更新API密钥和URL（使用AI对话配置）
            if hasattr(self.parent, 'chat_panel'):
                chat_api_key = chat_config['api_key'] or api_key  # 优先使用专用配置，如果没有则使用通用配置
                chat_api_url = chat_config['api_url']
                self.parent.chat_panel.set_api_key(chat_api_key, chat_api_url)
                logger.debug("已更新聊天面板的API密钥和URL")
            
            # 保存其他设置
            # ...
        
        logger.info("设置保存完成")
        super().accept()