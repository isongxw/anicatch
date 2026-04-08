# AniCatch TUI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace CLI with textual TUI for browsing anime by season/month, viewing details with magnet links, and downloading.

**Architecture:** Add seasons.py for season discovery, extend models.py with SeasonInfo/AnimeDetail, create tui.py with textual widgets, replace __main__.py entry point.

**Tech Stack:** Python 3.10+, textual (TUI), scrapling (HTML), curl_cffi (HTTP), pydantic (data), libtorrent (optional download)

---

## Task 1: Add textual dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add textual to dependencies**

Edit `pyproject.toml`, add `textual` to dependencies list:

```toml
dependencies = [
    "browserforge>=1.2.4",
    "curl-cffi>=0.15.0",
    "playwright>=1.58.0",
    "scrapling>=0.2.0",
    "pydantic>=2.0.0",
    "loguru>=0.7.0",
    "libtorrent>=2.0.11",
    "textual>=0.44.0",
]
```

- [ ] **Step 2: Install dependency**

Run: `uv sync`
Expected: textual installed successfully

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add textual dependency for TUI"
```

---

## Task 2: Add SeasonInfo and AnimeDetail models

**Files:**
- Modify: `src/anicatch/models.py`

- [ ] **Step 1: Add SeasonInfo model**

Add to `models.py` after imports:

```python
class SeasonInfo(BaseModel):
    """季度信息数据类"""
    name: str              # "2026年春季"
    year: int              # 2026
    season: str            # "春"/"夏"/"秋"/"冬"
    months: list[str]      # ["3月", "4月", "5月"]
    url: str               # 季度入口 URL
```

- [ ] **Step 2: Add AnimeDetail model**

Add to `models.py` after SeasonInfo:

```python
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
    def from_anime_item(cls, item: AnimeItem, magnet_link: str = "") -> "AnimeDetail":
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
```

- [ ] **Step 3: Commit**

```bash
git add src/anicatch/models.py
git commit -m "feat: add SeasonInfo and AnimeDetail models"
```

---

## Task 3: Create seasons.py module

**Files:**
- Create: `src/anicatch/seasons.py`

- [ ] **Step 1: Create seasons.py with season detection**

Create `src/anicatch/seasons.py`:

```python
"""季度发现模块"""

import re
from datetime import datetime
from typing import Optional

from loguru import logger
from scrapling import Selector

from .config import TARGET_URL, REQUEST_DELAY, MAX_RETRIES, RETRY_DELAYS
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
```

- [ ] **Step 2: Update __init__.py exports**

Edit `src/anicatch/__init__.py`, add seasons exports:

```python
"""AniCatch - 动漫资源爬虫包"""

from .models import AnimeItem, CrawlResult, SeasonInfo, AnimeDetail
from .config import (
    TARGET_URL,
    TEST_URL,
    OUTPUT_DIR,
    DOWNLOAD_DIR,
)
from .scraper import fetch_with_retry, parse_anime_data, parse_books_data
from .seasons import (
    get_current_season,
    parse_seasons_from_page,
    fetch_season_anime,
    find_current_season_index,
)
from .downloader import get_magnet_link, download_with_libtorrent, download_from_json
from .utils import setup_logging, save_to_json

__all__ = [
    'AnimeItem',
    'CrawlResult',
    'SeasonInfo',
    'AnimeDetail',
    'TARGET_URL',
    'TEST_URL',
    'OUTPUT_DIR',
    'DOWNLOAD_DIR',
    'fetch_with_retry',
    'parse_anime_data',
    'parse_books_data',
    'get_current_season',
    'parse_seasons_from_page',
    'fetch_season_anime',
    'find_current_season_index',
    'get_magnet_link',
    'download_with_libtorrent',
    'download_from_json',
    'setup_logging',
    'save_to_json',
]
```

- [ ] **Step 3: Commit**

```bash
git add src/anicatch/seasons.py src/anicatch/__init__.py
git commit -m "feat: add seasons module for season discovery"
```

---

## Task 4: Create TUI main structure

**Files:**
- Create: `src/anicatch/tui.py`

- [ ] **Step 1: Create TUI app skeleton with textual**

Create `src/anicatch/tui.py`:

```python
"""TUI 模块"""

from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Label, ListView, ListItem, Static
from textual.binding import Binding
from textual.reactive import reactive

from loguru import logger

from .models import SeasonInfo, AnimeItem, AnimeDetail
from .seasons import (
    get_current_season,
    parse_seasons_from_page,
    fetch_season_anime,
    find_current_season_index,
)
from .scraper import fetch_with_retry
from .downloader import get_magnet_link, download_with_libtorrent, HAS_LIBTORRENT


class SeasonHeader(Static):
    """季度/月份显示组件"""

    season_name = reactive("")
    month_name = reactive("")

    def watch_season_name(self, name: str) -> None:
        self.update(f"季度: {name} ◀ ▶")

    def watch_month_name(self, name: str) -> None:
        # 覆盖父类 update
        pass

    def render(self) -> str:
        month_part = f"月份: {self.month_name} [ ]" if self.month_name else ""
        return f"季度: {self.season_name} ◀ ▶    {month_part}"


class AnimeListItem(ListItem):
    """番剧列表项"""

    def __init__(self, anime: AnimeItem, index: int) -> None:
        super().__init__()
        self.anime = anime
        self.index = index

    def compose(self) -> ComposeResult:
        title = self.anime.title[:50] + "..." if len(self.anime.title) > 50 else self.anime.title
        yield Label(f"[{self.index}] {title}    {self.anime.size}    {self.anime.publish_time}")


class AnimeListView(Container):
    """番剧列表容器"""

    def __init__(self) -> None:
        super().__init__()
        self.animes: list[AnimeItem] = []

    def update_animes(self, animes: list[AnimeItem]) -> None:
        """更新番剧列表"""
        self.animes = animes
        list_view = self.query_one(ListView)
        list_view.clear()

        for i, anime in enumerate(animes):
            list_view.append(AnimeListItem(anime, i))

    def compose(self) -> ComposeResult:
        yield Label("─ 番剧列表 ─", classes="header")
        yield ListView()


class DetailView(Container):
    """番剧详情视图"""

    anime: Optional[AnimeDetail] = None

    def update_detail(self, anime: AnimeDetail) -> None:
        """更新详情显示"""
        self.anime = anime
        self.query_one("#detail-content", Static).update(self._render_detail())

    def _render_detail(self) -> str:
        if not self.anime:
            return "加载中..."

        lines = [
            f"标题: {self.anime.title}",
            f"大小: {self.anime.size}",
            f"发布: {self.anime.publish_time}",
            f"分类: {self.anime.category}",
            f"上传者: {self.anime.uploader}",
            f"种子数: {self.anime.seeders}  |  下载数: {self.anime.leechers}",
            "─" * 50,
            f"Magnet: {self.anime.magnet_link[:60]}..." if self.anime.magnet_link else "Magnet: 获取中...",
            "─" * 50,
            "操作: D下载 | Esc返回 | Q退出",
        ]
        return "\n".join(lines)

    def compose(self) -> ComposeResult:
        yield Static("", id="detail-content")


class AniCatchApp(App):
    """AniCatch TUI 应用"""

    CSS = """
    Screen {
        layout: vertical;
    }

    SeasonHeader {
        height: 3;
        padding: 1;
        text-align: center;
    }

    AnimeListView {
        height: 1fr;
        border: solid green;
    }

    .header {
        text-style: bold;
        color: green;
    }

    ListView {
        height: 1fr;
    }

    AnimeListItem:focus {
        background: $surface-light;
    }

    DetailView {
        height: 1fr;
        border: solid blue;
        padding: 1;
    }

    #detail-content {
        height: 1fr;
    }

    Footer {
        height: 3;
    }
    """

    BINDINGS = [
        Binding("up", "scroll_up", "向上"),
        Binding("down", "scroll_down", "向下"),
        Binding("left", "prev_season", "上一季度"),
        Binding("right", "next_season", "下一季度"),
        Binding("bracketleft", "prev_month", "上一月"),
        Binding("bracketright", "next_month", "下一月"),
        Binding("enter", "show_detail", "详情"),
        Binding("d", "download", "下载"),
        Binding("r", "reload", "刷新"),
        Binding("escape", "back", "返回"),
        Binding("q", "quit", "退出"),
    ]

    seasons: list[SeasonInfo] = []
    current_season_index: reactive[int] = reactive(0)
    current_month_index: reactive[int] = reactive(0)
    current_animes: list[AnimeItem] = []
    in_detail_view: bool = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield SeasonHeader()
        yield AnimeListView()
        yield DetailView()
        yield Footer()

    def on_mount(self) -> None:
        """应用启动时加载当前季度"""
        self.call_from_thread(self.load_initial_data)

    async def load_initial_data(self) -> None:
        """加载初始数据"""
        try:
            # 抓取首页获取季度入口
            page = fetch_with_retry("https://miobt.com/")
            self.seasons = parse_seasons_from_page(page)

            if not self.seasons:
                self.notify("未找到季度入口", severity="error")
                return

            # 定位当前季度
            self.current_season_index = find_current_season_index(self.seasons)
            await self.load_season_animes()

        except Exception as e:
            logger.error(f"加载失败: {e}")
            self.notify(f"加载失败: {e}", severity="error")

    async def load_season_animes(self) -> None:
        """加载当前季度的番剧"""
        if not self.seasons:
            return

        season = self.seasons[self.current_season_index]
        self.query_one(SeasonHeader).season_name = season.name

        # 设置月份
        if season.months and self.current_month_index < len(season.months):
            self.query_one(SeasonHeader).month_name = season.months[self.current_month_index]
        else:
            self.query_one(SeasonHeader).month_name = ""

        self.notify(f"加载: {season.name}")

        # 抓取番剧列表
        self.current_animes = fetch_season_anime(season.url)

        if not self.current_animes:
            self.notify("当前季度无数据", severity="warning")
        else:
            self.query_one(AnimeListView).update_animes(self.current_animes)
            self.notify(f"加载 {len(self.current_animes)} 条数据")

    def action_scroll_up(self) -> None:
        """向上滚动"""
        if not self.in_detail_view:
            list_view = self.query_one(AnimeListView).query_one(ListView)
            list_view.action_cursor_up()

    def action_scroll_down(self) -> None:
        """向下滚动"""
        if not self.in_detail_view:
            list_view = self.query_one(AnimeListView).query_one(ListView)
            list_view.action_cursor_down()

    def action_prev_season(self) -> None:
        """切换上一季度"""
        if self.in_detail_view or not self.seasons:
            return

        if self.current_season_index > 0:
            self.current_season_index -= 1
            self.current_month_index = 0
            self.call_from_thread(self.load_season_animes)

    def action_next_season(self) -> None:
        """切换下一季度"""
        if self.in_detail_view or not self.seasons:
            return

        if self.current_season_index < len(self.seasons) - 1:
            self.current_season_index += 1
            self.current_month_index = 0
            self.call_from_thread(self.load_season_animes)

    def action_prev_month(self) -> None:
        """切换上一月"""
        if self.in_detail_view:
            return

        season = self.seasons[self.current_season_index]
        if season.months and self.current_month_index > 0:
            self.current_month_index -= 1
            self.call_from_thread(self.load_season_animes)

    def action_next_month(self) -> None:
        """切换下一月"""
        if self.in_detail_view:
            return

        season = self.seasons[self.current_season_index]
        if season.months and self.current_month_index < len(season.months) - 1:
            self.current_month_index += 1
            self.call_from_thread(self.load_season_animes)

    def action_show_detail(self) -> None:
        """显示详情"""
        if self.in_detail_view or not self.current_animes:
            return

        list_view = self.query_one(AnimeListView).query_one(ListView)
        index = list_view.cursor_index

        if 0 <= index < len(self.current_animes):
            anime = self.current_animes[index]

            # 隐藏列表，显示详情
            self.query_one(AnimeListView).visible = False
            self.query_one(DetailView).visible = True
            self.in_detail_view = True

            # 异步获取 magnet
            self.call_from_thread(self.fetch_detail, anime, index)

    async def fetch_detail(self, anime: AnimeItem, index: int) -> None:
        """获取详情（含 magnet）"""
        detail_view = self.query_one(DetailView)

        # 先显示基本信息
        detail = AnimeDetail.from_anime_item(anime, "")
        detail_view.update_detail(detail)

        # 获取 magnet 链接
        magnet = get_magnet_link(anime.download_link)
        detail.magnet_link = magnet if magnet else "获取失败"
        detail_view.update_detail(detail)

    def action_back(self) -> None:
        """返回列表"""
        if self.in_detail_view:
            self.query_one(AnimeListView).visible = True
            self.query_one(DetailView).visible = False
            self.in_detail_view = False

    def action_download(self) -> None:
        """下载当前番剧"""
        if not self.in_detail_view:
            return

        if not HAS_LIBTORRENT:
            self.notify("libtorrent 未安装，无法下载", severity="error")
            return

        detail_view = self.query_one(DetailView)
        if not detail_view.anime or not detail_view.anime.magnet_link:
            self.notify("无 magnet 链接", severity="error")
            return

        magnet = detail_view.anime.magnet_link
        if magnet == "获取失败":
            self.notify("magnet 链接无效", severity="error")
            return

        self.notify("开始下载...")
        self.call_from_thread(self.start_download, magnet)

    async def start_download(self, magnet: str) -> None:
        """开始下载"""
        success = download_with_libtorrent(magnet)
        if success:
            self.notify("下载完成", severity="information")
        else:
            self.notify("下载失败或超时", severity="error")

    def action_reload(self) -> None:
        """刷新当前季度"""
        if self.in_detail_view:
            return
        self.call_from_thread(self.load_season_animes)


def run_tui() -> None:
    """启动 TUI"""
    app = AniCatchApp()
    app.run()
```

- [ ] **Step 2: Commit**

```bash
git add src/anicatch/tui.py
git commit -m "feat: add TUI module with textual"
```

---

## Task 5: Replace CLI entry point with TUI

**Files:**
- Modify: `src/anicatch/__main__.py`

- [ ] **Step 1: Replace __main__.py with TUI entry**

Replace entire content of `src/anicatch/__main__.py`:

```python
"""CLI 入口点"""

from .tui import run_tui


def main_cli() -> None:
    """主入口函数"""
    run_tui()


if __name__ == "__main__":
    main_cli()
```

- [ ] **Step 2: Update __init__.py exports**

Edit `src/anicatch/__init__.py`, add `run_tui` to exports:

```python
"""AniCatch - 动漫资源爬虫包"""

from .models import AnimeItem, CrawlResult, SeasonInfo, AnimeDetail
from .config import (
    TARGET_URL,
    TEST_URL,
    OUTPUT_DIR,
    DOWNLOAD_DIR,
)
from .scraper import fetch_with_retry, parse_anime_data, parse_books_data
from .seasons import (
    get_current_season,
    parse_seasons_from_page,
    fetch_season_anime,
    find_current_season_index,
)
from .downloader import get_magnet_link, download_with_libtorrent, download_from_json
from .utils import setup_logging, save_to_json
from .tui import run_tui

__all__ = [
    'AnimeItem',
    'CrawlResult',
    'SeasonInfo',
    'AnimeDetail',
    'TARGET_URL',
    'TEST_URL',
    'OUTPUT_DIR',
    'DOWNLOAD_DIR',
    'fetch_with_retry',
    'parse_anime_data',
    'parse_books_data',
    'get_current_season',
    'parse_seasons_from_page',
    'fetch_season_anime',
    'find_current_season_index',
    'get_magnet_link',
    'download_with_libtorrent',
    'download_from_json',
    'setup_logging',
    'save_to_json',
    'run_tui',
]
```

- [ ] **Step 3: Commit**

```bash
git add src/anicatch/__main__.py src/anicatch/__init__.py
git commit -m "feat: replace CLI with TUI entry point"
```

---

## Task 6: Test and verify

**Files:**
- None (testing)

- [ ] **Step 1: Run the application**

Run: `uv run anicatch`
Expected: TUI window opens, shows current season anime list

- [ ] **Step 2: Test keybindings**

Manually test:
- `↑`/`↓` — scroll list works
- `←`/`→` — switch season works
- `Enter` — show detail works
- `Esc` — return to list works
- `Q` — quit works

- [ ] **Step 3: Final commit if any fixes needed**

If fixes required, commit after testing passes.