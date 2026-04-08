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

    try:
        # 查找季度链接（miobt.com 结构）
        # 常见格式: <a href="...">2026年春季</a> 或类似
        links = page.css("a")

        for link in links:
            text = link.text.strip()
            href = link.attrib.get("href", "")

            # 匹配季度格式: 20XX年X季
            match = re.search(r"(\d{4})年([春夏秋冬])季", text)
            if match and href:
                year = int(match.group(1))
                season_name = match.group(2)

                # 提取月份信息（如果有）
                months = []
                # 尝试从同一区域的链接找月份
                parent = link.parent
                if parent:
                    month_links = parent.css("a")
                    for ml in month_links:
                        month_text = ml.text.strip()
                        month_match = re.search(r"(\d+)月", month_text)
                        if month_match:
                            months.append(month_text)

                # 构建完整 URL
                if not href.startswith("http"):
                    href = TARGET_URL.rstrip("/") + "/" + href.lstrip("/")

                season_info = SeasonInfo(
                    name=text,
                    year=year,
                    season=season_name,
                    months=months,
                    url=href,
                )

                # 避免重复
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
    target_name = f"{year}年{season}季"

    for i, s in enumerate(seasons):
        if s.name == target_name:
            return i

    return 0
