# RF4-Fish-Helper

俄罗斯钓鱼4助手-客户端

## 目录结构
```bash
RF4-Fish-Helper/
├── assets/                  # 图标和资源文件
├── src/                     # 源代码
│   ├── __init__.py
│   ├── main.py              # 入口文件
│   ├── ui/                  # 界面相关代码
│   │   ├── __init__.py
│   │   ├── main_window.py   # 主窗口
│   │   └── widgets/         # 自定义控件
│   ├── core/                # 核心功能
│   │   ├── __init__.py
│   │   └── image_processor.py  # 图像处理逻辑
│   └── utils/               # 工具函数
│       ├── __init__.py
│       └── helpers.py
├── requirements.txt         # 依赖项
├── README.md                # 文档
└── setup.py                 # 打包配置
```