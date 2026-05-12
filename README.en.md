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

```bash
# Launch TUI browser
uv run anicatch

# Search
uv run anicatch --search "Demon Slayer"

# Search and download the first result
uv run anicatch --search "Demon Slayer" --download --index 0

# Test mode
uv run anicatch --test
```

## Output

- Search/scrape results: `output/` directory
- Downloaded files: `downloads/` directory

## Project Structure

```
src/anicatch/
├── __main__.py      # CLI entry
├── tui.py           # TUI interface
├── scraper.py       # Scraping & parsing
├── downloader.py    # BT download
├── seasons.py       # Season discovery
├── models.py        # Data models
├── config.py        # Configuration
└── utils.py         # Utilities
```

