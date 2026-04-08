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
        yield Label("-- 番剧列表 --", classes="header")
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
            "-" * 50,
            f"Magnet: {self.anime.magnet_link[:60]}..." if self.anime.magnet_link else "Magnet: 获取中...",
            "-" * 50,
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
        self.run_worker(self.load_initial_data)

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

        try:
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

        except Exception as e:
            logger.error(f"加载番剧列表失败: {e}")
            self.notify(f"加载失败: {e}", severity="error")

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
            self.run_worker(self.load_season_animes)

    def action_next_season(self) -> None:
        """切换下一季度"""
        if self.in_detail_view or not self.seasons:
            return

        if self.current_season_index < len(self.seasons) - 1:
            self.current_season_index += 1
            self.current_month_index = 0
            self.run_worker(self.load_season_animes)

    def action_prev_month(self) -> None:
        """切换上一月"""
        if self.in_detail_view:
            return

        season = self.seasons[self.current_season_index]
        if season.months and self.current_month_index > 0:
            self.current_month_index -= 1
            self.run_worker(self.load_season_animes)

    def action_next_month(self) -> None:
        """切换下一月"""
        if self.in_detail_view:
            return

        season = self.seasons[self.current_season_index]
        if season.months and self.current_month_index < len(season.months) - 1:
            self.current_month_index += 1
            self.run_worker(self.load_season_animes)

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
            self.run_worker(self.fetch_detail(anime, index))

    async def fetch_detail(self, anime: AnimeItem, index: int) -> None:
        """获取详情（含 magnet）"""
        detail_view = self.query_one(DetailView)

        try:
            # 先显示基本信息
            detail = AnimeDetail.from_anime_item(anime, "")
            detail_view.update_detail(detail)

            # 获取 magnet 链接
            magnet = get_magnet_link(anime.download_link)
            detail.magnet_link = magnet if magnet else "获取失败"
            detail_view.update_detail(detail)
        except Exception as e:
            logger.error(f"获取详情失败: {e}")
            detail = AnimeDetail.from_anime_item(anime, "获取失败")
            detail_view.update_detail(detail)
            self.notify(f"获取详情失败: {e}", severity="error")

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
        self.run_worker(self.start_download(magnet))

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
        self.run_worker(self.load_season_animes)


def run_tui() -> None:
    """启动 TUI"""
    app = AniCatchApp()
    app.run()