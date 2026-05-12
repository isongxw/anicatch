"""CLI 入口点"""

import argparse
import sys

from loguru import logger

from .config import OUTPUT_DIR, TARGET_URL
from .downloader import download_from_json, download_with_libtorrent, get_magnet_link
from .models import CrawlResult
from .scraper import fetch_with_retry, search_anime
from .seasons import (
    fetch_season_anime,
    find_current_season_index,
    parse_seasons_from_page,
)
from .tui import run_tui
from .utils import save_to_json, setup_logging


def main_cli() -> None:
    """主入口函数"""
    parser = argparse.ArgumentParser(description="AniCatch - 动漫资源爬虫")
    parser.add_argument("--search", type=str, metavar="KEYWORD", help="搜索关键词")
    parser.add_argument(
        "--download",
        nargs="?",
        const="flag",
        metavar="URL",
        help="下载: 直接指定详情页 URL, 或配合 --search/--season 使用",
    )
    parser.add_argument("--index", type=int, default=0, help="下载索引 (默认 0)")
    parser.add_argument("--seasons", action="store_true", help="列出所有季度")
    parser.add_argument(
        "--season",
        type=int,
        nargs="?",
        const=-1,
        metavar="INDEX",
        help="浏览季度番剧 (默认: 当前季度)",
    )

    args = parser.parse_args()
    _dispatch(args)


def _dispatch(args: argparse.Namespace) -> None:
    """统一分发命令"""
    # 直接指定 URL 下载
    if args.download and args.download != "flag":
        _run_download_url(args.download)
        return

    do_download = args.download == "flag"

    # 搜索
    if args.search:
        _run_search_mode(args.search, do_download, args.index)
        return

    # 季度
    if args.seasons:
        _run_seasons_mode()
    elif args.season is not None:
        _run_season_mode(args.season, do_download, args.index)
    elif do_download:
        logger.error("--download 需要配合 --search / --season 或直接指定 URL")
        sys.exit(1)
    else:
        run_tui()


def _run_download_url(url: str) -> None:
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


def _load_seasons():
    """加载首页并解析季度列表（公共辅助）"""
    page = fetch_with_retry(TARGET_URL)
    seasons = parse_seasons_from_page(page)
    if not seasons:
        logger.error("未找到季度入口")
        sys.exit(1)
    return seasons


def _run_seasons_mode() -> None:
    """列出所有季度"""
    setup_logging()
    logger.info("获取季度列表...")

    seasons = _load_seasons()
    current_idx = find_current_season_index(seasons)

    print(f"\n共 {len(seasons)} 个季度:\n")
    for i, s in enumerate(seasons):
        marker = " ← 当前" if i == current_idx else ""
        print(f"[{i}] {s.name} ({s.year}年{s.season}季){marker}")
        print(f"    URL: {s.url}")
        print()


def _run_season_mode(season_index: int, download: bool, index: int) -> None:
    """浏览季度番剧"""
    setup_logging()
    logger.info("获取季度列表...")

    seasons = _load_seasons()

    if season_index == -1:
        season_index = find_current_season_index(seasons)

    if season_index < 0 or season_index >= len(seasons):
        logger.error(f"季度索引 {season_index} 超出范围 (共 {len(seasons)} 个)")
        sys.exit(1)

    season = seasons[season_index]
    logger.info(f"加载季度: {season.name}")

    items = fetch_season_anime(season.url)

    if not items:
        logger.error("当前季度无数据")
        sys.exit(1)

    print(f"\n{season.name} ({len(items)} 条):\n")
    for i, item in enumerate(items):
        print(f"[{i}] {item.title}")
        print(
            f"    大小: {item.size} | 时间: {item.publish_time} | 上传: {item.uploader}"
        )
        print(f"    链接: {item.download_link}")
        print()

    if download:
        output_file = OUTPUT_DIR / f"season_{season.name}.json"
        result = CrawlResult.create(items)
        save_to_json(result.model_dump(), output_file)
        logger.info(f"开始下载索引 {index} 的资源...")
        success = download_from_json(output_file, index)
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
