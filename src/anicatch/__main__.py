"""CLI 入口点"""

import argparse
import sys

from loguru import logger

from .config import OUTPUT_DIR, TEST_URL
from .downloader import download_from_json, download_with_libtorrent, get_magnet_link
from .models import CrawlResult
from .scraper import fetch_with_retry, parse_books_data, search_anime
from .tui import run_tui
from .utils import save_to_json, setup_logging


def main_cli() -> None:
    """主入口函数"""
    parser = argparse.ArgumentParser(description="AniCatch - 动漫资源爬虫")
    parser.add_argument(
        "--test", action="store_true", help="测试模式 (books.toscrape.com)"
    )
    parser.add_argument("--search", type=str, metavar="KEYWORD", help="搜索关键词")
    parser.add_argument("--download", action="store_true", help="下载模式")
    parser.add_argument("--index", type=int, default=0, help="下载索引 (默认 0)")
    parser.add_argument("--url", type=str, metavar="URL", help="直接从详情页 URL 下载")

    args = parser.parse_args()

    if args.test:
        _run_test_mode()
    elif args.url:
        _run_download_mode(args.url)
    elif args.search:
        _run_search_mode(args.search, args.download, args.index)
    elif args.download:
        logger.error("--download 需要配合 --search 或 --url 使用")
        sys.exit(1)
    else:
        run_tui()


def _run_test_mode() -> None:
    """测试模式"""
    setup_logging()
    logger.info("测试模式启动...")

    page = fetch_with_retry(TEST_URL)
    items = parse_books_data(page)
    result = CrawlResult.create(items)

    output_file = OUTPUT_DIR / "test_data.json"
    save_to_json(result.model_dump(), output_file)
    logger.info(f"测试完成，共抓取 {len(items)} 条数据")


def _run_download_mode(url: str) -> None:
    """直接从详情页 URL 下载"""
    setup_logging()
    logger.info(f"获取 magnet: {url}")

    magnet = get_magnet_link(url)
    if not magnet:
        logger.error("无法获取 magnet 链接")
        sys.exit(1)

    logger.info(f"Magnet: {magnet[:60]}...")
    success = download_with_libtorrent(magnet)
    if not success:
        sys.exit(1)


def _run_search_mode(keyword: str, download: bool, index: int) -> None:
    """搜索模式"""
    setup_logging()
    logger.info(f"搜索: {keyword}")

    items = search_anime(keyword)
    result = CrawlResult.create(items)

    output_file = OUTPUT_DIR / f"search_{keyword}.json"
    save_to_json(result.model_dump(), output_file)

    # 直接输出结果到 stdout
    print(f"\n共 {len(items)} 条结果:\n")
    for i, item in enumerate(items):
        print(f"[{i}] {item.title}")
        print(
            f"    大小: {item.size} | 时间: {item.publish_time} | 上传: {item.uploader}"
        )
        print(f"    链接: {item.download_link}")
        print()

    if download:
        logger.info(f"开始下载索引 {index} 的资源...")
        success = download_from_json(output_file, index)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main_cli()
