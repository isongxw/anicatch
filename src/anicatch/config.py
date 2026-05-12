"""配置模块"""

from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DOWNLOAD_DIR = BASE_DIR / "downloads"
OUTPUT_FILE = OUTPUT_DIR / "anime_data.json"

# URL 配置
TARGET_URL = "https://miobt.com/"
TEST_URL = "https://books.toscrape.com/"

# 请求配置
REQUEST_DELAY = 2.0  # 基础延迟（秒）
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAYS = [1, 2, 4]  # 重试间隔（秒）

# 下载配置
DOWNLOAD_TIMEOUT = 300  # 下载超时（秒）
DOWNLOAD_PORTS = (6881, 6891)  # BT 端口范围

# 日志配置
LOG_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Tracker 列表
TRACKERS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.bittor.pw:1337/announce",
    "udp://public.popcorn-tracker.org:6969/announce",
    "http://open.acgtracker.com:1096/announce",
]
