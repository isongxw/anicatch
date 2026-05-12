# AniCatch - 动漫资源爬虫

抓取 miobt.com 动漫资源，支持搜索、浏览、BT 下载。

[English](README.en.md) | 中文

## 致谢

感谢 [miobt.com](https://miobt.com) 提供动漫资源索引。

## 安装

```bash
git clone https://github.com/isongxw/anicatch.git
cd anicatch
uv sync
uv add libtorrent  # 下载功能需要
```

## 使用

提供两种模式：

### TUI 模式（人机交互）

```bash
uv run anicatch
```

- 浏览季度新番（左右切换季度、月份）
- 键盘导航查看番剧详情和 magnet 链接
- 支持下载选中的资源

### CLI 模式（自动化 / Agent 调用）

```bash
uv run anicatch --search "JOJO"                    # 搜索，结果直接打印到终端
uv run anicatch --search "JOJO" --download --index 0  # 搜索并下载
uv run anicatch --url "https://miobt.com/show-xxx.html"  # 直接从详情页下载
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
