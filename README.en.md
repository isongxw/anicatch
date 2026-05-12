# AniCatch - Anime Resource Scraper

A Python scraper for miobt.com anime resources. Browse by season, search, and download via BitTorrent.

[中文](README.md) | English

## Acknowledgments

Thanks to [miobt.com](https://miobt.com) for providing the anime resource index.

## Install

```bash
git clone https://github.com/isongxw/anicatch.git
cd anicatch
uv sync
uv add libtorrent  # required for download
```

## Usage

Two modes available:

### TUI Mode (interactive)

```bash
uv run anicatch
```

- Browse anime by season (navigate with arrow keys, switch months)
- Keyboard-driven detail view with magnet links
- Download selected resources

### CLI Mode (automation / Agent)

```bash
uv run anicatch --search "Demon Slayer"                          # Search
uv run anicatch --search "Demon Slayer" --download --index 0      # Search and download
uv run anicatch --download "https://miobt.com/show-xxx.html"      # Download by URL
uv run anicatch --seasons                                        # List all seasons
uv run anicatch --season                                         # Browse current season
uv run anicatch --season 1 --download --index 0                   # Download from season
```

## Output

- Search results: printed to stdout, also saved to `output/`
- Downloads: `downloads/` directory

## Project Structure

```
src/anicatch/
├── __main__.py      # CLI/TUI entry
├── tui.py           # TUI interface
├── scraper.py       # Scraping & parsing
├── downloader.py    # BT download
├── seasons.py       # Season discovery
├── models.py        # Data models
├── config.py        # Configuration
└── utils.py         # Utilities
```
