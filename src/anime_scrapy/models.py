"""数据模型模块"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional


@dataclass
class AnimeItem:
    """动漫资源数据类"""
    title: str
    download_link: str
    size: str
    publish_time: str
    category: str = ""
    uploader: str = ""
    seeders: int = 0
    leechers: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AnimeItem":
        return cls(
            title=data.get("title", ""),
            download_link=data.get("download_link", ""),
            size=data.get("size", ""),
            publish_time=data.get("publish_time", ""),
            category=data.get("category", ""),
            uploader=data.get("uploader", ""),
            seeders=data.get("seeders", 0),
            leechers=data.get("leechers", 0),
        )


@dataclass
class CrawlResult:
    """抓取结果数据类"""
    crawl_time: str
    total_count: int
    data: list[dict]

    @classmethod
    def create(cls, items: list[AnimeItem]) -> "CrawlResult":
        return cls(
            crawl_time=datetime.now().isoformat(),
            total_count=len(items),
            data=[item.to_dict() for item in items]
        )

    def to_dict(self) -> dict:
        return asdict(self)