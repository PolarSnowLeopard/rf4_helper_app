import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from ui.main_window import MainWindow

def main():
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                            "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()