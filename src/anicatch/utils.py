"""工具模块"""

import json
from pathlib import Path

from loguru import logger


def setup_logging() -> None:
    """配置日志系统"""
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> <level>{level}</level>: {message}",
        level="INFO",
    )


def save_to_json(data: dict, filepath: Path) -> None:
    """
    将抓取结果保存为 JSON 文件

    Args:
        data: 抓取结果数据
        filepath: 输出文件路径
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"数据已保存到 {filepath}")