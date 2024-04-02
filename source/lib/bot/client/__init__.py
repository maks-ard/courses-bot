from aiogram import Router

from lib.bot.client.client import router as client_router

router = Router(name='client')
router.include_routers(client_router)
