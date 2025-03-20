import json
from PyQt5.QtWidgets import (QWidget, QTreeView, QFileDialog, QFileSystemModel,
                             QTabWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QMenu, QAction, QInputDialog)
from PyQt5.QtCore import pyqtSignal, Qt
from pathlib import Path
from conf.config_manager import ConfigManager
from core.logger import logger

class CategoryPanel(QTreeWidget):
    file_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.categories = {}
        logger.debug("初始化分类面板")
        self.load_categories()
        
    def initUI(self):
        self.setHeaderLabel('文献分类')
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        menu = QMenu()
        add_category = QAction('添加分类', self)
        add_category.triggered.connect(self.add_category)
        menu.addAction(add_category)
        
        item = self.itemAt(position)
        if item:
            add_to_category = QAction('添加文献到此分类', self)
            add_to_category.triggered.connect(lambda: self.add_file_to_category(item))
            remove_category = QAction('删除分类', self)
            remove_category.triggered.connect(lambda: self.remove_category(item))
            menu.addAction(add_to_category)
            menu.addAction(remove_category)
        
        menu.exec_(self.mapToGlobal(position))
    
    def add_category(self):
        name, ok = QInputDialog.getText(self, '添加分类', '请输入分类名称：')
        if ok and name:
            if name not in self.categories:
                self.categories[name] = []
                item = QTreeWidgetItem([name])
                self.addTopLevelItem(item)
                self.save_categories()
    
    def add_file_to_category(self, category_item):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, '选择PDF文件', '', 'PDF文件 (*.pdf)')
        if file_path:
            category_name = category_item.text(0)
            if file_path not in self.categories[category_name]:
                self.categories[category_name].append(file_path)
                file_item = QTreeWidgetItem([Path(file_path).name])
                file_item.setToolTip(0, file_path)
                category_item.addChild(file_item)
                self.save_categories()
    
    def remove_category(self, item):
        category_name = item.text(0)
        if category_name in self.categories:
            del self.categories[category_name]
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            self.save_categories()
    
    def save_categories(self):
        categories_file = Path('categories.json')
        try:
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=2)
            logger.info(f"分类信息保存成功，共{len(self.categories)}个分类")
        except Exception as e:
            logger.error(f"保存分类信息失败: {str(e)}")
    
    def load_categories(self):
        categories_file = Path('categories.json')
        if categories_file.exists():
            try:
                with open(categories_file, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
                    logger.info(f"成功加载分类信息，共{len(self.categories)}个分类")
                    for category, files in self.categories.items():
                        category_item = QTreeWidgetItem([category])
                        for file_path in files:
                            file_item = QTreeWidgetItem([Path(file_path).name])
                            file_item.setToolTip(0, file_path)
                            category_item.addChild(file_item)
                        self.addTopLevelItem(category_item)
            except Exception as e:
                logger.error(f"加载分类信息失败: {str(e)}")
                self.categories = {}

class FileTreePanel(QTreeView):
    file_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        logger.debug("初始化文件树面板")
        self.initUI()
    
    def initUI(self):
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        # 只显示PDF文件
        self.model.setNameFilters(['*.pdf'])
        self.model.setNameFilterDisables(False)
        self.setModel(self.model)
        
        # 显示文件系统完整路径，设置根目录为系统根目录
        self.setRootIndex(self.model.index(''))
        
        # 只显示文件名列
        for i in range(1, 4):
            self.hideColumn(i)
        
        self.clicked.connect(self._on_file_clicked)
        
        # 设置上下文菜单策略
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # 如果有上次访问的路径，则定位到该位置
        last_path = self.config_manager.last_folder_path
        if last_path and Path(last_path).exists():
            self.set_root_path(last_path)
    
    def set_root_path(self, path):
        # 设置当前路径，但保持完整的文件系统可见
        try:
            index = self.model.index(path)
            self.setCurrentIndex(index)
            self.scrollTo(index)
            self.expand(index)
            logger.info(f"设置文件树根路径: {path}")
        except Exception as e:
            logger.error(f"设置文件树根路径失败: {path}, 错误: {str(e)}")
    
    def _on_file_clicked(self, index):
        file_path = self.model.filePath(index)
        if file_path.endswith('.pdf'):
            # 保存当前文件夹路径
            self.config_manager.last_folder_path = str(Path(file_path).parent)
            logger.info(f"选择PDF文件: {file_path}")
            self.file_selected.emit(file_path)
    
    def show_context_menu(self, position):
        index = self.indexAt(position)
        if not index.isValid():
            return
            
        file_path = self.model.filePath(index)
        if not file_path.endswith('.pdf'):
            return
            
        menu = QMenu(self)
        
        # 添加到分类选项
        add_to_category_action = QAction('添加到分类', self)
        add_to_category_action.triggered.connect(lambda: self.add_to_category(file_path))
        menu.addAction(add_to_category_action)
        
        # 使用资源管理器打开所在位置选项
        open_in_explorer_action = QAction('使用资源管理器打开所在位置', self)
        open_in_explorer_action.triggered.connect(lambda: self.open_in_explorer(file_path))
        menu.addAction(open_in_explorer_action)
        
        menu.exec_(self.viewport().mapToGlobal(position))
    
    def add_to_category(self, file_path):
        # 获取所有分类
        categories_file = Path('categories.json')
        categories = {}
        if categories_file.exists():
            with open(categories_file, 'r', encoding='utf-8') as f:
                categories = json.load(f)
        
        if not categories:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, '提示', '没有可用的分类，请先在分类面板中创建分类。')
            return
        
        # 显示分类选择对话框
        category_name, ok = QInputDialog.getItem(
            self, '选择分类', '请选择要添加到的分类：', 
            list(categories.keys()), 0, False
        )
        
        if ok and category_name:
            # 将文件添加到选定的分类
            if file_path not in categories[category_name]:
                categories[category_name].append(file_path)
                # 保存分类
                with open(categories_file, 'w', encoding='utf-8') as f:
                    json.dump(categories, f, ensure_ascii=False, indent=2)
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, '成功', f'已将文件添加到分类 {category_name}')
    
    def open_in_explorer(self, file_path):
        # 使用系统资源管理器打开文件所在位置（文件夹）
        import os
        import subprocess
        from core.logger import logger
        
        try:
            # 确保文件路径存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return
                
            # 获取文件所在的文件夹路径
            folder_path = os.path.dirname(file_path)
            # 使用绝对路径，确保路径格式正确
            abs_folder_path = os.path.abspath(folder_path)
            logger.info(f"尝试在资源管理器中打开文件夹: {abs_folder_path}")
            
            # 直接打开文件夹，不使用/select参数
            result = subprocess.run(['explorer', abs_folder_path], 
                                   capture_output=True, text=True, shell=True)
            
            if result.returncode != 0 and result.stderr:
                logger.warning(f"资源管理器命令返回警告: {result.stderr}")
            else:
                logger.info(f"资源管理器命令已成功执行")
                
        except Exception as e:
            logger.error(f"打开资源管理器失败: {str(e)}")
            # 如果出现异常，再次尝试打开文件夹
            try:
                folder_path = os.path.dirname(file_path)
                logger.info(f"尝试使用备用方法打开文件夹: {folder_path}")
                subprocess.run(['explorer', folder_path], shell=True)
            except Exception as e2:
                logger.error(f"打开文件夹也失败: {str(e2)}")
        

class FilePanel(QWidget):
    file_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        logger.debug("初始化文件树面板")
        self.initUI()
        # 加载上次的文件夹路径
        last_path = self.config_manager.last_folder_path
        if last_path and Path(last_path).exists():
            self.set_root_path(last_path)
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 文件树标签页
        self.file_tree = FileTreePanel()
        self.tab_widget.addTab(self.file_tree, '文件树')
        
        # 分类标签页
        self.category_panel = CategoryPanel()
        self.tab_widget.addTab(self.category_panel, '分类')
        
        layout.addWidget(self.tab_widget)
        
        # 连接信号
        self.file_tree.file_selected.connect(self.file_selected.emit)
        self.category_panel.file_selected.connect(self.file_selected.emit)
        self.category_panel.itemDoubleClicked.connect(self._on_category_item_double_clicked)
    
    def _on_category_item_double_clicked(self, item):
        if item.parent():  # 如果是文件项（有父项）
            file_path = item.toolTip(0)
            self.file_selected.emit(file_path)
    
    def set_root_path(self, path):
        self.file_tree.set_root_path(path)