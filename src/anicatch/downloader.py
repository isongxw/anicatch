"""下载模块"""

import re
import time
import json
from pathlib import Path
from typing import Optional

from curl_cffi import requests
from loguru import logger

from .config import (
    DOWNLOAD_TIMEOUT,
    DOWNLOAD_PORTS,
    DOWNLOAD_DIR,
    TRACKERS,
)

# 尝试导入 libtorrent
try:
    import libtorrent as lt

    HAS_LIBTORRENT = True
except ImportError:
    HAS_LIBTORRENT = False

# 公共 tracker 列表，弥补 miobt tracker 做种者不足的问题
EXTRA_TRACKERS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.openbittorrent.com:6969/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
    "udp://retracker.lanta-net.ru:2710/announce",
]


def get_magnet_link(detail_url: str) -> Optional[str]:
    """
    从详情页获取 magnet 链接，并补充公共 tracker

    Args:
        detail_url: 详情页 URL

    Returns:
        magnet 链接或 None
    """
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        resp = session.get(detail_url, headers=headers, timeout=30)

        # 绕过验证码
        if "captcha" in resp.text.lower():
            resp = session.post(
                "https://miobt.com/addon.php?r=document/view&page=visitor-test",
                data={"visitor_test": "human"},
                headers={**headers, "Referer": detail_url},
                timeout=30,
            )

        # 提取 magnet 链接
        magnets = re.findall(r'magnet:\?xt=urn:btih:[a-zA-Z0-9]+[^"\'<>\s]*', resp.text)

        if magnets:
            magnet = magnets[0]
            for tracker in EXTRA_TRACKERS:
                if tracker not in magnet:
                    magnet += f"&tr={tracker}"
            return magnet

    except Exception as e:
        logger.error(f"获取 magnet 链接失败: {e}")

    return None


def download_with_libtorrent(
    magnet_link: str, save_path: Optional[Path] = None, timeout: int = DOWNLOAD_TIMEOUT
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
    if not HAS_LIBTORRENT:
        logger.error("libtorrent 未安装，无法下载")
        logger.info("请运行: uv add libtorrent")
        return False

    if save_path is None:
        save_path = DOWNLOAD_DIR

    save_path.mkdir(parents=True, exist_ok=True)

    try:
        ses = lt.session()
        ses.listen_on(*DOWNLOAD_PORTS)

        # 解析 magnet 链接
        params = lt.parse_magnet_uri(magnet_link)
        params.save_path = str(save_path)

        # 添加 tracker 列表以加速种子发现
        for tracker in TRACKERS:
            params.trackers.append(tracker)

        # 添加下载
        handle = ses.add_torrent(params)

        logger.info("正在获取元数据...")
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
        logger.info(f"总大小: {total_size / (1024 * 1024):.1f} MB")

        # 等待下载完成
        start_time = time.time()
        while True:
            status = handle.status()

            progress = status.progress * 100
            download_rate = status.download_rate / 1024
            upload_rate = status.upload_rate / 1024

            if int(time.time()) % 5 == 0:
                logger.info(
                    f"进度: {progress:.1f}% | "
                    f"下载: {download_rate:.1f} KB/s | "
                    f"上传: {upload_rate:.1f} KB/s | "
                    f"节点: {status.num_peers}"
                )

            if status.is_finished:
                logger.success(f"下载完成: {name}")
                logger.info(f"保存位置: {save_path / name}")
                return True

            if time.time() - start_time > timeout:
                logger.warning(f"下载超时，当前进度: {progress:.1f}%")
                logger.info(f"可以稍后继续下载，文件位于: {save_path}")
                return False

            time.sleep(1)

    except Exception as e:
        logger.error(f"下载失败: {e}")
        return False


def download_from_json(
    json_file: Path, index: int = 0, save_path: Optional[Path] = None
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
    if not json_file.exists():
        logger.error(f"文件不存在: {json_file}")
        return False

    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("data", [])
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

    detail_url = item.get("download_link", "")
    if not detail_url:
        logger.error("没有找到详情页链接")
        return False

    logger.info("正在获取 magnet 链接...")
    magnet_link = get_magnet_link(detail_url)

    if not magnet_link:
        logger.error("无法获取 magnet 链接")
        return False

    logger.info(f"Magnet: {magnet_link[:60]}...")

    return download_with_libtorrent(magnet_link, save_path)
