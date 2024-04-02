from typing import Any

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class GeneralCallback(CallbackData, prefix='admin'):
    action: str
    data: Any


def default_inline_kb(buttons: tuple, action: str, size: int = None) -> InlineKeyboardMarkup:
    if size is None:
        size = 1

    builder = InlineKeyboardBuilder()

    for button in buttons:
        builder.button(
            text=button['name'],
            callback_data=GeneralCallback(
                action=action,
                data=button['data']
            ).pack())

    builder.adjust(size)

    return builder.as_markup()


def menu_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='Тематики', callback_data=GeneralCallback(action='menu', data='topics').pack())
    builder.button(text='Поиск 🔍', callback_data=GeneralCallback(action='menu', data='search').pack())

    builder.adjust(1)

    return builder.as_markup()
