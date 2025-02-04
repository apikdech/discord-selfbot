from enum import Enum
from datetime import datetime
from typing import Any
import json


class LogLevel(Enum):
    """Log levels with their ANSI color codes."""

    DEBUG = ("\033[36m", "DEBUG")  # Cyan
    INFO = ("\033[32m", "INFO")  # Green
    WARN = ("\033[33m", "WARN")  # Yellow
    ERROR = ("\033[31m", "ERROR")  # Red


class Logger:
    """
    A simple logger with colored output and timestamps.

    Attributes:
        debug_mode (bool): Whether to show debug messages
        RESET (str): ANSI code to reset text color

    Example:
        log = Logger(debug=True)
        log.info("Bot started")
        log.debug("Received payload", some_data)
        log.warn("Rate limit reached")
        log.error("Failed to connect", error)
    """

    RESET = "\033[0m"

    def __init__(self, debug: bool = False):
        """
        Initialize the logger.

        Args:
            debug (bool): Whether to show debug messages
        """
        self.debug_mode = debug

    def _log(self, level: LogLevel, message: str, *args: Any) -> None:
        """
        Internal method to handle logging with consistent formatting.

        Args:
            level (LogLevel): The log level
            message (str): The message to log
            *args: Additional data to log (will be JSON formatted)
        """
        # Skip debug messages if debug mode is off
        if level == LogLevel.DEBUG and not self.debug_mode:
            return

        # Get current timestamp with timezone
        timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S.%f%z")
        # Truncate microseconds to 3 digits and format timezone
        if len(timestamp) >= 26:  # Make sure we have timezone info
            timestamp = (
                timestamp[:23] + timestamp[-5:]
            )  # Keep only 3 digits of microseconds
            timestamp = (
                timestamp[:-2] + ":" + timestamp[-2:]
            )  # Format timezone with colon

        # Format the message with color
        color, level_name = level.value
        log_message = f"{color}[{timestamp}] [{level_name}] {message}{self.RESET}"

        # Print the message
        print(log_message)

        # Print additional data if provided
        if args:
            for arg in args:
                if isinstance(arg, (dict, list)):
                    # Pretty print JSON data
                    print(f"{color}  {json.dumps(arg, indent=2)}{self.RESET}")
                else:
                    # Print other types directly
                    print(f"{color}  {str(arg)}{self.RESET}")

    def debug(self, message: str, *args: Any) -> None:
        """
        Log a debug message.

        Args:
            message (str): The message to log
            *args: Additional data to log
        """
        self._log(LogLevel.DEBUG, message, *args)

    def info(self, message: str, *args: Any) -> None:
        """
        Log an info message.

        Args:
            message (str): The message to log
            *args: Additional data to log
        """
        self._log(LogLevel.INFO, message, *args)

    def warn(self, message: str, *args: Any) -> None:
        """
        Log a warning message.

        Args:
            message (str): The message to log
            *args: Additional data to log
        """
        self._log(LogLevel.WARN, message, *args)

    def error(self, message: str, *args: Any) -> None:
        """
        Log an error message.

        Args:
            message (str): The message to log
            *args: Additional data to log
        """
        self._log(LogLevel.ERROR, message, *args)
