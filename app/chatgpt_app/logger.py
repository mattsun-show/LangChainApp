import logging
import sys
from typing import Any, Dict, Optional

from colorama import Back, Fore, Style

LOG_LEVEL = logging.INFO


class ColoredFormatter(logging.Formatter):
    """Colored log formatter."""

    def __init__(self, *args: Any, colors: Optional[Dict[str, str]] = None, **kwargs: Any) -> None:
        """Initialize the formatter with specified format strings."""

        super().__init__(*args, **kwargs)

        self.colors = colors if colors else {}

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as text."""

        record.color = self.colors.get(record.levelname, "")
        record.reset = Style.RESET_ALL

        return super().format(record)


def get_logger(name: Optional[str] = None, loglevel: int = LOG_LEVEL) -> logging.Logger:
    logger = logging.getLogger(name)
    # このセルを複数回呼び出しても同じログが重複して出ないようにハンドラの中身をリセット
    # cf: [python loggingメモ - shimo lab2](https://tabeta-log.blogspot.com/2018/04/python-logging.html)
    # cf: [［python］loggerの出力が重複するのを防ぐ - 盆暗の学習記録](https://nigimitama.hatenablog.jp/entry/2021/01/27/084458)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(loglevel)
    handler = logging.StreamHandler(sys.stdout)
    handler_format = ColoredFormatter(
        "{color}{asctime} [{levelname:8}] {name}:{funcName}:{lineno}{reset} {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        colors={
            "DEBUG": Fore.CYAN,
            "INFO": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
        },
    )
    handler.setFormatter(handler_format)
    handler.setLevel(loglevel)
    logger.addHandler(handler)
    # 親のロガーを呼ばないようにすることで重複したログを出さないようにする
    # vars(logger) で親のロガー見れる
    # cf: [[Python]loggingモジュールざっくり理解 - Qiita](https://qiita.com/Kept1994/items/ae2853addb64fdda9139)
    logger.propagate = False
    return logger
