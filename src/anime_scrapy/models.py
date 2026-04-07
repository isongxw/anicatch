"""数据模型模块"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AnimeItem(BaseModel):
    """动漫资源数据类"""
    title: str
    download_link: str
    size: str
    publish_time: str
    category: str = ""
    uploader: str = ""
    seeders: int = Field(default=0, ge=0)
    leechers: int = Field(default=0, ge=0)


class CrawlResult(BaseModel):
    """抓取结果数据类"""
    crawl_time: str
    total_count: int = Field(description="抓取数据总数")
    data: list[dict]

    @classmethod
    def create(cls, items: list[AnimeItem]) -> "CrawlResult":
        """从 AnimeItem 列表创建抓取结果"""
        return cls(
            crawl_time=datetime.now().isoformat(),
            total_count=len(items),
            data=[item.model_dump() for item in items]
        )