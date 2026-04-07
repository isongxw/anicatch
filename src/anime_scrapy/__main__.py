"""CLI 入口点"""

import sys
import urllib.parse
import argparse
from pathlib import Path

from loguru import logger

from .config import TARGET_URL, OUTPUT_DIR, DOWNLOAD_DIR, OUTPUT_FILE
from .models import CrawlResult
from .scraper import fetch_with_retry, parse_anime_data, parse_books_data
from .downloader import download_from_json
from .utils import setup_logging, save_to_json


def main_cli() -> None:
    """主 CLI 函数"""
    parser = argparse.ArgumentParser(
        description="miobt.com 动漫资源爬虫 - 支持搜索和下载",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 抓取首页
  uv run anime_scrapy

  # 搜索动漫
  uv run anime_scrapy --search "海贼王"

  # 下载搜索结果的第一条
  uv run anime_scrapy --search "JOJO" --download

  # 下载第三条（索引从0开始）
  uv run anime_scrapy --search "海贼王" --download --index 2

  # 从 JSON 文件下载
  uv run anime_scrapy --download --file output/search_JOJO.json --index 0

  # 测试模式
  uv run anime_scrapy --test
        """
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="使用测试模式（抓取 books.toscrape.com，无验证码）"
    )
    parser.add_argument(
        "--search", "-s",
        type=str,
        help="搜索关键词"
    )
    parser.add_argument(
        "--download", "-d",
        action="store_true",
        help="下载资源（需要 libtorrent）"
    )
    parser.add_argument(
        "--index", "-i",
        type=int,
        default=0,
        help="下载资源的索引（从0开始）"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="从 JSON 文件读取数据并下载"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="下载保存路径（默认: downloads/）"
    )
    parser.add_argument(
        "--cookies",
        type=str,
        help="Cookies 字符串"
    )

    args = parser.parse_args()

    setup_logging()

    # 解析 cookies
    cookies_dict = None
    if args.cookies:
        cookies_dict = {}
        for cookie in args.cookies.split(";"):
            if "=" in cookie:
                name, value = cookie.strip().split("=", 1)
                cookies_dict[name] = value

    # 解析保存路径
    save_path = Path(args.output) if args.output else DOWNLOAD_DIR

    # 下载模式
    if args.download:
        if args.file:
            json_file = Path(args.file)
            success = download_from_json(json_file, args.index, save_path)
            sys.exit(0 if success else 1)
        elif args.search:
            logger.info(f"搜索关键词: {args.search}")
            encoded_keyword = urllib.parse.quote(args.search)
            target_url = f"https://miobt.com/search.php?keyword={encoded_keyword}"

            page = fetch_with_retry(target_url, cookies=cookies_dict)
            data = parse_anime_data(page)

            if not data:
                logger.error("未找到任何资源")
                sys.exit(1)

            safe_keyword = "".join(
                c if c.isalnum() or c in ('-', '_') else '_'
                for c in args.search
            )
            json_file = OUTPUT_DIR / f"search_{safe_keyword}.json"
            result = CrawlResult.create(data)
            save_to_json(result.model_dump(), json_file)

            logger.info(f"找到 {len(data)} 条结果:")
            for i, item in enumerate(data[:10]):
                logger.info(f"  [{i}] {item.title[:50]}... ({item.size})")

            if args.index >= len(data):
                logger.error(f"索引 {args.index} 超出范围")
                sys.exit(1)

            success = download_from_json(json_file, args.index, save_path)
            sys.exit(0 if success else 1)
        else:
            page = fetch_with_retry(TARGET_URL, cookies=cookies_dict)
            data = parse_anime_data(page)

            if not data:
                logger.error("未找到任何资源")
                sys.exit(1)

            logger.info(f"首页最新 {len(data)} 条资源:")
            for i, item in enumerate(data[:10]):
                logger.info(f"  [{i}] {item.title[:50]}... ({item.size})")

            success = download_from_json(OUTPUT_FILE, args.index, save_path)
            sys.exit(0 if success else 1)

    # 正常抓取模式
    if args.test:
        target_url = "https://books.toscrape.com/"
        parse_func = parse_books_data
        output_file = OUTPUT_DIR / "test_books_data.json"
        logger.info("使用测试模式...")
    else:
        if args.search:
            encoded_keyword = urllib.parse.quote(args.search)
            target_url = f"https://miobt.com/search.php?keyword={encoded_keyword}"
            safe_keyword = "".join(
                c if c.isalnum() or c in ('-', '_') else '_'
                for c in args.search
            )
            output_file = OUTPUT_DIR / f"search_{safe_keyword}.json"
            logger.info(f"搜索关键词: {args.search}")
        else:
            target_url = TARGET_URL
            output_file = OUTPUT_FILE
            logger.info("开始抓取首页...")
        parse_func = parse_anime_data

    try:
        page = fetch_with_retry(target_url, cookies=cookies_dict)
        data = parse_func(page)

        if not data:
            logger.warning("未解析到任何数据")
            return

        result = CrawlResult.create(data)
        save_to_json(result.model_dump(), output_file)

        logger.success(f"抓取完成！共获取 {len(data)} 条数据")

    except Exception as e:
        logger.error(f"抓取失败: {e}")
        raise


if __name__ == "__main__":
    main_cli()