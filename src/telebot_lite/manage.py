# telebot_lite/manage.py
import sys
import os

sys.path.append(os.getcwd())
import argparse
import asyncio
import os
import importlib
from tortoise import Tortoise
from typing import Optional

DEFAULT_DB_URL = "sqlite://telebot.db"
DEFAULT_MODELS = ["telebot_lite.db.orm"]


def get_args():
    parser = argparse.ArgumentParser(description="Tortoise ORM DB Manager")
    parser.add_argument("action", choices=["init", "drop", "reset"], help="DB action")
    parser.add_argument("--db", type=str, help="Database URL (override settings)")
    parser.add_argument("--models", type=str, help="Comma-separated model list")
    parser.add_argument("--settings", type=str, default="core.settings", help="Settings module to load")
    return parser.parse_args()


def load_settings(settings_path: str) -> Optional[object]:
    try:
        module = importlib.import_module(settings_path)
        return getattr(module, "setttings", None)
    except Exception as e:
        print(f"⚠️ Warning: Failed to import settings from '{settings_path}': {e}")
        return None


async def init_db(db_url, modules):
    await Tortoise.init(db_url=db_url, modules=modules)
    await Tortoise.generate_schemas()


async def drop_db(db_url, modules):
    await Tortoise.init(db_url=db_url, modules=modules)
    conn = Tortoise.get_connection("default")
    for model in Tortoise.apps.get("models", {}).values():
        table = model._meta.db_table
        await conn.execute_script(f'DROP TABLE IF EXISTS "{table}" CASCADE;')


def build_db_url_from_dict(config: dict) -> str:
    engine = config.get("ENGINE")
    if engine == "django.db.backends.postgresql":
        return f"postgres://{config['USER']}:{config['PASSWORD']}@{config['HOST']}:{config['PORT']}/{config['NAME']}"
    elif engine == "django.db.backends.sqlite3":
        return f"sqlite://{config['NAME']}"
    raise ValueError(f"Unsupported DB engine: {engine}")


async def main():
    args = get_args()

    # تلاش برای لود تنظیمات پروژه
    settings = load_settings(args.settings)

    # استخراج db_url
    if args.db:
        db_url = args.db
    elif settings:
        db_url = getattr(settings, "DATABASE_URL", None)
        if not db_url and hasattr(settings, "DATABASE"):
            db_url = build_db_url_from_dict(settings.DATABASE["default"])
    else:
        db_url = DEFAULT_DB_URL

    # استخراج مدل‌ها
    if args.models:
        model_list = args.models.split(",")
    elif settings and hasattr(settings, "MODELS"):
        model_list = settings.MODELS
    else:
        model_list = DEFAULT_MODELS

    modules = {"models": model_list}

    if args.action == "init":
        await init_db(db_url, modules)
        print(f"✅ Database initialized at {db_url}")
    elif args.action == "drop":
        await drop_db(db_url, modules)
        print("🗑️ All tables dropped.")
    elif args.action == "reset":
        await drop_db(db_url, modules)
        await init_db(db_url, modules)
        print("🔄 Database reset.")


if __name__ == "__main__":
    asyncio.run(main())
