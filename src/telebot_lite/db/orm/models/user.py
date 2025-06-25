from tortoise import fields
from tortoise.models import Model
from telebot_lite.db.orm.mixin import MixinTimestamp

class AbstractTelegramUser(Model, MixinTimestamp):
    telegram_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=64, null=True)
    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=100, null=True)

    class Meta:
        abstract = True
        
        
class TelegramUser(AbstractTelegramUser):
    is_active = fields.BooleanField(default=True)