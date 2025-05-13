import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSplitter)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
# from core.image_processor import ImageProcessor

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("俄罗斯钓鱼4助手")
        self.setMinimumSize(900, 700)
        # self.image_processor = ImageProcessor()  # 添加图像处理器
        self.setup_ui()

    # def process_image(self, image_path):
    #     """调用后端处理图片"""
    #     try:
    #         self.status_label.setText("正在处理图片...")
    #         # 调用图像处理器
    #         result = self.image_processor.process(image_path)
            
    #         if result["success"]:
    #             # 更新结果表格
    #             self.update_results_table(result["fishes"])
                
    #             # 如果有处理后的图片，显示它
    #             if "result_image" in result and os.path.exists(result["result_image"]):
    #                 self.display_image(result["result_image"])
                    
    #             self.status_label.setText("处理完成")
    #         else:
    #             self.status_label.setText(f"处理失败: {result.get('error', '未知错误')}")
            
    #     except Exception as e:
    #         self.status_label.setText(f"处理失败: {str(e)}")
        
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
        self.image_label.setMinimumSize(400, 300)
        image_layout.addWidget(self.image_label)
        
        splitter.addWidget(image_widget)
        
        # 右侧 - 结果显示区域
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        results_label = QLabel("渔获分析结果")
        results_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        results_layout.addWidget(results_label)
        
        # 表格显示结果
        self.results_table = QTableWidget(0, 2)  # 列：鱼类序号，鱼类信息
        self.results_table.setHorizontalHeaderLabels(["序号", "鱼类信息"])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
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
    
    def process_image(self, image_path):
        """调用后端处理图片"""
        try:
            # 这里需要集成您现有的后端逻辑
            # 暂时使用模拟数据
            # TODO: 实际项目中替换为真实API调用
            sample_results = [
                ["大西洋鲑鱼", "4.9kg", "48cm"],
                ["虹鳟鱼", "2.3kg", "37cm"],
                ["北极红点鲑", "1.2kg", "29cm"]
            ]
            
            # 更新表格
            self.update_results_table(sample_results)
            self.status_label.setText("处理完成")
            
        except Exception as e:
            self.status_label.setText(f"处理失败: {str(e)}")
    
    def update_results_table(self, fish_data):
        """更新结果表格"""
        self.results_table.setRowCount(0)  # 清空表格
        
        for i, fish in enumerate(fish_data):
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            
            # 添加序号
            self.results_table.setItem(row_position, 0, QTableWidgetItem(str(i + 1)))
            
            # 添加鱼类信息
            fish_info = ", ".join(fish)
            self.results_table.setItem(row_position, 1, QTableWidgetItem(fish_info))