"""动漫资源爬虫包"""

from .models import AnimeItem, CrawlResult
from .config import (
    TARGET_URL,
    TEST_URL,
    OUTPUT_DIR,
    DOWNLOAD_DIR,
)
from .scraper import fetch_with_retry, parse_anime_data, parse_books_data
from .downloader import get_magnet_link, download_with_libtorrent, download_from_json
from .utils import setup_logging, save_to_json

__all__ = [
    'AnimeItem',
    'CrawlResult',
    'TARGET_URL',
    'TEST_URL',
    'OUTPUT_DIR',
    'DOWNLOAD_DIR',
    'fetch_with_retry',
    'parse_anime_data',
    'parse_books_data',
    'get_magnet_link',
    'download_with_libtorrent',
    'download_from_json',
    'setup_logging',
    'save_to_json',
]