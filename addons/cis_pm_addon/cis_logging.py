# cis_pm_addon/cis_logging.py

import logging
import os
import traceback

LOG_FILENAME = "cis_pm_generator_log.txt"
LOGGER_NAME = "cis_pm_generator"


def get_addon_root() -> str:
    """Return the folder where this add-on (cis_pm_addon) lives."""
    return os.path.dirname(__file__)


def get_log_path() -> str:
    """Absolute path to the cis_pm_generator_log.txt file."""
    return os.path.join(get_addon_root(), LOG_FILENAME)


def setup_logger() -> logging.Logger:
    """
    Configure and return the shared logger.
    - Writes to cis_pm_generator_log.txt (overwritten each run).
    - Safe to call multiple times.
    """
    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(get_log_path(), mode="w", encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Optional: also echo to Blender console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.debug("Logger initialized, writing to %s", get_log_path())
    return logger


def log_exception(logger: logging.Logger, msg: str) -> None:
    """Log an exception with traceback."""
    tb = traceback.format_exc()
    logger.error("%s\n%s", msg, tb)


def open_log_in_text_editor() -> None:
    """
    Load cis_pm_generator_log.txt into the Blender Text Editor.

    - If a text with the same name exists, it is removed and reloaded from disk
      so you always see the latest run.
    """
    try:
        import bpy
    except ImportError:
        # Running outside Blender – nothing to do
        return

    path = get_log_path()
    name = os.path.basename(path)

    # Remove existing text block with same name to force reload
    existing = bpy.data.texts.get(name)
    if existing is not None:
        try:
            bpy.data.texts.remove(existing)
        except RuntimeError:
            # If it's pinned or in use, just leave it
            pass

    if os.path.exists(path):
        try:
            bpy.data.texts.load(path)
        except Exception:
            # As a fallback, create an empty text and write a hint
            txt = bpy.data.texts.new(name=name)
            txt.write("// Could not load log file from disk.\n")
            txt.write(f"// Expected path: {path}\n")
    else:
        # No file yet – create an empty text with a message
        txt = bpy.data.texts.new(name=name)
        txt.write("// Log file not found.\n")
        txt.write(f"// Expected path: {path}\n")
