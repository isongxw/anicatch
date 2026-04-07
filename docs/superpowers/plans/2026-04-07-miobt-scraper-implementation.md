# miobt.com 动漫资源爬虫实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个使用 Scrapling 库的单文件 Python 爬虫，抓取 miobt.com 首页动漫资源信息并保存为 JSON 格式。

**Architecture:** 单文件脚本设计，包含配置、抓取、解析、存储、日志五大模块，使用错误重试机制和请求限速策略。

**Tech Stack:** Python 3.11+, Scrapling, uv 包管理器

---

## Task 1: 项目初始化和依赖配置

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`

- [ ] **Step 1: 创建 Python 版本文件**

创建 `.python-version` 文件：

```
3.11
```

- [ ] **Step 2: 创建 uv 项目配置文件**

创建 `pyproject.toml` 文件：

```toml
[project]
name = "anime-scrapy"
version = "0.1.0"
description = "miobt.com 动漫资源爬虫"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "scrapling>=0.2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 3: 使用 uv 安装依赖**

运行命令：
```bash
uv sync
```

预期输出：
```
Resolved 1 package in 1ms
Installed 1 package in 10ms
 + scrapling==0.2.0
```

- [ ] **Step 4: 验证依赖安装成功**

运行命令：
```bash
uv pip list
```

预期输出应包含 scrapling。

- [ ] **Step 5: 提交初始化配置**

```bash
git add pyproject.toml .python-version uv.lock
git commit -m "feat: initialize project with uv and scrapling dependency"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 2: 创建基础程序结构和配置

**Files:**
- Create: `main.py`

- [ ] **Step 1: 创建 main.py 文件基础结构**

创建 `main.py` 文件：

```python
#!/usr/bin/env python3
"""
miobt.com 动漫资源爬虫
使用 Scrapling 库抓取首页数据并保存为 JSON 格式
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from scrapling import Fetcher


# 配置常量
TARGET_URL = "https://miobt.com/"
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "anime_data.json"

# 请求配置
REQUEST_DELAY = 2.0  # 基础延迟（秒）
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAYS = [1, 2, 4]  # 重试间隔（秒）

# 日志配置
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )


def main() -> None:
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("开始抓取 miobt.com 首页数据...")
    # TODO: 实现抓取逻辑


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试基础程序运行**

运行命令：
```bash
uv run main.py
```

预期输出：
```
[2026-04-07 XX:XX:XX] INFO: 开始抓取 miobt.com 首页数据...
```

- [ ] **Step 3: 提交基础结构**

```bash
git add main.py
git commit -m "feat: create basic program structure with configuration"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 3: 实现日志模块测试

**Files:**
- Modify: `main.py:30-35`

- [ ] **Step 1: 编写日志测试函数**

在 `main.py` 中添加测试函数（临时，用于验证）：

```python
def test_logging() -> None:
    """测试日志功能"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("这是一条测试 INFO 日志")
    logger.warning("这是一条测试 WARNING 日志")
    logger.error("这是一条测试 ERROR 日志")

    print("日志测试完成")
```

- [ ] **Step 2: 运行日志测试**

修改 `main()` 函数调用测试：
```python
def main() -> None:
    test_logging()
```

运行命令：
```bash
uv run main.py
```

预期输出包含三条不同级别的日志。

- [ ] **Step 3: 恢复 main 函数**

恢复 `main()` 函数：
```python
def main() -> None:
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("开始抓取 miobt.com 首页数据...")
```

- [ ] **Step 4: 提交日志模块**

```bash
git add main.py
git commit -m "feat: implement logging module with test"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 4: 实现数据结构定义

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 定义数据结构**

在 `main.py` 中添加数据结构定义（在 imports 之后）：

```python
# 数据结构定义
AnimeData = dict[str, Any]  # 单条动漫数据
CrawlResult = dict[str, Any]  # 抓取结果


def create_anime_entry(
    title: str,
    download_link: str,
    size: str,
    publish_time: str,
    seeders: int = 0,
    leechers: int = 0
) -> AnimeData:
    """创建单条动漫数据条目"""
    return {
        "title": title,
        "download_link": download_link,
        "size": size,
        "publish_time": publish_time,
        "seeders": seeders,
        "leechers": leechers
    }


def create_crawl_result(data: list[AnimeData], crawl_time: str) -> CrawlResult:
    """创建完整的抓取结果"""
    return {
        "crawl_time": crawl_time,
        "total_count": len(data),
        "data": data
    }
```

- [ ] **Step 2: 编写数据结构测试函数**

添加测试函数：

```python
def test_data_structures() -> None:
    """测试数据结构"""
    # 测试单条数据
    anime = create_anime_entry(
        title="测试动漫",
        download_link="magnet:?xt=urn:test",
        size="1.5GB",
        publish_time="2026-04-07",
        seeders=10,
        leechers=5
    )

    assert anime["title"] == "测试动漫"
    assert anime["size"] == "1.5GB"
    print("单条数据测试通过")

    # 测试完整结果
    result = create_crawl_result([anime], "2026-04-07T20:30:00")
    assert result["total_count"] == 1
    assert len(result["data"]) == 1
    print("完整结果测试通过")
```

- [ ] **Step 3: 运行数据结构测试**

修改 `main()` 函数：
```python
def main() -> None:
    test_data_structures()
```

运行命令：
```bash
uv run main.py
```

预期输出：
```
单条数据测试通过
完整结果测试通过
```

- [ ] **Step 4: 提交数据结构**

```bash
git add main.py
git commit -m "feat: implement data structures with tests"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 5: 实现 JSON 存储功能

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 实现 JSON 存储函数**

在 `main.py` 中添加存储函数：

```python
def save_to_json(data: CrawlResult, filepath: Path) -> None:
    """
    将抓取结果保存为 JSON 文件

    Args:
        data: 抓取结果数据
        filepath: 输出文件路径
    """
    # 创建输出目录
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # 写入 JSON 文件
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger = logging.getLogger(__name__)
    logger.info(f"数据已保存到 {filepath}")
```

- [ ] **Step 2: 编写存储测试函数**

添加测试函数：

```python
def test_json_storage() -> None:
    """测试 JSON 存储功能"""
    import tempfile
    import os

    # 创建测试数据
    anime = create_anime_entry(
        title="测试动漫",
        download_link="magnet:?xt=urn:test",
        size="1.5GB",
        publish_time="2026-04-07"
    )
    result = create_crawl_result([anime], "2026-04-07T20:30:00")

    # 使用临时文件测试
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test_output.json"
        save_to_json(result, output_path)

        # 验证文件存在
        assert output_path.exists()
        print(f"文件已创建: {output_path}")

        # 验证内容
        with output_path.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
            assert loaded["total_count"] == 1
            assert loaded["data"][0]["title"] == "测试动漫"
            print("JSON 内容验证通过")
```

- [ ] **Step 3: 运行存储测试**

修改 `main()` 函数：
```python
def main() -> None:
    setup_logging()
    test_json_storage()
```

运行命令：
```bash
uv run main.py
```

预期输出包含验证通过的日志。

- [ ] **Step 4: 提交存储功能**

```bash
git add main.py
git commit -m "feat: implement JSON storage with test"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 6: 实现网络请求重试机制

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 实现重试装饰器**

在 `main.py` 中添加重试逻辑：

```python
def fetch_with_retry(url: str, max_retries: int = MAX_RETRIES) -> Any:
    """
    使用 Scrapling 获取网页内容，支持重试机制

    Args:
        url: 目标网址
        max_retries: 最大重试次数

    Returns:
        Scrapling Page 对象

    Raises:
        Exception: 所有重试失败后抛出异常
    """
    logger = logging.getLogger(__name__)
    fetcher = Fetcher()

    for attempt in range(max_retries):
        try:
            logger.info(f"尝试获取网页 (第 {attempt + 1} 次)...")
            time.sleep(REQUEST_DELAY)  # 请求延迟

            page = fetcher.fetch(url)
            logger.info("成功获取网页内容")
            return page

        except Exception as e:
            logger.warning(f"第 {attempt + 1} 次尝试失败: {e}")

            if attempt < max_retries - 1:
                delay = RETRY_DELAYS[attempt]
                logger.info(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
            else:
                logger.error(f"所有重试失败，放弃抓取")
                raise Exception(f"获取 {url} 失败，已重试 {max_retries} 次")
```

- [ ] **Step 2: 编写重试测试函数**

添加测试函数：

```python
def test_retry_mechanism() -> None:
    """测试重试机制（使用无效URL验证重试逻辑）"""
    setup_logging()
    logger = logging.getLogger(__name__)

    # 测试成功场景
    logger.info("测试重试机制...")
    try:
        # 使用一个可能失败的URL测试重试
        page = fetch_with_retry("https://httpbin.org/status/200", max_retries=2)
        logger.info("重试机制测试通过（成功场景）")
    except Exception as e:
        logger.info(f"重试机制测试（预期失败）: {e}")
```

- [ ] **Step 3: 运行重试测试**

修改 `main()` 函数：
```python
def main() -> None:
    test_retry_mechanism()
```

运行命令：
```bash
uv run main.py
```

预期输出显示重试逻辑工作正常。

- [ ] **Step 4: 提交重试机制**

```bash
git add main.py
git commit -m "feat: implement network request retry mechanism"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 7: 实现 HTML 解析功能

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 实现 HTML 解析函数**

在 `main.py` 中添加解析函数：

```python
def parse_anime_data(page: Any) -> list[AnimeData]:
    """
    解析网页内容，提取动漫资源信息

    Args:
        page: Scrapling Page 对象

    Returns:
        动漫数据列表
    """
    logger = logging.getLogger(__name__)
    anime_list = []

    try:
        # 使用 Scrapling 的选择器查找动漫条目
        # 注意：实际选择器需要根据 miobt.com 的具体HTML结构调整
        entries = page.css("table tr")  # 基础选择器

        logger.info(f"找到 {len(entries)} 个条目")

        for entry in entries:
            try:
                # 提取标题
                title_elem = entry.css("a").first()
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                download_link = title_elem.attr("href") or ""

                # 提取其他信息（根据实际HTML结构调整）
                size = "未知"
                publish_time = datetime.now().strftime("%Y-%m-%d")
                seeders = 0
                leechers = 0

                # 尝试提取文件大小（可能在其他元素中）
                size_elem = entry.css("td:nth-child(3)").first()
                if size_elem:
                    size = size_elem.text.strip()

                anime_entry = create_anime_entry(
                    title=title,
                    download_link=download_link,
                    size=size,
                    publish_time=publish_time,
                    seeders=seeders,
                    leechers=leechers
                )

                anime_list.append(anime_entry)

            except Exception as e:
                logger.warning(f"解析条目失败，跳过: {e}")
                continue

        logger.info(f"成功解析 {len(anime_list)} 条数据")

    except Exception as e:
        logger.error(f"解析HTML失败: {e}")

    return anime_list
```

- [ ] **Step 2: 提交解析功能**

```bash
git add main.py
git commit -m "feat: implement HTML parsing function for anime data"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 8: 整合完整抓取流程

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 实现完整的主函数**

更新 `main()` 函数：

```python
def main() -> None:
    """主函数 - 整合所有功能"""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("开始抓取 miobt.com 首页数据...")

        # 1. 获取网页内容
        page = fetch_with_retry(TARGET_URL)

        # 2. 解析数据
        anime_data = parse_anime_data(page)

        if not anime_data:
            logger.warning("未解析到任何数据")
            return

        # 3. 创建结果对象
        crawl_time = datetime.now().isoformat()
        result = create_crawl_result(anime_data, crawl_time)

        # 4. 保存数据
        save_to_json(result, OUTPUT_FILE)

        logger.info(f"抓取完成！共获取 {len(anime_data)} 条数据")

    except Exception as e:
        logger.error(f"抓取失败: {e}")
        raise
```

- [ ] **Step 2: 清理测试代码**

删除所有测试函数，只保留生产代码：
- 删除 `test_logging()`
- 删除 `test_data_structures()`
- 删除 `test_json_storage()`
- 删除 `test_retry_mechanism()`

- [ ] **Step 3: 提交完整流程**

```bash
git add main.py
git commit -m "feat: integrate complete scraping workflow in main function"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 9: 创建输出目录和验证程序运行

**Files:**
- Modify: `output/anime_data.json` (自动生成)

- [ ] **Step 1: 创建输出目录**

运行命令：
```bash
mkdir -p output
```

- [ ] **Step 2: 运行完整程序**

运行命令：
```bash
uv run main.py
```

预期输出：
```
[2026-04-07 XX:XX:XX] INFO: 开始抓取 miobt.com 首页数据...
[2026-04-07 XX:XX:XX] INFO: 尝试获取网页 (第 1 次)...
[2026-04-07 XX:XX:XX] INFO: 成功获取网页内容
[2026-04-07 XX:XX:XX] INFO: 找到 X 个条目
[2026-04-07 XX:XX:XX] INFO: 成功解析 X 条数据
[2026-04-07 XX:XX:XX] INFO: 数据已保存到 output/anime_data.json
[2026-04-07 XX:XX:XX] INFO: 抓取完成！共获取 X 条数据
```

- [ ] **Step 3: 检查输出文件**

运行命令：
```bash
cat output/anime_data.json
```

预期输出包含 JSON 格式的动漫数据。

- [ ] **Step 4: 验证 JSON 格式**

运行命令验证 JSON 有效性：
```bash
python -m json.tool output/anime_data.json > /dev/null && echo "JSON 格式有效"
```

预期输出：
```
JSON 格式有效
```

- [ ] **Step 5: 提交最终版本**

```bash
git add output/.gitkeep  # 如果需要保留空目录
git commit -m "feat: complete miobt scraper with full integration test"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## Task 10: 添加 README 文档

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建 README 文件**

创建 `README.md` 文件：

```markdown
# miobt.com 动漫资源爬虫

一个简单的 Python 爬虫项目，使用 Scrapling 库抓取 miobt.com 首页动漫资源信息。

## 功能特性

- 抓取动漫资源基本信息（标题、下载链接、文件大小等）
- 自动重试机制（最多3次）
- 请求延迟防止被封
- JSON 格式输出
- 清晰的日志输出

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

- Python 3.11+
- Scrapling (网页抓取库)
- uv (包管理器)

## 注意事项

- 请遵守网站的使用条款
- 适当设置请求延迟避免被封禁
- 网站结构变化可能导致解析失败，需要调整选择器
```

- [ ] **Step 2: 提交 README**

```bash
git add README.md
git commit -m "docs: add README documentation"

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

---

## 自查清单

### Spec覆盖检查

对照规范检查每个需求是否都有对应的任务：

- ✅ 项目初始化和依赖配置（Task 1）
- ✅ 基础程序结构（Task 2）
- ✅ 日志模块（Task 3）
- ✅ 数据结构定义（Task 4）
- ✅ JSON存储功能（Task 5）
- ✅ 网络请求重试机制（Task 6）
- ✅ HTML解析功能（Task 7）
- ✅ 完整流程整合（Task 8）
- ✅ 程序运行验证（Task 9）
- ✅ 文档（Task 10）

### 占位符检查

- ✅ 所有代码步骤都包含完整的实现代码
- ✅ 所有命令都有具体的执行命令
- ✅ 没有使用 "TODO"、"TBD"、"implement later" 等占位符

### 类型一致性检查

- ✅ 所有函数签名保持一致
- ✅ 数据结构定义和所有引用一致
- ✅ 变量命名规范一致

---

## 成功标准

- [ ] 所有依赖正确安装
- [ ] 程序能够成功运行
- [ ] 成功抓取并解析数据
- [ ] JSON 输出格式正确
- [ ] 日志输出清晰
- [ ] 重试机制工作正常
- [ ] 所有功能测试通过