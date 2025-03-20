# views/file_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileSystemModel
from PyQt5.QtCore import Qt, pyqtSignal
from core.logger import logger

class FileView(QWidget):
    file_selected = pyqtSignal(str)
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        logger.info("初始化文件视图")
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建文件系统模型
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        
        # 创建树视图
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setAnimated(False)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        
        # 隐藏不需要的列
        self.tree_view.hideColumn(1)  # 隐藏大小列
        self.tree_view.hideColumn(2)  # 隐藏类型列
        self.tree_view.hideColumn(3)  # 隐藏修改日期列
        
        # 连接信号
        self.tree_view.clicked.connect(self.on_tree_view_clicked)
        
        layout.addWidget(self.tree_view)
    
    def set_controller(self, controller):
        """设置控制器
        
        Args:
            controller: 文件控制器
        """
        self.controller = controller
    
    def set_root_path(self, path):
        """设置根路径
        
        Args:
            path: 根路径
        """
        if path:
            self.model.setRootPath(path)
            self.tree_view.setRootIndex(self.model.index(path))
    
    def on_tree_view_clicked(self, index):
        """处理树视图点击事件
        
        Args:
            index: 索引
        """
        # 获取文件路径
        file_path = self.model.filePath(index)
        
        # 如果是PDF文件，则发送文件选择信号
        if file_path.lower().endswith('.pdf'):
            self.file_selected.emit(file_path)
            
            # 如果控制器存在，则调用控制器方法
            if self.controller:
                self.controller.open_pdf(file_path)