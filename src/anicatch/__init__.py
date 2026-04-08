"""AniCatch - 动漫资源爬虫包"""

from .models import AnimeItem, CrawlResult, SeasonInfo, AnimeDetail
from .config import (
    TARGET_URL,
    TEST_URL,
    OUTPUT_DIR,
    DOWNLOAD_DIR,
)
from .scraper import fetch_with_retry, parse_anime_data, parse_books_data
from .seasons import (
    get_current_season,
    parse_seasons_from_page,
    fetch_season_anime,
    find_current_season_index,
)
from .downloader import get_magnet_link, download_with_libtorrent, download_from_json
from .utils import setup_logging, save_to_json
from .tui import run_tui

__all__ = [
    'AnimeItem',
    'CrawlResult',
    'SeasonInfo',
    'AnimeDetail',
    'TARGET_URL',
    'TEST_URL',
    'OUTPUT_DIR',
    'DOWNLOAD_DIR',
    'fetch_with_retry',
    'parse_anime_data',
    'parse_books_data',
    'get_current_season',
    'parse_seasons_from_page',
    'fetch_season_anime',
    'find_current_season_index',
    'get_magnet_link',
    'download_with_libtorrent',
    'download_from_json',
    'setup_logging',
    'save_to_json',
    'run_tui',
]