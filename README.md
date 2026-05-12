# AniCatch - 动漫资源爬虫

抓取 miobt.com 动漫资源，支持搜索、浏览、BT 下载。

[English](README.en.md) | 中文

## 致谢

感谢 [miobt.com](https://miobt.com) 提供动漫资源索引。

## 安装

### PyPI（推荐）

```bash
pipx install anicatch        # 推荐：隔离安装
pip install anicatch         # 或标准 pip
uv tool install anicatch     # 或 uv
```

### 直接运行（零安装）

```bash
uvx anicatch --search "JOJO"
```

### 开发安装

```bash
git clone https://github.com/isongxw/anicatch.git
cd anicatch
uv sync
```

## 使用

提供两种模式：

### TUI 模式（人机交互）

```bash
anicatch
```

- 浏览季度新番（左右切换季度、月份）
- 键盘导航查看番剧详情和 magnet 链接
- 支持下载选中的资源

### CLI 模式（自动化 / Agent 调用）

```bash
anicatch --search "JOJO"                                    # 搜索
anicatch --search "JOJO" --download --index 0                # 搜索并下载
anicatch --search "JOJO" --download -o ~/Downloads           # 下载到指定目录
anicatch --download "https://miobt.com/show-xxx.html"        # 直接下载
anicatch --download "URL" -o ~/Downloads                    # 下载到指定目录
anicatch --seasons                                          # 列出所有季度
anicatch --season                                           # 浏览当前季度
anicatch --season 1 --download --index 0                     # 下载指定季度番剧
```

## 输出

- 搜索结果：打印到 stdout，同时保存 `output/` 目录
- 下载文件：`downloads/` 目录

## 项目结构

```
src/anicatch/
├── __main__.py      # CLI/TUI 入口
├── tui.py           # TUI 界面
├── scraper.py       # 爬取与解析
├── downloader.py    # BT 下载
├── seasons.py       # 季度发现
├── models.py        # 数据模型
├── config.py        # 配置常量
└── utils.py         # 工具函数
```
