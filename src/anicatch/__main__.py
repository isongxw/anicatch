"""CLI 入口点"""

from .tui import run_tui


def main_cli() -> None:
    """主入口函数"""
    run_tui()


if __name__ == "__main__":
    main_cli()