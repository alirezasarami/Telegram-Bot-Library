from tortoise.models import Model
from tortoise import fields
from telebot_lite.db.orm.utils.timezone import now_tz


class MixinTimestamp:
    created_at = fields.DatetimeField(default=now_tz)
    updated_at = fields.DatetimeField(default=now_tz)
