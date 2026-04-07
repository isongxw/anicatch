#!/usr/bin/env python3
"""
miobt.com 动漫资源爬虫
使用 Scrapling 库抓取首页数据并保存为 JSON 格式
支持 libtorrent 下载 magnet 链接
"""

import json
import logging
import re
import sys
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from curl_cffi import requests
from scrapling import Selector

# 尝试导入 libtorrent
try:
    import libtorrent as lt
    HAS_LIBTORRENT = True
except ImportError:
    HAS_LIBTORRENT = False


# 配置常量
TARGET_URL = "https://miobt.com/"
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "anime_data.json"
DOWNLOAD_DIR = Path("downloads")  # 下载目录

# 测试用备用网站（无验证码）
TEST_URL = "https://books.toscrape.com/"

# 请求配置
REQUEST_DELAY = 2.0  # 基础延迟（秒）
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAYS = [1, 2, 4]  # 重试间隔（秒）

# 下载配置
DOWNLOAD_TIMEOUT = 300  # 下载超时（秒）
DOWNLOAD_PORTS = (6881, 6891)  # BT 端口范围

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
        Scrapling Page 对象

    Raises:
        Exception: 所有重试失败后抛出异常
    """
    logger = logging.getLogger(__name__)

    # 使用 curl_cffi 的 session 来保持会话
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

            # 获取页面
            resp = session.get(url, headers=headers)
            logger.info(f"HTTP 状态码: {resp.status_code}")

            # 检测验证码
            if 'captcha' in resp.text.lower():
                logger.info("检测到验证码，尝试自动绕过...")

                # 提交验证表单
                verify_url = 'https://miobt.com/addon.php?r=document/view&page=visitor-test'
                resp = session.post(verify_url,
                    data={'visitor_test': 'human'},
                    headers={**headers, 'Referer': url}
                )
                logger.info(f"验证请求状态码: {resp.status_code}")

                # 检查是否通过
                if 'captcha' in resp.text.lower():
                    logger.warning("自动绕过验证码失败")
                    continue
                else:
                    logger.info("成功绕过验证码！")

            # 使用 Selector 解析 HTML
            page = Selector(resp.text)
            page.url = url  # 保存 URL 引用
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
    解析 miobt.com 网页内容，提取动漫资源信息

    Args:
        page: Scrapling Selector 对象

    Returns:
        动漫数据列表
    """
    logger = logging.getLogger(__name__)
    anime_list = []

    try:
        # 查找种子列表表格
        table = page.css("#listTable")
        if not table:
            logger.warning("未找到种子列表表格")
            return anime_list

        # 获取所有行
        rows = table[0].css("tbody tr")
        logger.info(f"找到 {len(rows)} 条资源记录")

        for row in rows:
            try:
                tds = row.css("td")
                if len(tds) < 4:
                    continue

                # 提取发表时间
                time_text = tds[0].text.strip()

                # 提取类别
                category = tds[1].text.strip()

                # 提取标题和链接
                title_link = tds[2].css("a")
                if not title_link:
                    continue
                title = title_link[0].text.strip()
                href = title_link[0].attrib.get("href", "")

                # 构建完整 URL
                if href and not href.startswith("http"):
                    href = "https://miobt.com/" + href

                # 提取大小
                size = tds[3].text.strip()

                # 提取 UP 主
                uploader = ""
                if len(tds) > 4:
                    uploader_links = tds[4].css("a")
                    if uploader_links:
                        uploader = uploader_links[0].text.strip()

                anime_entry = create_anime_entry(
                    title=title,
                    download_link=href,
                    size=size,
                    publish_time=time_text,
                    seeders=0,
                    leechers=0
                )

                # 添加额外信息
                anime_entry["category"] = category
                anime_entry["uploader"] = uploader

                anime_list.append(anime_entry)

            except Exception as e:
                logger.warning(f"解析条目失败，跳过: {e}")
                continue

        logger.info(f"成功解析 {len(anime_list)} 条数据")

    except Exception as e:
        logger.error(f"解析HTML失败: {e}")

    return anime_list


def parse_books_data(page: Any) -> list[AnimeData]:
    """
    解析测试网站（books.toscrape.com）的书籍数据
    用于测试爬虫功能

    Args:
        page: Scrapling Page 对象

    Returns:
        书籍数据列表
    """
    logger = logging.getLogger(__name__)
    books_list = []

    try:
        # 查找所有书籍条目
        articles = page.css("article.product_pod")
        logger.info(f"找到 {len(articles)} 本书籍")

        for article in articles:
            try:
                # 提取标题
                title_elems = article.css("h3 > a")
                if not title_elems:
                    continue
                title_elem = title_elems[0]

                title = title_elem.attrib.get("title") or title_elem.text.strip()
                if not title:
                    continue

                # 提取价格
                price_elems = article.css("p.price_color")
                price = price_elems[0].text.strip() if price_elems else "未知"

                # 提取评分
                rating_elems = article.css("p.star-rating")
                rating = ""
                if rating_elems:
                    classes = rating_elems[0].attrib.get("class") or ""
                    for cls in classes.split():
                        if cls != "star-rating":
                            rating = cls
                            break

                book_entry = create_anime_entry(
                    title=title,
                    download_link=page.url,
                    size=price,
                    publish_time=f"评分: {rating}",
                    seeders=0,
                    leechers=0
                )

                books_list.append(book_entry)

            except Exception as e:
                logger.warning(f"解析书籍失败，跳过: {e}")
                continue

        logger.info(f"成功解析 {len(books_list)} 本书籍")

    except Exception as e:
        logger.error(f"解析HTML失败: {e}")

    return books_list


def get_magnet_link(detail_url: str) -> Optional[str]:
    """
    从详情页获取 magnet 链接

    Args:
        detail_url: 详情页 URL

    Returns:
        magnet 链接或 None
    """
    logger = logging.getLogger(__name__)

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        # 获取详情页
        resp = session.get(detail_url, headers=headers, timeout=30)

        # 绕过验证码
        if 'captcha' in resp.text.lower():
            resp = session.post(
                'https://miobt.com/addon.php?r=document/view&page=visitor-test',
                data={'visitor_test': 'human'},
                headers={**headers, 'Referer': detail_url},
                timeout=30
            )

        # 提取 magnet 链接
        magnets = re.findall(
            r'magnet:\?xt=urn:btih:[a-zA-Z0-9]+[^"\'<>\s]*',
            resp.text
        )

        if magnets:
            return magnets[0]

    except Exception as e:
        logger.error(f"获取 magnet 链接失败: {e}")

    return None


def download_with_libtorrent(
    magnet_link: str,
    save_path: Optional[Path] = None,
    timeout: int = DOWNLOAD_TIMEOUT
) -> bool:
    """
    使用 libtorrent 下载 magnet 链接

    Args:
        magnet_link: magnet 链接
        save_path: 保存路径
        timeout: 超时时间（秒）

    Returns:
        是否成功
    """
    logger = logging.getLogger(__name__)

    if not HAS_LIBTORRENT:
        logger.error("libtorrent 未安装，无法下载")
        logger.info("请运行: uv add libtorrent")
        return False

    if save_path is None:
        save_path = DOWNLOAD_DIR

    save_path.mkdir(parents=True, exist_ok=True)

    try:
        # 创建 session
        ses = lt.session()
        ses.listen_on(*DOWNLOAD_PORTS)

        # 添加 tracker（提高下载速度）
        trackers = [
            'udp://tracker.opentrackr.org:1337/announce',
            'udp://open.stealth.si:80/announce',
            'udp://tracker.torrent.eu.org:451/announce',
            'udp://tracker.bittor.pw:1337/announce',
            'udp://public.popcorn-tracker.org:6969/announce',
            'http://open.acgtracker.com:1096/announce',
        ]

        # 解析 magnet 链接
        params = lt.parse_magnet_uri(magnet_link)
        params.save_path = str(save_path)

        # 添加下载
        handle = ses.add_torrent(params)

        logger.info(f"正在获取元数据...")
        logger.info(f"保存路径: {save_path}")

        # 等待获取元数据
        start_time = time.time()
        while not handle.status().has_metadata:
            time.sleep(1)
            if time.time() - start_time > 60:
                logger.error("获取元数据超时")
                return False

        # 获取种子信息
        torrent_info = handle.get_torrent_info()
        name = torrent_info.name()
        total_size = torrent_info.total_size()

        logger.info(f"开始下载: {name}")
        logger.info(f"总大小: {total_size / (1024*1024):.1f} MB")

        # 等待下载完成
        start_time = time.time()
        while True:
            status = handle.status()

            # 计算进度
            progress = status.progress * 100
            download_rate = status.download_rate / 1024  # KB/s
            upload_rate = status.upload_rate / 1024

            # 每 5 秒输出一次进度
            if int(time.time()) % 5 == 0:
                logger.info(
                    f"进度: {progress:.1f}% | "
                    f"下载: {download_rate:.1f} KB/s | "
                    f"上传: {upload_rate:.1f} KB/s | "
                    f"节点: {status.num_peers}"
                )

            # 检查是否完成
            if status.is_finished:
                logger.info(f"✓ 下载完成: {name}")
                logger.info(f"保存位置: {save_path / name}")
                return True

            # 检查超时
            if time.time() - start_time > timeout:
                logger.warning(f"下载超时，当前进度: {progress:.1f}%")
                logger.info(f"可以稍后继续下载，文件位于: {save_path}")
                return False

            time.sleep(1)

    except Exception as e:
        logger.error(f"下载失败: {e}")
        return False


def download_from_json(
    json_file: Path,
    index: int = 0,
    save_path: Optional[Path] = None
) -> bool:
    """
    从 JSON 文件下载指定索引的资源

    Args:
        json_file: JSON 数据文件
        index: 资源索引（从 0 开始）
        save_path: 保存路径

    Returns:
        是否成功
    """
    logger = logging.getLogger(__name__)

    if not json_file.exists():
        logger.error(f"文件不存在: {json_file}")
        return False

    with json_file.open('r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get('data', [])
    if not items:
        logger.error("JSON 文件中没有数据")
        return False

    if index >= len(items):
        logger.error(f"索引 {index} 超出范围 (共 {len(items)} 条)")
        return False

    item = items[index]
    logger.info(f"选择: {item['title']}")
    logger.info(f"大小: {item['size']}")
    logger.info(f"发布时间: {item['publish_time']}")

    # 获取详情页链接
    detail_url = item.get('download_link', '')
    if not detail_url:
        logger.error("没有找到详情页链接")
        return False

    logger.info(f"正在获取 magnet 链接...")
    magnet_link = get_magnet_link(detail_url)

    if not magnet_link:
        logger.error("无法获取 magnet 链接")
        return False

    logger.info(f"Magnet: {magnet_link[:60]}...")

    # 开始下载
    return download_with_libtorrent(magnet_link, save_path)


def main(
    test_mode: bool = False,
    cookies: Optional[dict] = None,
    search_keyword: Optional[str] = None
) -> None:
    """
    主函数 - 整合所有功能

    Args:
        test_mode: 是否使用测试网站（无验证码）
        cookies: 可选的 cookies 字典
        search_keyword: 搜索关键词
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    # 根据模式选择目标URL和解析函数
    if test_mode:
        target_url = TEST_URL
        parse_func = parse_books_data
        output_file = OUTPUT_DIR / "test_books_data.json"
        logger.info("使用测试模式，抓取 books.toscrape.com...")
    else:
        if search_keyword:
            # 构建搜索 URL
            encoded_keyword = urllib.parse.quote(search_keyword)
            target_url = f"https://miobt.com/search.php?keyword={encoded_keyword}"
            # 安全的文件名
            safe_keyword = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in search_keyword)
            output_file = OUTPUT_DIR / f"search_{safe_keyword}.json"
            logger.info(f"搜索关键词: {search_keyword}")
        else:
            target_url = TARGET_URL
            output_file = OUTPUT_FILE
            logger.info("开始抓取 miobt.com 首页数据...")
        parse_func = parse_anime_data

    try:
        # 1. 获取网页内容
        page = fetch_with_retry(target_url, cookies=cookies)

        # 2. 解析数据
        data = parse_func(page)

        if not data:
            logger.warning("未解析到任何数据")
            return

        # 3. 创建结果对象
        crawl_time = datetime.now().isoformat()
        result = create_crawl_result(data, crawl_time)

        # 4. 保存数据
        save_to_json(result, output_file)

        logger.info(f"抓取完成！共获取 {len(data)} 条数据")

    except Exception as e:
        logger.error(f"抓取失败: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="miobt.com 动漫资源爬虫 - 支持搜索和下载",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 抓取首页
  python main.py

  # 搜索动漫
  python main.py --search "海贼王"

  # 下载搜索结果的第一条
  python main.py --search "JOJO" --download

  # 下载搜索结果的第三条（索引从0开始）
  python main.py --search "海贼王" --download --index 2

  # 从已有的 JSON 文件下载
  python main.py --download --file output/search_海贼王.json --index 0

  # 测试模式
  python main.py --test
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
        help="搜索关键词，例如: '海贼王', '葬送的芙莉莲'"
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
        help="下载资源的索引（从0开始，默认第一条）"
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
        help="Cookies 字符串，格式: 'name1=value1; name2=value2'"
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)

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
            # 从 JSON 文件下载
            json_file = Path(args.file)
            success = download_from_json(json_file, args.index, save_path)
            sys.exit(0 if success else 1)
        elif args.search:
            # 先搜索再下载
            logger.info(f"搜索关键词: {args.search}")
            encoded_keyword = urllib.parse.quote(args.search)
            target_url = f"https://miobt.com/search.php?keyword={encoded_keyword}"

            page = fetch_with_retry(target_url, cookies=cookies_dict)
            data = parse_anime_data(page)

            if not data:
                logger.error("未找到任何资源")
                sys.exit(1)

            # 保存搜索结果
            safe_keyword = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in args.search)
            json_file = OUTPUT_DIR / f"search_{safe_keyword}.json"
            result = create_crawl_result(data, datetime.now().isoformat())
            save_to_json(result, json_file)

            # 显示搜索结果
            logger.info(f"找到 {len(data)} 条结果:")
            for i, item in enumerate(data[:10]):
                logger.info(f"  [{i}] {item['title'][:50]}... ({item['size']})")

            # 下载指定索引
            if args.index >= len(data):
                logger.error(f"索引 {args.index} 超出范围")
                sys.exit(1)

            success = download_from_json(json_file, args.index, save_path)
            sys.exit(0 if success else 1)
        else:
            # 下载首页最新资源
            page = fetch_with_retry(TARGET_URL, cookies=cookies_dict)
            data = parse_anime_data(page)

            if not data:
                logger.error("未找到任何资源")
                sys.exit(1)

            # 显示资源列表
            logger.info(f"首页最新 {len(data)} 条资源:")
            for i, item in enumerate(data[:10]):
                logger.info(f"  [{i}] {item['title'][:50]}... ({item['size']})")

            success = download_from_json(OUTPUT_FILE, args.index, save_path)
            sys.exit(0 if success else 1)

    # 正常抓取模式
    main(test_mode=args.test, cookies=cookies_dict, search_keyword=args.search)