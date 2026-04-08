"""数据模型模块"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SeasonInfo(BaseModel):
    """季度信息数据类"""
    name: str              # "2026年春季"
    year: int              # 2026
    season: str            # "春"/"夏"/"秋"/"冬"
    months: list[str]      # ["3月", "4月", "5月"]
    url: str               # 季度入口 URL


class AnimeDetail(BaseModel):
    """番剧详情数据类（含 magnet 链接）"""
    title: str
    download_link: str
    size: str
    publish_time: str
    category: str = ""
    uploader: str = ""
    seeders: int = Field(default=0, ge=0)
    leechers: int = Field(default=0, ge=0)
    magnet_link: str = ""

    @classmethod
    def from_anime_item(cls, item: "AnimeItem", magnet_link: str = "") -> "AnimeDetail":
        """从 AnimeItem 创建详情"""
        return cls(
            title=item.title,
            download_link=item.download_link,
            size=item.size,
            publish_time=item.publish_time,
            category=item.category,
            uploader=item.uploader,
            seeders=item.seeders,
            leechers=item.leechers,
            magnet_link=magnet_link,
        )


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