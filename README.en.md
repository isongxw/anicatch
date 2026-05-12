# AniCatch - Anime Resource Scraper

A Python scraper for miobt.com anime resources. Browse by season, search, and download via BitTorrent.

[中文](README.md) | English

## Acknowledgments

Thanks to [miobt.com](https://miobt.com) for providing the anime resource index.

## Install

### PyPI (recommended)

```bash
pipx install anicatch        # Recommended: isolated install
pip install anicatch         # or standard pip
uv tool install anicatch     # or uv
```

### Run directly (zero install)

```bash
uvx anicatch --search "Demon Slayer"
```

### Dev install

```bash
git clone https://github.com/isongxw/anicatch.git
cd anicatch
uv sync
```

## Usage

Two modes available:

### TUI Mode (interactive)

```bash
anicatch
```

- Browse anime by season (navigate with arrow keys, switch months)
- Keyboard-driven detail view with magnet links
- Download selected resources

### CLI Mode (automation / Agent)

```bash
anicatch --search "Demon Slayer"                               # Search
anicatch --search "Demon Slayer" --download --index 0           # Search and download
anicatch --download "https://miobt.com/show-xxx.html"           # Download by URL
anicatch --seasons                                             # List all seasons
anicatch --season                                              # Browse current season
anicatch --season 1 --download --index 0                        # Download from season
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
