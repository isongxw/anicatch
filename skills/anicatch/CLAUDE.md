# AniCatch Skill

Anime resource scraper for miobt.com. Search anime, browse by season, download via BitTorrent.

TRIGGER when: user asks to search anime resources, download anime torrents, find anime episodes, or browse miobt.com content.

## Usage

All commands use `uvx` — no install needed. The tool auto-installs on first run.

```bash
uvx --from git+https://github.com/isongxw/anicatch.git anicatch --search "KEYWORD"
```

## Commands

| Command | Description |
|---|---|
| `--search "KEYWORD"` | Search anime resources on miobt.com |
| `--search "KEYWORD" --download --index N` | Search and download the Nth result (0-based) |
| `--test` | Test mode (books.toscrape.com, no captcha) |

## Search Tips

- Use English keywords for broader results (e.g., "Demon Slayer" over "鬼灭之刃")
- Use short keywords for more matches (e.g., "JOJO" over full title)
- Results saved to JSON in output/ directory, downloads in downloads/

## Limitations

- Download requires libtorrent (auto-installed via uvx)
- Seeders may be zero on miobt tracker; DHT + public trackers are used as fallback
- Site structure changes may break parsing
