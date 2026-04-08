# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AniCatch is a Python scraper for miobt.com anime resources. It fetches torrent metadata, supports keyword search, and downloads magnet links via libtorrent.

## Package Manager

Use **uv** (not pip). Install dependencies: `uv sync`. Add packages: `uv add <package>`.

## Commands

```bash
# Run the scraper
uv run anicatch                 # scrape homepage
uv run anicatch --search "关键词"  # search anime
uv run anicatch --test          # test mode (books.toscrape.com)

# Download
uv run anicatch --search "JOJO" --download --index 0
```

## Architecture

`src/anicatch/` contains the main package:
- `__main__.py` — CLI entry point with argparse
- `scraper.py` — HTTP fetching with retry/captcha bypass, HTML parsing with Scrapling
- `downloader.py` — magnet link extraction and libtorrent downloads
- `models.py` — Pydantic models (AnimeItem, CrawlResult)
- `config.py` — constants (URLs, delays, retry config, tracker list)
- `utils.py` — logging setup and JSON output

Flow: CLI → scraper fetches page → parse to AnimeItem → save JSON → optionally download via libtorrent.

## Output

- `output/` — JSON files (anime_data.json, search_*.json)
- `downloads/` — torrent downloads

## Dependencies

Key libraries: scrapling (HTML parsing), curl_cffi (HTTP), pydantic (data validation), loguru (logging), libtorrent (optional, for downloads).

## Python Version

Requires Python 3.10+ (see `.python-version`).