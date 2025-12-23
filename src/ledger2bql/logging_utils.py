"""
Logging utilities for ledger2bql using loguru for beautiful, structured logging.
"""

import sys
from typing import Optional, Any


class _NullLogger:
    """A null logger that does nothing - used when logging is disabled."""
    
    def debug(self, *args, **kwargs):
        pass
    
    def info(self, *args, **kwargs):
        pass
    
    def warning(self, *args, **kwargs):
        pass
    
    def error(self, *args, **kwargs):
        pass
    
    def exception(self, *args, **kwargs):
        pass
    
    def critical(self, *args, **kwargs):
        pass
    
    def bind(self, **kwargs):
        return self


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """
    Set up logging using loguru with beautiful formatting.
    
    Args:
        verbose: Enable verbose debug logging
        log_file: Optional path to log file for file logging
    """
    # If not verbose, return a null logger immediately - no loguru import
    if not verbose:
        return _NullLogger()
    
    # Only import loguru when verbose mode is enabled
    try:
        from loguru import logger
        
        # Remove default handler to customize
        logger.remove()
        
        # Add console handler with beautiful formatting
        console_format = (
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        
        logger.add(
            sys.stderr,
            level="DEBUG",
            format=console_format,
            colorize=True,
            diagnose=False  # Disable slow diagnostics for performance
        )
        
        # Add file handler if log file is specified
        if log_file:
            file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
            logger.add(
                log_file,
                level="DEBUG",
                format=file_format,
                colorize=False,
                rotation="10 MB",  # Rotate logs at 10MB
                retention="7 days"  # Keep logs for 7 days
            )
        
        logger.debug("Logging initialized")
        return logger
        
    except ImportError:
        # Fallback to standard logging if loguru is not available
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr
        )
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
        
        logger = logging.getLogger(__name__)
        logger.debug("Logging initialized (fallback to standard logging)")
        return logger


def get_logger(name: str = __name__):
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Name for the logger
    
    Returns:
        Logger instance (or null logger if logging is disabled)
    """
    # Always return a null logger from get_logger()
    # The main module will have the real logger when verbose is enabled
    return _NullLogger()


def log_environment_info():
    """
    Log key environment information for debugging.
    """
    import os
    logger = get_logger(__name__)
    
    logger.debug("=== Environment Information ===")
    logger.debug(f"BEANCOUNT_FILE: {os.getenv('BEANCOUNT_FILE')}")
    logger.debug(f"Current working directory: {os.getcwd()}")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Platform: {sys.platform}")
    
    # Log all environment variables that start with common prefixes
    env_vars = {k: v for k, v in os.environ.items() 
                if k.startswith(('BEAN', 'LEDGER', 'BQL')) or 'FILE' in k}
    for key, value in env_vars.items():
        logger.debug(f"ENV {key}: {value}")