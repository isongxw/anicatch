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


def setup_logging() -> None:
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )


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

            page = fetcher.get(url)
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
        # 检查是否有验证码
        html_content = page.html_content
        if "captcha" in html_content.lower() or "验证" in html_content:
            logger.warning("检测到验证码页面，可能需要手动处理")
            logger.info("HTML 内容片段: " + html_content[:500])
            return anime_list

        # 使用 Scrapling 的选择器查找动漫条目
        # 尝试多种选择器
        entries = page.css("table tr")

        if not entries:
            # 尝试其他选择器
            entries = page.css(".torrent-item, .item, li[data-id]")

        if not entries:
            # 尝试查找所有带链接的列表项
            entries = page.css("li:has(a)")

        logger.info(f"找到 {len(entries)} 个条目")

        for entry in entries:
            try:
                # 提取标题
                title_elem = entry.css("a").first()
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                if not title or len(title) < 2:  # 过滤太短的标题
                    continue

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


if __name__ == "__main__":
    main()