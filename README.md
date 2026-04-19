# RF4-Fish-Helper

> ⚠️ **本仓库已废弃并归档**
>
> 桌面版不再维护。同等能力（截图渔获识别）已迁移到 Web：[`PolarSnowLeopard/rf4-web`](https://github.com/PolarSnowLeopard/rf4-web)，路由 `/catch/from-image`。
>
> 历史源码作为只读参考保留在新仓库的 `legacy/desktop/` 目录。

---

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