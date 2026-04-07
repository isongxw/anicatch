# miobt.com 动漫资源爬虫

一个 Python 爬虫项目，抓取 miobt.com 首页动漫资源信息，支持搜索和下载功能。

## 功能特性

- 抓取动漫资源基本信息（标题、下载链接、文件大小等）
- 关键词搜索功能
- 自动绕过验证码
- 自动重试机制（最多3次）
- 请求延迟防止被封
- JSON 格式输出
- 支持 libtorrent 下载 magnet 链接
- 测试模式（使用无验证码网站测试）

## 技术栈

- Python 3.10+
- Scrapling (网页抓取库)
- curl_cffi (HTTP 请求)
- Pydantic (数据验证)
- Loguru (日志)
- libtorrent (BT 下载)
- uv (包管理器)

## 安装

```bash
# 克隆项目
git clone https://github.com/isongxw/anime_scrapy.git
cd anime_scrapy

# 使用 uv 安装依赖
uv sync

# 安装 libtorrent（下载功能需要）
uv add libtorrent
```

## 使用

### 基本用法

```bash
# 抓取首页
uv run anime_scrapy

# 搜索动漫
uv run anime_scrapy --search "海贼王"
uv run anime_scrapy -s "JOJO的奇妙冒险"

# 下载搜索结果的第一条
uv run anime_scrapy --search "JOJO" --download

# 下载第三条结果（索引从0开始）
uv run anime_scrapy --search "海贼王" --download --index 2

# 从已保存的 JSON 文件下载
uv run anime_scrapy --download --file output/search_JOJO.json --index 0

# 指定下载路径
uv run anime_scrapy --search "JOJO" --download --output ~/Downloads

# 测试模式
uv run anime_scrapy --test
```

### 命令行参数

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--search "关键词"` | `-s` | 搜索动漫资源 |
| `--download` | `-d` | 下载资源（需要 libtorrent） |
| `--index N` | `-i` | 下载第 N 条资源（从0开始） |
| `--file path.json` | `-f` | 从 JSON 文件读取并下载 |
| `--output path` | `-o` | 指定下载保存路径 |
| `--test` | | 测试模式 |
| `--cookies "..."` | | 传递自定义 Cookies |

## 输出

### 抓取结果

- 首页：`output/anime_data.json`
- 搜索：`output/search_关键词.json`
- 下载：`downloads/` 目录

### JSON 格式

```json
{
  "crawl_time": "2026-04-07T22:18:54",
  "total_count": 50,
  "data": [
    {
      "title": "【喵萌奶茶屋】JOJO的奇妙冒险...",
      "download_link": "https://miobt.com/show-xxx.html",
      "size": "2.1GB",
      "publish_time": "今天 22:13",
      "seeders": 0,
      "leechers": 0,
      "category": "动画",
      "uploader": "喵萌奶茶屋"
    }
  ]
}
```

## 项目结构

```
src/anime_scrapy/
├── __init__.py      # 包入口
├── __main__.py      # CLI 入口
├── config.py        # 配置常量
├── models.py        # Pydantic 数据模型
├── scraper.py       # 爬取函数
├── downloader.py    # 下载函数
└── utils.py         # 工具函数（loguru 日志）
```

## 注意事项

- 请遵守网站的使用条款
- 适当设置请求延迟避免被封禁
- 下载功能需要安装 libtorrent
- 网站结构变化可能导致解析失败