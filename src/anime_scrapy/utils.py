"""工具模块"""

import json
import logging
from pathlib import Path

from .config import LOG_FORMAT, LOG_DATE_FORMAT
from .models import CrawlResult


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
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w", encoding="utf-8") as f:
        json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)

    logger = logging.getLogger(__name__)
    logger.info(f"数据已保存到 {filepath}")