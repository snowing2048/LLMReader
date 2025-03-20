from PyQt5.QtWidgets import QAction, QInputDialog, QFileDialog, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from core import vars
from core.logger import logger
from gui.settings_dialog import SettingsDialog

class MenuManager:
    """菜单管理器类，负责创建和管理主窗口的菜单"""
    
    def __init__(self, main_window):
        """初始化菜单管理器
        
        Args:
            main_window: 主窗口实例，用于访问主窗口的组件和方法
        """
        self.main_window = main_window
        logger.debug("初始化菜单管理器")
        self.create_menu_bar()
    
    def create_menu_bar(self):
        """创建菜单栏及其所有菜单项"""
        # 创建菜单栏
        menubar = self.main_window.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        open_library_action = QAction('打开文献库', self.main_window)
        open_library_action.triggered.connect(self.open_library)
        file_menu.addAction(open_library_action)
        
        open_file_action = QAction('打开单个文件', self.main_window)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        # 添加重建PDF缓存菜单项
        self.rebuild_cache_action = QAction('重建PDF缓存', self.main_window)
        self.rebuild_cache_action.triggered.connect(self.rebuild_pdf_cache)
        self.rebuild_cache_action.setEnabled(False)  # 默认禁用
        file_menu.addAction(self.rebuild_cache_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self.main_window)
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        copy_action = QAction('复制', self.main_window)
        copy_action.triggered.connect(self.copy_text)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('粘贴', self.main_window)
        paste_action.triggered.connect(self.paste_text)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        settings_action = QAction('设置', self.main_window)
        settings_action.triggered.connect(self.show_settings_dialog)
        edit_menu.addAction(settings_action)
        
        # 查看菜单
        view_menu = menubar.addMenu('查看')
        
        zoom_in_action = QAction('放大', self.main_window)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('缩小', self.main_window)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        view_menu.addSeparator()
        
        reset_layout_action = QAction('还原默认布局', self.main_window)
        reset_layout_action.triggered.connect(self.reset_default_layout)
        view_menu.addAction(reset_layout_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        
        search_action = QAction('搜索文本', self.main_window)
        search_action.triggered.connect(self.search_text)
        tools_menu.addAction(search_action)
        
        translate_action = QAction('翻译选中文本', self.main_window)
        translate_action.triggered.connect(self.translate_text)
        tools_menu.addAction(translate_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self.main_window)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction('使用帮助', self.main_window)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        logger.debug("菜单栏创建完成")
    
    def open_library(self):
        """打开文献库目录"""
        directory = QFileDialog.getExistingDirectory(self.main_window, "选择文献库目录")
        if directory:
            logger.info(f"选择文献库目录: {directory}")
            self.main_window.file_panel.set_root_path(directory)
            # 保存最后打开的文献库路径
            self.main_window.config_manager.last_library_path = directory
    
    def open_file(self):
        """打开单个PDF文件"""
        file_path, _ = QFileDialog.getOpenFileName(self.main_window, "选择PDF文件", "", "PDF文件 (*.pdf)")
        if file_path:
            logger.info(f"选择单个PDF文件: {file_path}")
            result = self.main_window.reader_panel.load_pdf(file_path)
            # 如果PDF加载成功，启用重建缓存菜单项
            if result:
                logger.debug("PDF加载成功，启用重建缓存菜单项")
                self.rebuild_cache_action.setEnabled(True)
            else:
                logger.warning(f"PDF加载失败: {file_path}")
    
    def rebuild_pdf_cache(self):
        """重建当前PDF文件的缓存"""
        # 确认是否要重建缓存
        reply = QMessageBox.question(self.main_window, '确认重建缓存', 
                                    '确定要重建当前PDF文件的缓存吗？这将重新提取PDF内容。',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            logger.info("用户确认重建PDF缓存")
            # 调用PDF管理器的重建缓存方法
            result = self.main_window.reader_panel.pdf_manager.rebuild_cache()
            if result:
                logger.info("PDF缓存重建成功")
                QMessageBox.information(self.main_window, '重建缓存成功', '已成功重建PDF文件的缓存。')
            else:
                logger.error("PDF缓存重建失败")
                QMessageBox.warning(self.main_window, '重建缓存失败', '重建PDF文件缓存失败，请检查日志获取详细信息。')
    
    def copy_text(self):
        """复制选中的文本
        
        根据当前焦点控件执行复制操作
        """
        from PyQt5.QtWidgets import QApplication
        
        # 获取当前焦点控件
        focus_widget = QApplication.focusWidget()
        
        if focus_widget:
            # 检查控件是否有copy方法
            if hasattr(focus_widget, 'copy') and callable(getattr(focus_widget, 'copy')):
                focus_widget.copy()
                logger.debug("复制文本：使用控件的copy方法")
            # 检查是否有selectedText方法（QLineEdit等）
            elif hasattr(focus_widget, 'selectedText') and callable(getattr(focus_widget, 'selectedText')):
                selected_text = focus_widget.selectedText()
                if selected_text:
                    QApplication.clipboard().setText(selected_text)
                    logger.debug(f"复制文本：使用selectedText方法，长度: {len(selected_text)}")
            # 检查是否有textCursor方法（QTextEdit等）
            elif hasattr(focus_widget, 'textCursor') and callable(getattr(focus_widget, 'textCursor')):
                cursor = focus_widget.textCursor()
                if cursor.hasSelection():
                    selected_text = cursor.selectedText()
                    QApplication.clipboard().setText(selected_text)
                    logger.debug(f"复制文本：使用textCursor方法，长度: {len(selected_text)}")
    
    def paste_text(self):
        """粘贴文本
        
        根据当前焦点控件执行粘贴操作
        """
        from PyQt5.QtWidgets import QApplication
        
        # 获取当前焦点控件
        focus_widget = QApplication.focusWidget()
        
        if focus_widget:
            # 检查控件是否有paste方法
            if hasattr(focus_widget, 'paste') and callable(getattr(focus_widget, 'paste')):
                focus_widget.paste()
                logger.debug("粘贴文本：使用控件的paste方法")
            # 检查是否有insertPlainText方法（QTextEdit等）
            elif hasattr(focus_widget, 'insertPlainText') and callable(getattr(focus_widget, 'insertPlainText')):
                text = QApplication.clipboard().text()
                if text:
                    focus_widget.insertPlainText(text)
                    logger.debug(f"粘贴文本：使用insertPlainText方法，长度: {len(text)}")
            # 检查是否有insert方法（QLineEdit等）
            elif hasattr(focus_widget, 'insert') and callable(getattr(focus_widget, 'insert')):
                text = QApplication.clipboard().text()
                if text:
                    focus_widget.insert(text)
                    logger.debug(f"粘贴文本：使用insert方法，长度: {len(text)}")
    
    def set_api_key_dialog(self):
        """设置OpenAI API密钥"""
        key, ok = QInputDialog.getText(self.main_window, '设置API密钥', '请输入OpenAI API密钥:')
        if ok and key:
            logger.info("用户设置了新的API密钥")
            self.main_window.chat_panel.set_api_key(key)
            # 保存API密钥到配置
            self.main_window.config_manager.api_key = key
    
    def zoom_in(self):
        """放大PDF内容"""
        logger.debug("菜单操作：放大PDF内容")
        self.main_window.reader_panel.zoom_in()
        # 保存缩放级别到配置
        self.main_window.config_manager.zoom_level = self.main_window.reader_panel.zoom_level / 100.0
    
    def zoom_out(self):
        """缩小PDF内容"""
        logger.debug("菜单操作：缩小PDF内容")
        self.main_window.reader_panel.zoom_out()
        # 保存缩放级别到配置
        self.main_window.config_manager.zoom_level = self.main_window.reader_panel.zoom_level / 100.0
    
    def reset_default_layout(self):
        """还原默认布局"""
        logger.info("还原默认布局")
        # 设置默认的分割器比例
        default_sizes = [200, 400, 400, 200]  # 左侧文件树、文本阅读区、图片查看区、右侧聊天区的宽度比例
        self.main_window.splitter.setSizes(default_sizes)
        # 保存到配置
        self.main_window.config_manager.splitter_sizes = default_sizes
        
        # 设置图片查看器的默认分割器比例
        default_image_viewer_sizes = [700, 300]  # 上部图片区域和下部缩略图区域的高度比例
        self.main_window.image_viewer_panel.splitter.setSizes(default_image_viewer_sizes)
        # 保存到配置
        self.main_window.config_manager.image_viewer_splitter_sizes = default_image_viewer_sizes
    
    def search_text(self):
        """搜索文本"""
        # 获取搜索文本
        text, ok = QInputDialog.getText(self.main_window, '搜索文本', '请输入要搜索的文本:')
        if ok and text:
            logger.info(f"搜索文本: {text}")
            # 调用PDF管理器的搜索方法
            results = self.main_window.reader_panel.pdf_manager.search_text(text)
            if results:
                logger.info(f"搜索结果数量: {len(results)}")
                # 显示搜索结果
                self.show_search_results(text, results)
            else:
                logger.info("未找到搜索结果")
                QMessageBox.information(self.main_window, '搜索结果', f'未找到匹配文本 "{text}"')
    
    def translate_text(self):
        """翻译选中文本"""
        from PyQt5.QtWidgets import QApplication
        
        # 获取当前焦点控件
        focus_widget = QApplication.focusWidget()
        selected_text = ""
        
        if focus_widget:
            # 检查是否有selectedText方法（QLineEdit等）
            if hasattr(focus_widget, 'selectedText') and callable(getattr(focus_widget, 'selectedText')):
                selected_text = focus_widget.selectedText()
            # 检查是否有textCursor方法（QTextEdit等）
            elif hasattr(focus_widget, 'textCursor') and callable(getattr(focus_widget, 'textCursor')):
                cursor = focus_widget.textCursor()
                if cursor.hasSelection():
                    selected_text = cursor.selectedText()
        
        if selected_text:
            logger.info(f"翻译选中文本，长度: {len(selected_text)}")
            # 这里可以调用翻译API或者发送到聊天面板进行翻译
            # 暂时实现为发送到聊天面板
            if hasattr(self.main_window, 'chat_panel'):
                self.main_window.chat_panel.send_message(f"请翻译以下文本:\n{selected_text}")
                logger.debug("已将选中文本发送到聊天面板进行翻译")
            else:
                logger.warning("无法访问聊天面板，无法发送翻译请求")
                QMessageBox.warning(self.main_window, '翻译失败', '无法访问聊天面板，无法发送翻译请求')
        else:
            logger.info("未选中文本，无法翻译")
            QMessageBox.information(self.main_window, '翻译提示', '请先选择要翻译的文本')
    
    def show_settings_dialog(self):
        """显示设置对话框"""
        logger.info("打开设置对话框")
        dialog = SettingsDialog(self.main_window)
        dialog.exec_()
        logger.debug("设置对话框已关闭")
    
    def show_about(self):
        """显示关于对话框"""
        logger.info("显示关于对话框")
        QMessageBox.about(self.main_window, '关于文献阅读器', 
                         '文献阅读器 v1.0\n\n一个用于阅读和管理学术文献的工具，支持PDF阅读、笔记和AI辅助功能。\n\n© 2023 雪灵工作室')
        logger.debug("关于对话框已关闭")
    
    def show_help(self):
        """显示使用帮助对话框"""
        logger.info("显示使用帮助对话框")
        help_text = (
            "<h3>文献阅读器使用帮助</h3>"
            "<p><b>基本操作：</b></p>"
            "<ul>"
            "<li>打开文献库：通过\"文件\"菜单选择\"打开文献库\"，选择包含PDF文件的目录</li>"
            "<li>打开单个文件：通过\"文件\"菜单选择\"打开单个文件\"，选择要打开的PDF文件</li>"
            "<li>放大/缩小：使用\"查看\"菜单中的\"放大\"和\"缩小\"选项，或使用鼠标滚轮</li>"
            "</ul>"
            "<p><b>文本操作：</b></p>"
            "<ul>"
            "<li>复制文本：选中文本后按Ctrl+C或使用\"编辑\"菜单中的\"复制\"选项</li>"
            "<li>搜索文本：使用\"工具\"菜单中的\"搜索文本\"选项</li>"
            "<li>翻译文本：选中文本后使用\"工具\"菜单中的\"翻译选中文本\"选项</li>"
            "</ul>"
            "<p><b>AI辅助功能：</b></p>"
            "<ul>"
            "<li>设置API密钥：在\"编辑\"菜单中选择\"设置\"，在API设置标签页中设置OpenAI API密钥</li>"
            "<li>发送问题：在右侧聊天面板中输入问题并发送</li>"
            "</ul>"
        )
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("使用帮助")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText("".join(help_text))
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        logger.debug("使用帮助对话框已关闭")
    
    def show_search_results(self, query, results):
        """显示搜索结果
        
        Args:
            query: 搜索文本
            results: 搜索结果列表
        """
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel
        
        logger.info(f"显示搜索结果对话框，查询：\"{query}\"，结果数量：{len(results)}")
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle('搜索结果')
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 添加搜索信息标签
        info_label = QLabel(f'搜索 "{query}" 的结果，共找到{len(results)}个匹配项')
        layout.addWidget(info_label)
        
        # 创建结果列表
        result_list = QListWidget()
        layout.addWidget(result_list)
        
        # 添加结果项
        for i, result in enumerate(results):
            page_num = result.get('page', 0) + 1  # 页码从0开始，显示时加1
            text = result.get('text', '')
            item_text = f'第{page_num}页: {text}'
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, result)  # 存储完整结果数据
            result_list.addItem(item)
        
        logger.debug(f"已添加{len(results)}个搜索结果项到列表中")
        
        # 添加按钮
        button_layout = QHBoxLayout()
        
        goto_btn = QPushButton('跳转到选中位置')
        goto_btn.clicked.connect(lambda: self.goto_search_result(result_list))
        button_layout.addWidget(goto_btn)
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # 显示对话框
        dialog.exec_()
        logger.debug("搜索结果对话框已关闭")