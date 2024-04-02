from aiogram import Router

from lib.bot.admin.add_course import router as add_course_router

router = Router(name='admin')
router.include_routers(add_course_router)
