"""爬虫模块"""

import re
import time
import logging
from typing import Any, Optional

from curl_cffi import requests
from scrapling import Selector

from .config import (
    TARGET_URL,
    REQUEST_DELAY,
    MAX_RETRIES,
    RETRY_DELAYS,
)
from .models import AnimeItem


def fetch_with_retry(
    url: str,
    max_retries: int = MAX_RETRIES,
    cookies: Optional[dict] = None
) -> Any:
    """
    使用 Scrapling 获取网页内容，支持重试机制和自动绕过验证码

    Args:
        url: 目标网址
        max_retries: 最大重试次数
        cookies: 可选的 cookies 字典

    Returns:
        Scrapling Selector 对象

    Raises:
        Exception: 所有重试失败后抛出异常
    """
    logger = logging.getLogger(__name__)

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    if cookies:
        session.cookies.update(cookies)

    for attempt in range(max_retries):
        try:
            logger.info(f"尝试获取网页 (第 {attempt + 1} 次)...")
            time.sleep(REQUEST_DELAY)

            resp = session.get(url, headers=headers)
            logger.info(f"HTTP 状态码: {resp.status_code}")

            # 检测验证码
            if 'captcha' in resp.text.lower():
                logger.info("检测到验证码，尝试自动绕过...")

                verify_url = 'https://miobt.com/addon.php?r=document/view&page=visitor-test'
                resp = session.post(verify_url,
                    data={'visitor_test': 'human'},
                    headers={**headers, 'Referer': url}
                )
                logger.info(f"验证请求状态码: {resp.status_code}")

                if 'captcha' in resp.text.lower():
                    logger.warning("自动绕过验证码失败")
                    continue
                else:
                    logger.info("成功绕过验证码！")

            page = Selector(resp.text)
            page.url = url
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


def parse_anime_data(page: Any) -> list[AnimeItem]:
    """
    解析 miobt.com 网页内容，提取动漫资源信息

    Args:
        page: Scrapling Selector 对象

    Returns:
        动漫数据列表
    """
    logger = logging.getLogger(__name__)
    anime_list = []

    try:
        table = page.css("#listTable")
        if not table:
            logger.warning("未找到种子列表表格")
            return anime_list

        rows = table[0].css("tbody tr")
        logger.info(f"找到 {len(rows)} 条资源记录")

        for row in rows:
            try:
                tds = row.css("td")
                if len(tds) < 4:
                    continue

                time_text = tds[0].text.strip()
                category = tds[1].text.strip()

                title_link = tds[2].css("a")
                if not title_link:
                    continue
                title = title_link[0].text.strip()
                href = title_link[0].attrib.get("href", "")

                if href and not href.startswith("http"):
                    href = "https://miobt.com/" + href

                size = tds[3].text.strip()

                uploader = ""
                if len(tds) > 4:
                    uploader_links = tds[4].css("a")
                    if uploader_links:
                        uploader = uploader_links[0].text.strip()

                anime_item = AnimeItem(
                    title=title,
                    download_link=href,
                    size=size,
                    publish_time=time_text,
                    category=category,
                    uploader=uploader,
                )

                anime_list.append(anime_item)

            except Exception as e:
                logger.warning(f"解析条目失败，跳过: {e}")
                continue

        logger.info(f"成功解析 {len(anime_list)} 条数据")

    except Exception as e:
        logger.error(f"解析HTML失败: {e}")

    return anime_list


def parse_books_data(page: Any) -> list[AnimeItem]:
    """
    解析测试网站（books.toscrape.com）的书籍数据
    用于测试爬虫功能

    Args:
        page: Scrapling Selector 对象

    Returns:
        书籍数据列表
    """
    logger = logging.getLogger(__name__)
    books_list = []

    try:
        articles = page.css("article.product_pod")
        logger.info(f"找到 {len(articles)} 本书籍")

        for article in articles:
            try:
                title_elems = article.css("h3 > a")
                if not title_elems:
                    continue
                title_elem = title_elems[0]

                title = title_elem.attrib.get("title") or title_elem.text.strip()
                if not title:
                    continue

                price_elems = article.css("p.price_color")
                price = price_elems[0].text.strip() if price_elems else "未知"

                rating_elems = article.css("p.star-rating")
                rating = ""
                if rating_elems:
                    classes = rating_elems[0].attrib.get("class") or ""
                    for cls in classes.split():
                        if cls != "star-rating":
                            rating = cls
                            break

                book_item = AnimeItem(
                    title=title,
                    download_link=page.url,
                    size=price,
                    publish_time=f"评分: {rating}",
                )

                books_list.append(book_item)

            except Exception as e:
                logger.warning(f"解析书籍失败，跳过: {e}")
                continue

        logger.info(f"成功解析 {len(books_list)} 本书籍")

    except Exception as e:
        logger.error(f"解析HTML失败: {e}")

    return books_list