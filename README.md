# RF4-Fish-Helper

俄罗斯钓鱼4助手-客户端

## 配置环境

```bash
uv venv
# 激活环境
uv sync
uv pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 打包为exe
```python
pyinstaller RF4-helper.spec
```