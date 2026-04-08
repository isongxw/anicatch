# AniCatch TUI Feature Design

## Overview

Replace the current CLI with a textual TUI interface for browsing anime resources by season/month, viewing details with magnet links, and downloading.

## Module Structure

```
src/anicatch/
├── __main__.py      # TUI entry point (replaces CLI)
├── config.py        # Configuration (unchanged)
├── models.py        # Data models (add SeasonInfo, AnimeDetail)
├── scraper.py       # Scraping functions (add parse_seasons())
├── downloader.py    # Download functions (unchanged)
├── utils.py         # Utilities (unchanged)
├── seasons.py       # NEW: Season/month discovery and parsing
└── tui.py           # NEW: TUI implementation with textual
```

**New module responsibilities:**
- `seasons.py` — Parse season/month category links from homepage, fetch anime list for specified season
- `tui.py` — Textual application: anime list display, season switching, detail view, download
- `models.py` — Add `SeasonInfo` (season metadata), `AnimeDetail` (with magnet link)

## Data Flow

**Startup:**
1. Program starts → detect current season from system date
2. Call `parse_seasons()` to get all season/month entry links from homepage
3. Fetch current season anime list → display in TUI main view

**User operations:**
1. Browse anime list — shows title, size, publish time, scrollable
2. Switch season — press `←`/`→` to change season
3. Switch month — press `[`/`]` to change month within season
4. Select anime — press `Enter` to enter detail view
5. View details — shows full info + fetch magnet link on demand
6. Download — press `D` in detail view to start download, or `Esc` to return

## Keybindings

| Key | Action |
|-----|--------|
| `↑`/`↓` | Scroll anime list |
| `←`/`→` | Switch season |
| `[`/`]` | Switch month |
| `Enter` | View details |
| `D` | Download current anime |
| `R` | Retry/reload |
| `Esc` | Return to previous level |
| `Q` | Quit program |

## TUI Layout

**Main view (anime list):**

```
┌─ AniCatch ─────────────────────────────────────────────────────┐
│ 季度: 2026年春季 ◀ ▶                    月份: 4月 [ ]         │
├─────────────────────────────────────────────────────────────────┤
│ ┌─ 番剧列表 ──────────────────────────────────────────────────┐│
│ │ [1] 【喵萌奶茶屋】JOJO的奇妙冒险...    2.1GB   今天 22:13    ││
│ │ [2] 【动漫国】海贼王 第1100集...       400MB   今天 21:00    ││
│ │ [3] 【悠哈C9】间谍过家家 S2...         1.5GB   昨天 18:30    ││
│ │ ...                                                        ││
│ └─────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│ 操作: ↑↓滚动 | ←→切换季度 | Enter详情 | Q退出                   │
└─────────────────────────────────────────────────────────────────┘
```

**Detail view:**

```
┌─ 番剧详情 ─────────────────────────────────────────────────────┐
│ 标题: 【喵萌奶茶屋】JOJO的奇妙冒险 石之海 Part3 完结             │
│ 大小: 2.1 GB                                                    │
│ 发布: 今天 22:13                                                │
│ 分类: 动画                                                      │
│ 上传者: 喵萌奶茶屋                                              │
│ 种子数: 128  |  下载数: 45                                      │
├─────────────────────────────────────────────────────────────────┤
│ Magnet: magnet:?xt=urn:btih:abc123...                          │
├─────────────────────────────────────────────────────────────────┤
│ 操作: D下载 | Esc返回 | Q退出                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Season Discovery Logic

**Season entry discovery (`seasons.py`):**
- Parse season/month category links from homepage HTML
- Extract URL and name (e.g., "2026年春季", "4月")
- Generate structure: year → season → month → URL

**Current season detection:**
- Based on system date:
  - Spring: March-May (3-5)
  - Summer: June-August (6-8)
  - Autumn: September-November (9-11)
  - Winter: December-February (12-2)
- Default load: current season, current month

**Season switching:**
- `←`/`→` switches season → re-fetch that season's homepage URL
- `[`/`]` switches month within season (if available)
- After switch: re-fetch and refresh list

## Data Models

```python
class SeasonInfo(BaseModel):
    name: str          # "2026年春季"
    year: int          # 2026
    season: str        # "春"/"夏"/"秋"/"冬"
    months: list[str]  # ["3月", "4月", "5月"]
    url: str           # Season entry URL

class AnimeDetail(BaseModel):
    # Inherits all AnimeItem fields
    # Plus magnet_link field
```

## Error Handling

| Scenario | Handling |
|----------|----------|
| Network failure | Show error message, user can press `R` to retry |
| Captcha bypass fail | Prompt user to handle manually or skip |
| Magnet link fetch fail | Show "获取失败" in detail view, don't block other info |
| libtorrent not installed | Show install command, disable download button |
| Empty list | Show "当前季度无数据", allow switching seasons |

## Dependencies

**New dependency:**
- `textual` — TUI framework (required)

**Existing (unchanged):**
- `scrapling` — HTML parsing
- `curl_cffi` — HTTP requests
- `pydantic` — Data validation
- `loguru` — Logging
- `libtorrent` — BT download (optional)

## Performance Considerations

- Season switch triggers re-fetch, don't preload all seasons (avoid excessive requests)
- Magnet link fetched only when entering detail view (on-demand)
- List data kept in memory, only re-fetch on season change

## Success Criteria

1. User can browse anime by season/month with keyboard navigation
2. Current season is displayed by default on startup
3. Anime details show magnet link for download
4. Download works from detail view with progress display
5. Error states are handled gracefully with retry option