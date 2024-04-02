from logging import Logger

from aiogram.filters import Filter
from aiogram.types import Message

from lib.postgres.postgres import Postgres


class AdminFilter(Filter):
    def __init__(self, postgres: Postgres, logger: Logger) -> None:
        self.logger = logger
        self.postgres = postgres

    async def __call__(self, message: Message) -> bool:
        user = await self.postgres.get_user(message.from_user.id)
        if not user.is_admin:
            self.logger.warning('An attempt to use the admin panel without rights', extra={
                'user_id': message.from_user.id,
                'user': message.from_user.username,
                'is_admin': user.is_admin,
                'text': message.text
            })
            return False
        return True
