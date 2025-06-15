from datetime import datetime
from zoneinfo import ZoneInfo
from telebot_lite.utils.load_settings import load_settings


def get_project_timezone() -> ZoneInfo:
    """
    Load the project's timezone from settings.
    """
    try:
        module = load_settings()
        return ZoneInfo(getattr(module, "TIME_ZONE", ZoneInfo("UTC")))
    except Exception as e:
        return ZoneInfo("UTC")


def now_tz():
    return datetime.now(tz=get_project_timezone())
