import logging
import os

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.exc import IntegrityError

from lib.bot.keyboards import GeneralCallback, menu_inline_keyboard, default_inline_kb
from lib.postgres.models import Users
from lib.postgres.postgres import Postgres

router = Router(name='client')
logger = logging.getLogger('courses-bot')
postgres = Postgres(os.environ.get('POSTGRES_URL'), logger)


@router.message(CommandStart())
async def start_command(message: Message):
    logger.info('Start command')
    await message.answer('Выберите тематику или поиск по названию', reply_markup=menu_inline_keyboard())

    from_user = message.from_user
    try:
        user = Users(
            user_id=from_user.id,
            is_bot=from_user.is_bot,
            first_name=from_user.first_name,
            last_name=from_user.last_name,
            username=from_user.username,
            language_code=from_user.language_code,
            is_premium=from_user.is_premium
        )
        await postgres.insert_object(user)
    except IntegrityError:
        logger.info(f'User exist {from_user.id} - {from_user.first_name}')


@router.callback_query(GeneralCallback.filter(F.action == 'menu'))
async def menu_action(callback: CallbackQuery, callback_data: GeneralCallback):
    if callback_data.data == 'topics':
        topics = await postgres.get_topics()
        kbs = [{'name': topic.name, 'data': topic.id} for topic in topics]
        kb = default_inline_kb(tuple(kbs), action='choice_topic')
        await callback.message.edit_text('Тематики:', reply_markup=kb)
    elif callback_data.data == 'search':
        await callback.message.edit_text('Введи текст поиска')
