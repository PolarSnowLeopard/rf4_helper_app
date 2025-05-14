import sys
import os
import json
import base64
import requests
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSplitter, QProgressDialog)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from src.api.client import rf4_api, APIException
# from core.image_processor import ImageProcessor

class ImageProcessThread(QThread):
    """处理图像的线程"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        
    def run(self):
        try:
            # 使用API层处理图片
            result = rf4_api.process_image(self.image_path)
            self.finished.emit(result)
        except APIException as e:
            self.error.emit(e.message)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("俄罗斯钓鱼4助手")
        self.setMinimumSize(1200, 800)  # 调大窗口尺寸
        # self.image_processor = ImageProcessor()  # 添加图像处理器
        self.setup_ui()
        self.process_thread = None
        self.progress_dialog = None
        
    def setup_ui(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 上部分 - 标题区域
        title_layout = QHBoxLayout()
        title_label = QLabel("俄罗斯钓鱼4渔获分析")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # 中部 - 分割区域
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧 - 图片显示区域
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        
        # 上传按钮
        self.upload_btn = QPushButton("上传截图")
        self.upload_btn.setMinimumHeight(40)
        self.upload_btn.clicked.connect(self.upload_image)
        image_layout.addWidget(self.upload_btn)
        
        # 图片显示
        self.image_label = QLabel("请上传游戏截图...")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        self.image_label.setMinimumSize(500, 400)  # 调大图片显示区域
        image_layout.addWidget(self.image_label)
        
        splitter.addWidget(image_widget)
        
        # 右侧 - 结果显示区域
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        results_label = QLabel("渔获分析结果")
        results_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        results_layout.addWidget(results_label)
        
        # 表格显示结果
        self.results_table = QTableWidget(0, 4)  # 修改为4列：新鲜度、鱼类、重量、售价
        self.results_table.setHorizontalHeaderLabels(["新鲜度", "鱼类名称", "重量", "售价"])
        # 设置表格列宽
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        results_layout.addWidget(self.results_table)
        
        splitter.addWidget(results_widget)
        main_layout.addWidget(splitter)
        
        # 底部状态区域
        self.status_label = QLabel("准备就绪")
        main_layout.addWidget(self.status_label)
    
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择截图", "", "图片文件 (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.status_label.setText(f"正在处理图片: {os.path.basename(file_path)}")
            self.display_image(file_path)
            self.process_image(file_path)
    
    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(), 
            self.image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
    
    def display_base64_image(self, base64_data):
        """显示Base64编码的图片"""
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(base64_data))
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(), 
            self.image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
    
    def process_image(self, image_path):
        """调用后端处理图片"""
        # 显示进度对话框
        self.progress_dialog = QProgressDialog("正在处理图片...", "取消", 0, 0, self)
        self.progress_dialog.setWindowTitle("请稍候")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
        
        # 创建并启动处理线程
        self.process_thread = ImageProcessThread(image_path)
        self.process_thread.finished.connect(self.handle_process_result)
        self.process_thread.error.connect(self.handle_process_error)
        self.process_thread.start()
    
    def handle_process_result(self, result):
        """处理API返回的结果"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        # 显示处理后的图片
        if "image" in result:
            self.display_base64_image(result["image"])
        
        # 更新鱼类数据表格
        if "fishes" in result:
            self.update_results_table(result["fishes"])
            
        self.status_label.setText("处理完成")
    
    def handle_process_error(self, error_msg):
        """处理API错误"""
        if self.progress_dialog:
            self.progress_dialog.close()
        self.status_label.setText(f"处理失败: {error_msg}")
    
    def update_results_table(self, fish_data):
        """更新结果表格"""
        self.results_table.setRowCount(0)  # 清空表格
        
        for fish in fish_data:
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            
            # 添加鱼的信息（新鲜度、鱼类名称、重量、售价）
            for col, value in enumerate(fish):
                self.results_table.setItem(row_position, col, QTableWidgetItem(value))