from aiogram.types import User
from loguru import logger
from tortoise import fields
from tortoise.models import Model

nb = dict(null=True, )


class UserBot(Model):
    id = fields.BigIntField(pk=True)  # telegram_id
    is_bot = fields.BooleanField(default=False)
    first_name = fields.CharField(max_length=256)
    last_name = fields.CharField(max_length=256, **nb)
    username = fields.CharField(max_length=32, **nb)
    language_code = fields.CharField(max_length=256, **nb)
    can_join_groups = fields.BooleanField(default=False)
    can_read_all_group_messages = fields.BooleanField(default=False)
    supports_inline_queries = fields.BooleanField(default=False)
    parent = fields.ForeignKeyField('models.UserBot', null=True, related_name='partners', on_delete=fields.SET_NULL)
    pr_is = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)
    captcha = fields.CharField(max_length=32, **nb)
    partners: list = fields.ReverseRelation["models.UserBot"]

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.id}'

    @classmethod
    async def get_user_and_created(cls, user_data: User):
        """ python-telegram-bot's Update, Context --> User instance """
        data = user_data.to_python()
        data.pop('id')
        u, created = await cls.update_or_create(defaults=data, id=user_data.id)
        logger.info(f"User {u.tg_str} created: {created}")
        return u, created

    @classmethod
    async def get_user(cls, user_data: User):
        u, _ = await cls.get_user_and_created(user_data)
        return u

    @property
    async def get_parent(self):
        if self.parent:
            await self.fetch_related('parent')
            return self.parent

    @property
    async def get_partners(self):
        return await self.partners.filter(pr_is=True).all()

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"
