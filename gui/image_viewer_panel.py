from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout, QSplitter,
                             QPushButton, QSlider, QFrame, QGridLayout, QSpacerItem, QSizePolicy,
                             QGraphicsOpacityEffect)
from gui.flow_layout import QFlowLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QPixmap, QImage, QCursor, QMouseEvent, QPainter, QColor, QPen
from core.logger import logger

class ImageViewerPanel(QWidget):
    """PDF图片查看器面板，用于显示PDF中的图片和缩略图预览"""
    
    # 定义信号
    image_changed = pyqtSignal(int)  # 当前图片索引改变时发出信号
    
    def __init__(self):
        super().__init__()
        self.images = []  # 存储当前页面的所有图片数据
        self.current_index = 0  # 当前显示的图片索引
        self.zoom_level = 100  # 缩放级别，默认100%
        self.drag_start_position = None  # 拖拽起始位置
        self.is_dragging = False  # 是否正在拖拽
        self.image_offset = QPoint(0, 0)  # 图片偏移量
        logger.debug("初始化图片查看器面板")
        self.initUI()
    
    def initUI(self):
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建分割器，上半部分显示当前图片，下半部分显示缩略图
        self.splitter = QSplitter(Qt.Vertical)
        
        # 设置分割器样式，添加分隔线
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #CCCCCC;
                border: 1px solid #999999;
                width: 2px;
                height: 2px;
                margin: 1px;
            }
            QSplitter::handle:horizontal {
                width: 4px;
            }
            QSplitter::handle:vertical {
                height: 4px;
            }
        """)
        
        # 上半部分 - 当前图片显示区域
        self.current_image_widget = QWidget()
        current_image_layout = QVBoxLayout(self.current_image_widget)
        current_image_layout.setContentsMargins(0, 0, 0, 0)
        
        # 图片显示区域
        self.current_image_scroll = QScrollArea()
        self.current_image_scroll.setWidgetResizable(True)
        self.current_image_scroll.setAlignment(Qt.AlignCenter)
        self.current_image_scroll.setFrameShape(QFrame.NoFrame)
        
        # 创建图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("无图片")
        self.image_label.setStyleSheet("background-color: transparent;")
        self.current_image_scroll.setWidget(self.image_label)
        
        # 创建左右切换按钮容器
        self.nav_buttons_widget = QWidget(self.current_image_widget)
        self.nav_buttons_widget.setObjectName("navButtons")
        self.nav_buttons_widget.setStyleSheet("#navButtons { background-color: transparent; }")
        nav_buttons_layout = QHBoxLayout(self.nav_buttons_widget)
        nav_buttons_layout.setContentsMargins(10, 0, 10, 0)
        
        # 左切换按钮
        self.prev_button = QPushButton("<")
        self.prev_button.setFixedSize(40, 40)
        self.prev_button.setStyleSheet(
            "QPushButton { background-color: rgba(0, 0, 0, 100); color: white; border-radius: 20px; }"
            "QPushButton:hover { background-color: rgba(0, 0, 0, 150); }"
        )
        self.prev_button.clicked.connect(self.prev_image)
        self.prev_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.prev_button.setVisible(False)  # 初始不可见
        
        # 右切换按钮
        self.next_button = QPushButton(">")
        self.next_button.setFixedSize(40, 40)
        self.next_button.setStyleSheet(
            "QPushButton { background-color: rgba(0, 0, 0, 100); color: white; border-radius: 20px; }"
            "QPushButton:hover { background-color: rgba(0, 0, 0, 150); }"
        )
        self.next_button.clicked.connect(self.next_image)
        self.next_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_button.setVisible(False)  # 初始不可见
        
        # 添加左右按钮到布局
        nav_buttons_layout.addWidget(self.prev_button)
        nav_buttons_layout.addStretch(1)
        nav_buttons_layout.addWidget(self.next_button)
        
        # 设置按钮容器的大小和位置
        self.nav_buttons_widget.setFixedHeight(50)
        
        # 添加图片显示区域到布局
        current_image_layout.addWidget(self.current_image_scroll)
        
        # 添加缩放控制栏
        zoom_control_layout = QHBoxLayout()
        zoom_control_layout.setContentsMargins(5, 0, 5, 5)
        
        # 减小缩放按钮
        self.zoom_out_btn = QPushButton('-')
        self.zoom_out_btn.setFixedWidth(30)
        self.zoom_out_btn.clicked.connect(lambda: self.set_zoom_level(self.zoom_level * 0.9))
        zoom_control_layout.addWidget(self.zoom_out_btn)
        
        # 缩放滑动条
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)  # 最小缩放比例10%
        self.zoom_slider.setMaximum(1000)  # 最大缩放比例1000%
        self.zoom_slider.setValue(100)  # 默认缩放比例100%
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.valueChanged.connect(self.slider_zoom_changed)
        zoom_control_layout.addWidget(self.zoom_slider)
        
        # 增加缩放按钮
        self.zoom_in_btn = QPushButton('+')
        self.zoom_in_btn.setFixedWidth(30)
        self.zoom_in_btn.clicked.connect(lambda: self.set_zoom_level(self.zoom_level * 1.1))
        zoom_control_layout.addWidget(self.zoom_in_btn)
        
        # 显示当前缩放比例的标签
        self.zoom_level_label = QLabel('100%')
        self.zoom_level_label.setFixedWidth(50)
        self.zoom_level_label.setAlignment(Qt.AlignCenter)
        zoom_control_layout.addWidget(self.zoom_level_label)
        
        # 添加自适应页面按钮
        self.fit_screen_btn = QPushButton('[]')
        self.fit_screen_btn.setFixedWidth(30)
        self.fit_screen_btn.setToolTip('自适应页面')
        self.fit_screen_btn.clicked.connect(self.fit_to_screen)
        zoom_control_layout.addWidget(self.fit_screen_btn)
        
        # 添加弹性空间，使控件靠左对齐
        zoom_control_layout.addStretch(1)
        
        # 添加缩放控制栏到布局
        current_image_layout.addLayout(zoom_control_layout)
        
        # 下半部分 - 缩略图预览区域
        self.thumbnails_widget = QWidget()
        # 使用流式布局替代网格布局，更灵活地显示缩略图
        self.thumbnails_layout = QFlowLayout()
        self.thumbnails_layout.setSpacing(5)
        self.thumbnails_layout.setContentsMargins(5, 5, 5, 5)
        self.thumbnails_widget.setLayout(self.thumbnails_layout)
        
        self.thumbnails_scroll = QScrollArea()
        self.thumbnails_scroll.setWidgetResizable(True)
        self.thumbnails_scroll.setWidget(self.thumbnails_widget)
        self.thumbnails_scroll.setMinimumHeight(120)  # 设置缩略图区域的最小高度
        self.thumbnails_scroll.setFrameShape(QFrame.NoFrame)
        
        # 添加到分割器
        self.splitter.addWidget(self.current_image_widget)
        self.splitter.addWidget(self.thumbnails_scroll)
        
        # 从配置中加载分割器的初始大小比例
        from conf.config_manager import ConfigManager
        self.config_manager = ConfigManager()
        self.splitter.setSizes(self.config_manager.image_viewer_splitter_sizes)
        
        # 添加分割器到主布局
        main_layout.addWidget(self.splitter)
        
        # 设置面板的最小宽度
        self.setMinimumWidth(300)
        
        # 安装事件过滤器以处理鼠标移动事件
        self.current_image_widget.installEventFilter(self)
        self.image_label.installEventFilter(self)
    
    def set_images(self, image_data_list):
        """设置要显示的图片列表
        
        Args:
            image_data_list: 图片数据列表，每个元素是图片的二进制数据
        """
        self.images = image_data_list
        self.current_index = 0 if image_data_list else -1
        self.image_offset = QPoint(0, 0)  # 重置图片偏移量
        
        logger.info(f"设置图片列表，共{len(image_data_list) if image_data_list else 0}张图片")
        
        # 清除所有缩略图
        self.clear_thumbnails()
        
        if not image_data_list:
            # 如果没有图片，显示提示信息
            self.image_label.setText("无图片")
            self.image_label.setPixmap(QPixmap())  # 清除图片
            logger.debug("没有图片可显示")
            self.prev_button.setVisible(False)
            self.next_button.setVisible(False)
            self.thumbnails_widget.setStyleSheet("background-color: #f5f5f5;")
            no_image_label = QLabel("当前PDF没有图片")
            no_image_label.setAlignment(Qt.AlignCenter)
            no_image_label.setFixedSize(300, 100)  # 设置固定大小
            self.thumbnails_layout.addWidget(no_image_label)
            return
        
        # 创建所有缩略图（使用流式布局）
        for i, img_data in enumerate(image_data_list):
            thumbnail = self.add_thumbnail(img_data, i)
            if thumbnail:
                self.thumbnails_layout.addWidget(thumbnail)
        
        # 显示第一张图片
        self.show_image(0)
        
        # 更新导航按钮状态
        self.update_nav_buttons()
    
    def clear_thumbnails(self):
        """清除所有缩略图"""
        while self.thumbnails_layout.count():
            item = self.thumbnails_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
    
    def add_thumbnail(self, img_data, index):
        """添加一个缩略图
        
        Args:
            img_data: 图片的二进制数据
            index: 图片在列表中的索引
            
        Returns:
            创建的缩略图标签，如果创建失败则返回None
        """
        img = QImage.fromData(img_data)
        if not img.isNull():
            # 创建缩略图（固定高度为100像素）
            pixmap = QPixmap.fromImage(img)
            thumbnail_height = 100
            thumbnail_width = int(pixmap.width() * thumbnail_height / pixmap.height()) if pixmap.height() > 0 else 100
            scaled_pixmap = pixmap.scaled(
                thumbnail_width, 
                thumbnail_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # 创建缩略图标签
            thumbnail_label = QLabel()
            thumbnail_label.setPixmap(scaled_pixmap)
            thumbnail_label.setAlignment(Qt.AlignCenter)
            thumbnail_label.setFixedSize(thumbnail_width + 10, thumbnail_height + 10)  # 添加一些边距
            thumbnail_label.setStyleSheet("border: 1px solid lightgray; margin: 2px;")
            thumbnail_label.setProperty("index", index)  # 存储图片索引
            thumbnail_label.setCursor(QCursor(Qt.PointingHandCursor))
            
            # 添加鼠标点击事件
            thumbnail_label.mousePressEvent = lambda event, idx=index: self.show_image(idx)
            
            return thumbnail_label
        return None
    
    def show_image(self, index):
        """显示指定索引的图片
        
        Args:
            index: 图片在列表中的索引
        """
        if not self.images or index < 0 or index >= len(self.images):
            return
        
        self.current_index = index
        self.image_offset = QPoint(0, 0)  # 重置图片偏移量
        img_data = self.images[index]
        img = QImage.fromData(img_data)
        
        if not img.isNull():
            # 更新当前图片缓存
            self.current_pixmap = QPixmap.fromImage(img)
            
            # 根据缩放级别调整图片大小
            scaled_pixmap = self.current_pixmap.scaled(
                int(self.current_pixmap.width() * self.zoom_level / 100),
                int(self.current_pixmap.height() * self.zoom_level / 100),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.adjustSize()  # 调整标签大小以适应图片
            
            # 更新缩略图的选中状态
            self.update_thumbnail_selection()
            
            # 更新导航按钮状态
            self.update_nav_buttons()
            
            # 发出图片改变信号
            self.image_changed.emit(index)
    
    def update_thumbnail_selection(self):
        """更新缩略图的选中状态，高亮当前选中的图片缩略图"""
        # 遍历所有缩略图，更新选中状态
        for i in range(self.thumbnails_layout.count()):
            item = self.thumbnails_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel) and widget.property("index") is not None:
                    index = widget.property("index")
                    if index == self.current_index:
                        # 当前选中的缩略图
                        widget.setStyleSheet("border: 2px solid blue; margin: 1px; background-color: rgba(0, 0, 255, 0.1);")
                    else:
                        # 未选中的缩略图
                        widget.setStyleSheet("border: 1px solid lightgray; margin: 2px;")
    
    def update_nav_buttons(self):
        """更新导航按钮的可见性和状态"""
        if not self.images:
            self.prev_button.setVisible(False)
            self.next_button.setVisible(False)
            return
        
        # 如果只有一张图片，隐藏导航按钮
        if len(self.images) <= 1:
            self.prev_button.setVisible(False)
            self.next_button.setVisible(False)
            return
        
        # 显示导航按钮
        self.prev_button.setVisible(True)
        self.next_button.setVisible(True)
        
        # 更新按钮状态
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.images) - 1)
    
    def prev_image(self):
        """显示上一张图片"""
        if self.current_index > 0:
            self.show_image(self.current_index - 1)
    
    def next_image(self):
        """显示下一张图片"""
        if self.current_index < len(self.images) - 1:
            self.show_image(self.current_index + 1)
            
    def fade_in_buttons(self):
        """导航按钮淡入效果"""
        # 先确保按钮可见
        self.nav_buttons_widget.show()
        
        # 创建透明度效果
        opacity_effect_prev = QGraphicsOpacityEffect(self.prev_button)
        opacity_effect_next = QGraphicsOpacityEffect(self.next_button)
        self.prev_button.setGraphicsEffect(opacity_effect_prev)
        self.next_button.setGraphicsEffect(opacity_effect_next)
        
        # 创建动画
        self.fade_in_animation_prev = QPropertyAnimation(opacity_effect_prev, b"opacity")
        self.fade_in_animation_prev.setDuration(300)  # 300毫秒
        self.fade_in_animation_prev.setStartValue(0.0)
        self.fade_in_animation_prev.setEndValue(1.0)
        self.fade_in_animation_prev.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.fade_in_animation_next = QPropertyAnimation(opacity_effect_next, b"opacity")
        self.fade_in_animation_next.setDuration(300)  # 300毫秒
        self.fade_in_animation_next.setStartValue(0.0)
        self.fade_in_animation_next.setEndValue(1.0)
        self.fade_in_animation_next.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 启动动画
        self.fade_in_animation_prev.start()
        self.fade_in_animation_next.start()
    
    def fade_out_buttons(self):
        """导航按钮淡出效果"""
        # 创建透明度效果
        opacity_effect_prev = QGraphicsOpacityEffect(self.prev_button)
        opacity_effect_next = QGraphicsOpacityEffect(self.next_button)
        self.prev_button.setGraphicsEffect(opacity_effect_prev)
        self.next_button.setGraphicsEffect(opacity_effect_next)
        
        # 创建动画
        self.fade_out_animation_prev = QPropertyAnimation(opacity_effect_prev, b"opacity")
        self.fade_out_animation_prev.setDuration(300)  # 300毫秒
        self.fade_out_animation_prev.setStartValue(1.0)
        self.fade_out_animation_prev.setEndValue(0.0)
        self.fade_out_animation_prev.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.fade_out_animation_next = QPropertyAnimation(opacity_effect_next, b"opacity")
        self.fade_out_animation_next.setDuration(300)  # 300毫秒
        self.fade_out_animation_next.setStartValue(1.0)
        self.fade_out_animation_next.setEndValue(0.0)
        self.fade_out_animation_next.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 动画结束后隐藏按钮
        self.fade_out_animation_prev.finished.connect(lambda: self.nav_buttons_widget.hide())
        
        # 启动动画
        self.fade_out_animation_prev.start()
        self.fade_out_animation_next.start()
    
    def set_zoom_level(self, new_level, mouse_pos=None, rel_x=None, rel_y=None):
        """设置缩放级别
        
        Args:
            new_level: 新的缩放级别（百分比，如100表示100%）
            mouse_pos: 鼠标位置，用于以鼠标位置为中心点进行缩放
            rel_x: 鼠标相对于图片的水平位置比例
            rel_y: 鼠标相对于图片的垂直位置比例
        """
        # 限制缩放级别在10%到1000%之间
        new_zoom = max(10, min(1000, new_level))
        
        # 如果缩放级别没有变化，则不进行任何操作
        if abs(self.zoom_level - new_zoom) < 0.1:
            return
        
        # 保存旧的缩放级别和图片尺寸
        old_zoom = self.zoom_level
        old_width = self.image_label.width()
        old_height = self.image_label.height()
        old_offset = self.image_offset
        
        # 更新缩放级别
        self.zoom_level = new_zoom
        
        # 更新缩放滑动条 - 确保传递整数值
        self.zoom_slider.setValue(int(self.zoom_level))
        
        # 更新缩放级别标签
        self.zoom_level_label.setText(f'{int(self.zoom_level)}%')
        
        # 如果当前有图片，重新显示以应用新的缩放级别
        if self.current_index >= 0 and self.current_index < len(self.images):
            # 重新显示图片
            img_data = self.images[self.current_index]
            img = QImage.fromData(img_data)
            
            if not img.isNull():
                # 使用类变量缓存原始图片，避免重复加载
                if not hasattr(self, 'current_pixmap') or self.current_pixmap is None:
                    self.current_pixmap = QPixmap.fromImage(img)
                
                # 根据缩放级别调整图片大小
                scaled_pixmap = self.current_pixmap.scaled(
                    int(self.current_pixmap.width() * self.zoom_level / 100),
                    int(self.current_pixmap.height() * self.zoom_level / 100),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.adjustSize()  # 调整标签大小以适应图片
                
                # 计算新的图片尺寸
                new_width = self.image_label.width()
                new_height = self.image_label.height()
                
                # 如果提供了鼠标位置和相对位置比例，则以鼠标位置为中心点进行缩放
                if mouse_pos is not None and rel_x is not None and rel_y is not None:
                    # 计算缩放比例
                    scale_factor = new_zoom / old_zoom
                    
                    # 计算鼠标在图片上的相对位置（相对于图片左上角的比例）
                    # 这个比例在缩放前后应该保持不变
                    mouse_rel_x = rel_x
                    mouse_rel_y = rel_y
                    
                    # 计算鼠标在图片上的绝对位置（相对于图片左上角的像素）
                    mouse_x_on_image = mouse_rel_x * old_width
                    mouse_y_on_image = mouse_rel_y * old_height
                    
                    # 计算缩放后鼠标在图片上的新位置（像素）
                    new_mouse_x_on_image = mouse_rel_x * new_width
                    new_mouse_y_on_image = mouse_rel_y * new_height
                    
                    # 计算鼠标在窗口中的位置（相对于图片容器左上角）
                    mouse_x_on_window = mouse_pos.x()
                    mouse_y_on_window = mouse_pos.y()
                    
                    # 计算新的偏移量，保持鼠标指向的图片部分不变
                    # 新偏移量 = 鼠标在窗口中的位置 - 鼠标在新图片上的位置
                    new_offset_x = mouse_x_on_window - new_mouse_x_on_image
                    new_offset_y = mouse_y_on_window - new_mouse_y_on_image
                    
                    # 更新图片偏移量，保持鼠标位置不变
                    new_offset = QPoint(int(new_offset_x), int(new_offset_y))
                    self.image_offset = new_offset
                    self.image_label.move(new_offset)
                else:
                    # 如果没有提供鼠标位置，则使用旧的偏移量
                    self.image_offset = old_offset
                    self.image_label.move(old_offset)
    
    def slider_zoom_changed(self, value):
        """缩放滑动条值改变时的处理函数
        
        Args:
            value: 新的缩放级别值
        """
        self.set_zoom_level(value)
    
    def wheelEvent(self, event):
        """处理鼠标滚轮事件
        
        Args:
            event: 鼠标滚轮事件对象
        """
        if event.modifiers() == Qt.ControlModifier:
            # Ctrl+滚轮缩放
            delta = event.angleDelta().y()
            
            # 获取鼠标相对于图片的位置
            mouse_pos = event.pos()
            
            # 获取图片标签相对于视图的位置
            label_pos = self.image_label.pos()
            
            # 计算鼠标相对于图片的位置比例
            # 确保鼠标位置在图片范围内
            rel_x = max(0, min(1, (mouse_pos.x() - label_pos.x()) / self.image_label.width())) if self.image_label.width() > 0 else 0.5
            rel_y = max(0, min(1, (mouse_pos.y() - label_pos.y()) / self.image_label.height())) if self.image_label.height() > 0 else 0.5
            
            # 保存旧的缩放级别
            old_zoom = self.zoom_level
            
            # 计算新的缩放级别
            new_zoom = old_zoom * 1.1 if delta > 0 else old_zoom * 0.9
            
            # 设置新的缩放级别，传递鼠标位置和相对比例，以鼠标位置为中心点进行缩放
            self.set_zoom_level(new_zoom, mouse_pos, rel_x, rel_y)
            
            event.accept()  # 接受事件，防止继续传播
        else:
            # 非Ctrl+滚轮事件，交给父类处理
            super().wheelEvent(event)
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理鼠标事件
        
        Args:
            obj: 事件源对象
            event: 事件对象
            
        Returns:
            是否已处理事件
        """
        # 处理鼠标按下事件，开始拖拽
        if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
            if obj == self.image_label and self.image_label.pixmap() and not self.image_label.pixmap().isNull():
                self.drag_start_position = event.pos()
                self.is_dragging = True
                return True
        
        # 处理鼠标释放事件，结束拖拽
        elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.drag_start_position = None
            return True
        
        # 处理鼠标移动事件，实现拖拽
        elif event.type() == event.MouseMove and self.is_dragging and self.drag_start_position:
            if obj == self.image_label and self.image_label.pixmap() and not self.image_label.pixmap().isNull():
                # 计算拖拽偏移量
                delta = event.pos() - self.drag_start_position
                new_pos = self.image_label.pos() + delta
                
                # 更新图片位置
                self.image_label.move(new_pos)
                self.image_offset = new_pos
                return True
        
        # 处理鼠标滚轮事件，实现缩放
        elif event.type() == event.Wheel:
            if obj == self.image_label or obj == self.current_image_widget:
                if event.modifiers() == Qt.ControlModifier:
                    # Ctrl+滚轮缩放
                    delta = event.angleDelta().y()
                    
                    # 获取鼠标相对于当前视图的位置
                    mouse_pos = event.pos()
                    
                    # 如果是在图片标签上滚动，需要调整鼠标位置
                    if obj == self.image_label:
                        # 鼠标位置已经是相对于图片标签的
                        pass
                    else:
                        # 鼠标位置是相对于父容器的，需要减去图片标签的位置偏移
                        mouse_pos = event.pos() - self.image_label.pos()
                    
                    # 获取图片标签相对于视图的位置
                    label_pos = self.image_label.pos()
                    
                    # 计算鼠标相对于图片的位置比例
                    # 确保鼠标位置在图片范围内
                    rel_x = max(0, min(1, (mouse_pos.x() - (0 if obj == self.image_label else 0)) / self.image_label.width())) if self.image_label.width() > 0 else 0.5
                    rel_y = max(0, min(1, (mouse_pos.y() - (0 if obj == self.image_label else 0)) / self.image_label.height())) if self.image_label.height() > 0 else 0.5
                    
                    # 保存旧的缩放级别
                    old_zoom = self.zoom_level
                    
                    # 计算新的缩放级别
                    new_zoom = old_zoom * 1.1 if delta > 0 else old_zoom * 0.9
                    
                    # 设置新的缩放级别
                    self.set_zoom_level(new_zoom, mouse_pos, rel_x, rel_y)
                    
                    event.accept()  # 接受事件，防止继续传播
                    return True
        
        # 处理鼠标进入事件，显示导航按钮（带淡入效果）
        elif event.type() == event.Enter:
            if obj == self.current_image_widget and len(self.images) > 1:
                self.nav_buttons_widget.raise_()
                # 创建淡入效果
                self.fade_in_buttons()
                return True
        
        # 处理鼠标离开事件，隐藏导航按钮（带淡出效果）
        elif event.type() == event.Leave:
            if obj == self.current_image_widget:
                # 检查鼠标是否真的离开了整个区域
                # 兼容PyQt5不同版本，获取鼠标全局位置
                try:
                    # 首先尝试使用globalPos()
                    if hasattr(event, 'globalPos'):
                        global_pos = event.globalPos()
                    # 然后尝试使用globalPosition()
                    elif hasattr(event, 'globalPosition'):
                        global_pos = event.globalPosition().toPoint()
                    # 如果都不存在，使用QCursor.pos()作为备选方案
                    else:
                        global_pos = QCursor.pos()
                    if not self.current_image_widget.rect().contains(self.current_image_widget.mapFromGlobal(global_pos)):
                        self.fade_out_buttons()
                except Exception as e:
                    print(f"获取鼠标位置失败: {str(e)}")
                    global_pos = QCursor.pos()
                    # 如果发生异常，默认隐藏按钮
                    self.fade_out_buttons()
                return True
                
        # 处理鼠标滚轮事件，切换图片
        elif event.type() == event.Wheel and not event.modifiers() == Qt.ControlModifier:
                # 由于已经添加了wheelEvent方法直接处理Ctrl+滚轮事件
                # 这里只处理非Ctrl+滚轮的图片切换功能
                # 当鼠标在图片查看区域内时
                if obj == self.current_image_widget or obj == self.image_label:
                    delta = event.angleDelta().y()
                    if delta > 0:
                        # 向上滚动，显示上一张图片
                        self.prev_image()
                    else:
                        # 向下滚动，显示下一张图片
                        self.next_image()
                    event.accept()  # 接受事件，防止继续传播
                    return True
        
        return super().eventFilter(obj, event)
    
    def fit_to_screen(self):
        """将图片缩放到适合当前查看区域大小
        使图片完全显示在查看区域内，不需要滚动即可查看整个图片
        """
        if not self.images or self.current_index < 0 or self.current_index >= len(self.images):
            return
        
        # 获取当前图片数据
        img_data = self.images[self.current_index]
        img = QImage.fromData(img_data)
        
        if img.isNull():
            return
        
        # 获取图片原始尺寸
        img_width = img.width()
        img_height = img.height()
        
        # 获取查看区域的尺寸
        view_width = self.current_image_scroll.width() - 20  # 减去滚动条宽度
        view_height = self.current_image_scroll.height() - 20  # 减去滚动条高度
        
        # 计算适合的缩放比例
        width_ratio = view_width / img_width * 100
        height_ratio = view_height / img_height * 100
        
        # 选择较小的比例，确保图片完全显示
        fit_zoom = min(width_ratio, height_ratio)
        
        # 限制缩放比例在允许的范围内
        fit_zoom = max(10, min(1000, fit_zoom))
        
        # 将浮点数转换为整数，确保传递给setValue的是整数类型
        fit_zoom = int(fit_zoom)
        
        # 设置缩放级别
        self.set_zoom_level(fit_zoom)
        
        # 重置图片偏移量，使图片居中显示
        self.image_offset = QPoint(0, 0)
        self.image_label.move(self.image_offset)