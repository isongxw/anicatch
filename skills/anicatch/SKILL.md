---
name: anicatch
description: Use when the user asks to search anime torrents, download anime episodes, find anime resources, or browse miobt.com. Triggers on keywords like search anime, download anime, anime torrent, 番剧, 动漫下载, 磁力链接, magnet.
---

# AniCatch

Search and download anime torrents from miobt.com. Zero-install via `uvx`.

## Commands

```bash
uvx --from git+https://github.com/isongxw/anicatch.git anicatch --search "KEYWORD"
uvx --from git+https://github.com/isongxw/anicatch.git anicatch --search "KEYWORD" --download --index 0
uvx --from git+https://github.com/isongxw/anicatch.git anicatch --test
```

## Tips

- English keywords give broader results ("Demon Slayer" over "鬼灭之刃")
- First run downloads ~33 packages into uv cache; subsequent runs are instant
- Downloads use BitTorrent with DHT and public tracker fallback
