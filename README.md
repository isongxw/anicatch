# miobt.com 动漫资源爬虫

一个简单的 Python 爬虫项目，使用 Scrapling 库抓取 miobt.com 首页动漫资源信息。

## 功能特性

- 抓取动漫资源基本信息（标题、下载链接、文件大小等）
- 自动重试机制（最多3次）
- 请求延迟防止被封
- JSON 格式输出
- 清晰的日志输出
- 验证码检测
- 支持自定义 Cookies
- 测试模式（使用无验证码网站测试）

## 安装

```bash
# 使用 uv 安装依赖
uv sync
```

## 使用

### 基本用法

```bash
# 运行爬虫（抓取 miobt.com）
uv run main.py

# 测试模式（抓取 books.toscrape.com，无验证码）
uv run main.py --test

# 使用 Cookies 绕过验证码
uv run main.py --cookies "session_id=xxx; user_token=yyy"
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--test` | 使用测试模式，抓取 books.toscrape.com（无验证码） |
| `--cookies "..."` | 传递自定义 Cookies，格式: `name1=value1; name2=value2` |

## 输出

### 正常模式

数据保存在 `output/anime_data.json`

### 测试模式

数据保存在 `output/test_books_data.json`

格式如下：

```json
{
  "crawl_time": "2026-04-07T21:56:35",
  "total_count": 20,
  "data": [
    {
      "title": "书籍标题",
      "download_link": "https://...",
      "size": "£51.77",
      "publish_time": "评分: Five",
      "seeders": 0,
      "leechers": 0
    }
  ]
}
```

## 配置

可在 `main.py` 中修改以下配置：

- `REQUEST_DELAY`: 请求延迟时间（秒）
- `MAX_RETRIES`: 最大重试次数
- `OUTPUT_FILE`: 输出文件路径

## 技术栈

- Python 3.10+
- Scrapling (网页抓取库)
- uv (包管理器)

## 注意事项

- 请遵守网站的使用条款
- 适当设置请求延迟避免被封禁
- 网站结构变化可能导致解析失败，需要调整选择器
- 目标网站有验证码保护，使用 `--cookies` 参数传递验证后的 Cookies
- 使用 `--test` 模式可以测试爬虫功能，无需处理验证码
