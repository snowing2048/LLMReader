from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextBrowser, QScrollArea, QSlider, QInputDialog, QMenu, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from pdf.pdf_manager import PDFManager
from core.logger import logger
import io

class ReaderPanel(QWidget):
    def __init__(self):
        super().__init__()
        logger.debug("初始化阅读器面板")
        self.pdf_manager = PDFManager()
        self.zoom_level = 100  # 默认缩放级别为100%
        self.current_file_md5 = None  # 添加当前文件MD5变量
        self.initUI()
        # 将自身注册为PDF管理器的观察者
        self.pdf_manager.add_observer(self)
        # 初始化文本浏览器的字体大小
        self.update_text_font_size()
        # 添加键盘事件过滤器
        self.installEventFilter(self)
        # 标记是否正在使用Ctrl+滚轮缩放
        self.is_ctrl_zooming = False

    def initUI(self):
        logger.debug("创建阅读器面板UI组件")
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
        
        # 显示当前缩放比例的按钮
        self.zoom_level_btn = QPushButton('100%')
        self.zoom_level_btn.setFixedWidth(60)
        self.zoom_level_btn.clicked.connect(self.set_zoom_level_dialog)
        nav_layout.addWidget(self.zoom_level_btn)
        
        # 添加弹性空间，使控件靠左对齐
        nav_layout.addStretch(1)
        
        layout.addLayout(nav_layout)
        
        # 文本显示区域
        self.text_browser = QTextBrowser()
        # 设置自定义上下文菜单策略
        self.text_browser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_browser.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.text_browser)
        
        # 保留旧的图片布局（用于兼容性）
        self.image_layout = QVBoxLayout()
    
    def update(self, event_type, data=None):
        """观察者模式的更新方法，接收PDF管理器的通知
        
        Args:
            event_type: 事件类型
            data: 事件数据
        """
        if event_type == 'pdf_loaded':
            # 显示元数据
            metadata = data['metadata']
            if metadata:
                meta_text = "\n\n文档信息:\n"
                for key, value in metadata.items():
                    if value:
                        meta_text += f"{key}: {value}\n"
                self.text_browser.append(meta_text)
                
            # 如果是从缓存加载的PDF，直接显示缓存中的文本内容
            if data.get('cached', False) and 'cache_content' in data:
                # 清除之前的内容
                self.text_browser.clear()
                
                # 显示元数据
                if metadata:
                    meta_text = "\n\n文档信息:\n"
                    for key, value in metadata.items():
                        if value:
                            meta_text += f"{key}: {value}\n"
                    self.text_browser.append(meta_text)
                
                # 显示缓存中的文本内容
                self.text_browser.append(data['cache_content'].get('raw_content', ''))
                
                # 获取图片数据并通知主窗口
                self.get_cached_images()
            else:
                # 正常显示所有页面内容
                self.show_all_pages(reload_images=True)
        
        elif event_type == 'zoom_changed':
            # 更新缩放级别显示
            zoom_percent = int(data['zoom_level'] * 100)
            self.zoom_level = zoom_percent
            self.zoom_slider.setValue(zoom_percent)
            self.zoom_level_btn.setText(f'{zoom_percent}%')
            # 只更新文本字体大小，不重新加载图片
            self.update_text_font_size()
    
    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress and event.key() == Qt.Key_Control:
            self.is_ctrl_zooming = True
        elif event.type() == event.KeyRelease and event.key() == Qt.Key_Control:
            self.is_ctrl_zooming = False
            # Ctrl键释放时，将当前缩放级别写入配置文件
            if hasattr(self.window(), 'config_manager'):
                self.window().config_manager.zoom_level = self.zoom_level / 100.0
        return super().eventFilter(obj, event)

    def wheelEvent(self, event):
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
        new_zoom = min(self.zoom_level + 10, 200)  # 最大放大到200%
        logger.debug(f"放大操作：从{self.zoom_level}%到{new_zoom}%")
        self.set_zoom_level(new_zoom / 100.0, save_config)
        # 更新文本浏览器的字体大小
        self.update_text_font_size()
    
    def zoom_out(self, save_config=True):
        new_zoom = max(self.zoom_level - 10, 50)  # 最小缩小到50%
        logger.debug(f"缩小操作：从{self.zoom_level}%到{new_zoom}%")
        self.set_zoom_level(new_zoom / 100.0, save_config)
        # 更新文本浏览器的字体大小
        self.update_text_font_size()
    
    def slider_zoom_changed(self, value):
        logger.debug(f"滑动条缩放：设置为{value}%")
        self.set_zoom_level(value / 100.0, save_config=True)
        # 更新文本浏览器的字体大小
        self.update_text_font_size()
    
    def set_zoom_level(self, zoom_level, save_config=True):
        self.pdf_manager.set_zoom_level(zoom_level)
        # 更新文本浏览器的字体大小
        self.update_text_font_size()
        # 仅在非Ctrl+滚轮缩放时保存配置
        if save_config and not self.is_ctrl_zooming and hasattr(self.window(), 'config_manager'):
            self.window().config_manager.zoom_level = zoom_level
    
    def update_text_font_size(self):
        # 根据缩放级别调整文本浏览器的字体大小
        # 基础字体大小为9点，随缩放级别调整
        base_size = 9
        font = self.text_browser.font()
        font.setPointSize(int(base_size * self.zoom_level / 100.0))
        self.text_browser.setFont(font)
    
    def set_zoom_level_dialog(self):
        zoom, ok = QInputDialog.getInt(self, '设置缩放级别', '请输入缩放百分比 (50-200):', 
                                      self.zoom_level, 50, 200, 10)
        if ok:
            self.set_zoom_level(zoom / 100.0)
            # 更新文本浏览器的字体大小
            self.update_text_font_size()
    
    def show_context_menu(self, position):
        menu = QMenu()
        
        copy_action = QAction('复制', self)
        copy_action.triggered.connect(self.copy_selected_text)
        menu.addAction(copy_action)
        
        translate_action = QAction('翻译选中文本', self)
        translate_action.triggered.connect(self.translate_selected_text)
        menu.addAction(translate_action)
        
        menu.exec_(self.text_browser.mapToGlobal(position))
    
    def copy_selected_text(self):
        # 复制选中的文本
        self.text_browser.copy()
    
    def translate_selected_text(self):
        """翻译选中的文本"""
        from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
        
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
            
            # 使用LLM进行翻译
            from llm.llm_handler import LLMClient
            
            # 获取翻译配置
            translate_config = main_window.config_manager.translate_llm_config
            api_key = translate_config.get('api_key', '') or main_window.config_manager.api_key
            api_url = translate_config.get('api_url', '')
            
            if not api_key:
                QMessageBox.warning(self, '翻译失败', '请先在设置中配置API密钥。')
                return
            
            # 创建LLM客户端
            llm_client = LLMClient(api_key=api_key, api_url=api_url, client_type='translate')
            
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
                from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
                
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
            # 修复了这里的语法错误
            # QMessageBox.warning(self, '翻译失败', '请先在设置中
    
    def load_pdf(self, file_path):
        # 计算新文件的MD5值
        new_pdf_md5 = self.pdf_manager.cache_manager.get_pdf_md5(file_path)
        if not new_pdf_md5:
            logger.error(f"计算PDF文件MD5值失败: {file_path}")
            return False
            
        # 检查是否正在打开相同的文件
        if self.current_file_md5 == new_pdf_md5:
            logger.info(f"文件已经打开，跳过加载: {file_path}")
            return True
            
        # 保存新文件的MD5值
        self.current_file_md5 = new_pdf_md5
        
        # 重置UI状态
        self.text_browser.clear()
        self.clear_images()
        
        logger.info(f"阅读器面板开始加载PDF文件: {file_path}")
        result = self.pdf_manager.load_pdf(file_path)
        
        # 如果PDF加载成功，设置窗口标题为PDF标题 - LLMReader
        if result:
            # 获取PDF元数据
            metadata = self.pdf_manager.pdf_reader.get_metadata()
            # 获取标题，如果没有标题则使用文件名
            title = metadata.get('title', '')
            if not title:
                # 如果元数据中没有标题，使用文件名作为标题
                import os
                title = os.path.basename(file_path)
            
            # 设置主窗口标题
            main_window = self.window()
            if main_window:
                main_window.setWindowTitle(f'{title} - LLMReader')
        else:
            logger.warning(f"阅读器面板加载PDF文件失败: {file_path}")
            self.current_file_md5 = None  # 加载失败时重置MD5值
        
        return result
    
    # 图片处理功能已移至独立的ImageViewerPanel
    
    def clear_images(self):
        """清除图片显示区域，此方法仅用于兼容旧代码"""
        # 通知主窗口中的图片查看器面板清除图片
        main_window = self.window()
        if main_window and hasattr(main_window, 'image_viewer_panel'):
            main_window.image_viewer_panel.set_images([])
    
    def get_cached_images(self):
        """获取缓存中的图片数据，并传递给主窗口中的图片查看器面板"""
        if not self.pdf_manager.pdf_reader.doc or not self.pdf_manager.is_cached:
            return
        
        # 收集所有图片数据
        all_images = []
        
        # 从缓存中读取图片
        import os
        
        # 获取缓存中的图片路径列表
        cache_dir = self.pdf_manager.cache_manager.get_cache_dir(self.pdf_manager.current_pdf_md5)
        img_dir = os.path.join(cache_dir, 'img')
        
        if os.path.exists(img_dir):
            # 按顺序读取图片文件
            img_files = sorted([f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))])
            for img_file in img_files:
                try:
                    # 读取图片文件内容
                    with open(os.path.join(img_dir, img_file), 'rb') as f:
                        img_data = f.read()
                        all_images.append(img_data)
                except Exception as e:
                    print(f"读取缓存图片文件失败: {str(e)}")
        
        # 将所有图片数据传递给主窗口中的图片查看器面板
        main_window = self.window()
        if main_window and hasattr(main_window, 'image_viewer_panel'):
            main_window.image_viewer_panel.set_images(all_images)
        
        return all_images
    
    def show_all_pages(self, reload_images=True):
        """显示PDF的所有页面内容
        
        Args:
            reload_images: 是否重新加载图片，默认为True。缩放操作时应设为False
        """
        if not self.pdf_manager.pdf_reader.doc:
            return
        
        # 清除之前的内容
        self.text_browser.clear()
        
        total_pages = self.pdf_manager.pdf_reader.get_total_pages()
        logger.info(f"显示PDF所有页面内容，总页数: {total_pages}")
        
        try:
            # 只有在需要重新加载图片时才执行图片相关操作
            all_images = []
            
            # 检查是否使用缓存加载的PDF
            if self.pdf_manager.is_cached:
                # 从缓存中读取图片
                import os
                
                # 获取缓存中的图片路径列表
                cache_dir = self.pdf_manager.cache_manager.get_cache_dir(self.pdf_manager.current_pdf_md5)
                
                # 从缓存中读取文本内容并显示
                raw_content_file = os.path.join(cache_dir, 'raw_content.txt')
                if os.path.exists(raw_content_file) and os.path.getsize(raw_content_file) > 0:
                    try:
                        with open(raw_content_file, 'r', encoding='utf-8') as f:
                            self.text_browser.setText(f.read())
                    except Exception as e:
                        logger.error(f"读取缓存文本内容失败: {str(e)}")
                
                # 只有在需要重新加载图片时才执行图片相关操作
                if reload_images:
                    img_dir = os.path.join(cache_dir, 'img')
                    
                    if os.path.exists(img_dir):
                        # 按顺序读取图片文件
                        img_files = sorted([f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))])
                        for img_file in img_files:
                            try:
                                # 读取图片文件内容
                                with open(os.path.join(img_dir, img_file), 'rb') as f:
                                    img_data = f.read()
                                    all_images.append(img_data)
                            except Exception as e:
                                logger.error(f"读取缓存图片文件失败: {str(e)}")
            else:
                # 正常从PDF中提取图片
                # 显示所有页面的内容
                for page_num in range(total_pages):
                    page = self.pdf_manager.pdf_reader.get_page(page_num)
                    if page:
                        # 添加页码标记
                        self.text_browser.append(f"\n--- 第 {page_num + 1} 页 ---\n")
                        
                        # 显示文本内容
                        self.text_browser.append(page.get_text())
                        
                        # 只有在需要重新加载图片时才收集图片数据
                        if reload_images:
                            for img_data in page.images:
                                all_images.append(img_data)
            
            # 只有在需要重新加载图片时才传递图片数据给图片查看器面板
            if reload_images:
                main_window = self.window()
                if main_window and hasattr(main_window, 'image_viewer_panel'):
                    main_window.image_viewer_panel.set_images(all_images)
            
            # 将文本浏览器滚动到顶部
            self.text_browser.moveCursor(self.text_browser.textCursor().Start)
        except Exception as e:
            logger.error(f"显示PDF页面内容时出错: {str(e)}")
            self.text_browser.append(f"\n加载PDF内容时出错: {str(e)}\n")