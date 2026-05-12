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

```bash
# 启动 TUI 浏览模式
uv run anicatch

# 搜索
uv run anicatch --search "JOJO"

# 搜索并下载第一条结果
uv run anicatch --search "JOJO" --download --index 0

# 测试模式
uv run anicatch --test
```

## 输出

- 搜索/抓取结果：`output/` 目录
- 下载文件：`downloads/` 目录

## 项目结构

```
src/anicatch/
├── __main__.py      # CLI 入口
├── tui.py           # TUI 界面
├── scraper.py       # 爬取与解析
├── downloader.py    # BT 下载
├── seasons.py       # 季度发现
├── models.py        # 数据模型
├── config.py        # 配置常量
└── utils.py         # 工具函数
```

