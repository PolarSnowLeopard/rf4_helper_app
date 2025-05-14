#!/usr/bin/env python3
"""俄罗斯钓鱼4助手应用入口"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.config_loader import config_loader

# 配置日志
def setup_logging():
    log_level = logging.DEBUG if config_loader.get('debug', False) else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("日志系统初始化完成")

def main():
    # 初始化日志
    setup_logging()
    
    # 加载配置
    config = config_loader.get_all()
    logging.info(f"应用程序配置加载完成: {config}")
    
    # 创建应用
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()