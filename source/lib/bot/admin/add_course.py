import os
import logging

from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from lib.bot.filters import AdminFilter
from lib.bot.keyboards import default_inline_kb, GeneralCallback
from lib.postgres.models import Courses, Topics
from lib.postgres.postgres import Postgres

logger = logging.getLogger('courses-bot')
postgres = Postgres(os.environ.get('POSTGRES_URL'), logger)

router = Router(name='add_course')
router.message.filter(AdminFilter(postgres, logger))


class Course(StatesGroup):
    topic = State()
    title = State()
    link = State()
    description = State()
    edit_data = State()


@router.message(Command('add'))
async def add_course(message: Message, state: FSMContext):
    await state.set_state(Course.topic)

    topics = await postgres.get_topics()

    kbs = [{'name': topic.name, 'data': topic.id} for topic in topics]
    kbs.append({'name': '➕', 'data': 0})
    kb = default_inline_kb(tuple(kbs), action='choice_topic')

    await message.answer('Выбери тематику или добавь новую', reply_markup=kb)


@router.callback_query(Course.topic, GeneralCallback.filter(F.action == 'choice_topic'))
async def choice_topic(callback: CallbackQuery, state: FSMContext, callback_data: GeneralCallback):
    if callback_data.data == '0':
        await callback.message.edit_text('Введи название тематики')
        return
    await state.update_data(topic=callback_data.data)
    await state.set_state(Course.title)


@router.message(Course.topic)
async def add_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await state.set_state(Course.title)
    await message.answer('Введи название курса')


@router.message(Course.title)
async def add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(Course.link)
    await message.answer('Введи ссылку на курс')


@router.message(Course.link)
async def add_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await state.set_state(Course.description)
    await state.update_data(update_field='description')
    await message.answer('Введи описание курса')


@router.message(Course.description)
async def add_description(message: Message, state: FSMContext):
    data = await state.get_data()
    data = await state.update_data({data['update_field']: message.text})
    await state.set_state(Course.edit_data)

    kb = default_inline_kb((
        {'name': '✏️Название', 'data': 'title'},
        {'name': '✏️Ссылка', 'data': 'link'},
        {'name': '✏️Описание', 'data': 'description'},
        {'name': '✅Всё верно', 'data': 'ok'}

    ), 'edit_course')

    await message.answer(
        f'Данные корректные?\n'
        f'Название: {data["title"]}\n'
        f'Ссылка: {data["link"]}\n'
        f'Описание: {data["description"]}',
        reply_markup=kb
    )


@router.callback_query(Course.edit_data, GeneralCallback.filter(F.action == 'edit_course'))
async def final_step(callback: CallbackQuery, state: FSMContext, callback_data: GeneralCallback):
    data = await state.update_data(update_field=callback_data.data)
    await state.set_state(Course.description)

    if callback_data.data == 'title':
        await callback.message.edit_text('Введи новое название')
    elif callback_data.data == 'link':
        await callback.message.edit_text('Введи новую ссылку')
    elif callback_data.data == 'description':
        await callback.message.edit_text('Введи новое описание')
    elif callback_data.data == 'ok':
        if data['topic'].isdigit():
            topic = await postgres.get_topic(data['topic'])
        else:
            topic = Topics(name=data['topic'])

        course = Courses(
            link=data["link"],
            title=data["title"],
            description=data["description"]
        )
        course.topic = topic

        await postgres.insert_object(course)
        await callback.message.edit_text(
            'Данные сохранены\n'
            f'Название: {data["title"]}\n'
            f'Ссылка: {data["link"]}\n'
            f'Описание: {data["description"]}'
        )
        await state.clear()
