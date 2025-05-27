import importlib
from typing import Optional


def load_settings() -> Optional[object]:
    try:
        module = importlib.import_module("core.settings")
        return getattr(module, "setttings", None)
    except Exception as e:
        print(f"⚠️ Warning: Failed to import settings from 'core.settings': {e}")
        return None