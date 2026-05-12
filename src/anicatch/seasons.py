"""季度发现模块"""

import re
from datetime import datetime

from loguru import logger
from scrapling import Selector

from .config import TARGET_URL
from .models import SeasonInfo, AnimeItem
from .scraper import fetch_with_retry, parse_anime_data


def get_current_season() -> tuple[int, str]:
    """
    根据当前日期判断季度

    Returns:
        (year, season_name) 如 (2026, "春")
    """
    now = datetime.now()
    month = now.month
    year = now.year

    # 季度判断
    if month in (3, 4, 5):
        season = "春"
    elif month in (6, 7, 8):
        season = "夏"
    elif month in (9, 10, 11):
        season = "秋"
    else:  # 12, 1, 2
        season = "冬"
        if month == 12:
            year += 1  # 12月属于下一年的冬季

    return year, season


def parse_seasons_from_page(page: Selector) -> list[SeasonInfo]:
    """
    从首页解析季度分类入口

    Args:
        page: Scrapling Selector 对象

    Returns:
        季度信息列表
    """
    seasons = []
    season_map = {"01": "冬", "04": "春", "07": "夏", "10": "秋"}

    try:
        links = page.css("a")

        for link in links:
            text = link.text.strip()
            href = link.attrib.get("href", "")

            # 匹配新格式: 26年01月番
            match = re.search(r"(\d{2})年(\d{2})月番", text)
            if match and href:
                short_year = int(match.group(1))
                year = 2000 + short_year if short_year < 50 else 1900 + short_year
                month = match.group(2)
                season_name = season_map.get(month, "")

                if not season_name:
                    continue

                # 构建完整 URL
                if not href.startswith("http"):
                    href = TARGET_URL.rstrip("/") + "/" + href.lstrip("/")

                season_info = SeasonInfo(
                    name=text,
                    year=year,
                    season=season_name,
                    months=[f"{int(month)}月"],
                    url=href,
                )

                # 避免重复
                if not any(s.url == href for s in seasons):
                    seasons.append(season_info)
                continue

            # 匹配旧格式: 2026年春季
            match = re.search(r"(\d{4})年([春夏秋冬])季", text)
            if match and href:
                year = int(match.group(1))
                season_name = match.group(2)

                months = []
                parent = link.parent
                if parent:
                    month_links = parent.css("a")
                    for ml in month_links:
                        month_text = ml.text.strip()
                        month_match = re.search(r"(\d+)月", month_text)
                        if month_match:
                            months.append(month_text)

                if not href.startswith("http"):
                    href = TARGET_URL.rstrip("/") + "/" + href.lstrip("/")

                season_info = SeasonInfo(
                    name=text,
                    year=year,
                    season=season_name,
                    months=months,
                    url=href,
                )

                if not any(s.url == href for s in seasons):
                    seasons.append(season_info)

        logger.info(f"发现 {len(seasons)} 个季度入口")

    except Exception as e:
        logger.error(f"解析季度入口失败: {e}")

    return seasons


def fetch_season_anime(season_url: str) -> list[AnimeItem]:
    """
    抓取指定季度的番剧列表

    Args:
        season_url: 季度页面 URL

    Returns:
        番剧列表
    """
    try:
        page = fetch_with_retry(season_url)
        return parse_anime_data(page)
    except Exception as e:
        logger.error(f"抓取季度番剧失败: {e}")
        return []


def find_current_season_index(seasons: list[SeasonInfo]) -> int:
    """
    找到当前季度在列表中的索引

    Args:
        seasons: 季度列表

    Returns:
        索引（未找到返回 0）
    """
    year, season = get_current_season()

    for i, s in enumerate(seasons):
        if s.year == year and s.season == season:
            return i

    return 0
