# miobt.com 动漫资源爬虫

一个简单的 Python 爬虫项目，使用 Scrapling 库抓取 miobt.com 首页动漫资源信息。

## 功能特性

- 抓取动漫资源基本信息（标题、下载链接、文件大小等）
- 自动重试机制（最多3次）
- 请求延迟防止被封
- JSON 格式输出
- 清晰的日志输出
- 验证码检测

## 安装

```bash
# 使用 uv 安装依赖
uv sync
```

## 使用

```bash
# 运行爬虫
uv run main.py
```

## 输出

数据保存在 `output/anime_data.json`，格式如下：

```json
{
  "crawl_time": "2026-04-07T20:30:00",
  "total_count": 20,
  "data": [
    {
      "title": "动漫标题",
      "download_link": "magnet:?xt=urn:...",
      "size": "2.5GB",
      "publish_time": "2026-04-07",
      "seeders": 10,
      "leechers": 5
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
- 目标网站有验证码保护，可能需要额外处理
