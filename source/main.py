import argparse
import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from pythonjsonlogger import jsonlogger

from lib.bot.client import router as client_router
from lib.bot.admin import router as admin_router
from lib.bot.middleware import LogMessageMiddleware
from lib.postgres.postgres import Postgres


class Service:
    def __init__(self, logger, args):
        self.logger = logger
        self.args = args

        self.postgres = Postgres(self.args.postgres_url, self.logger)

        self.bot = Bot(os.getenv('TOKEN'))
        self.dp = Dispatcher()

    async def start(self):
        self.logger.info('Start')
        # await self.postgres.drop_tables()
        # await self.postgres.create_tables()

        self.dp.message.outer_middleware.register(
            LogMessageMiddleware(self.logger, -1002050723063)
        )
        self.dp.include_router(client_router)
        self.dp.include_router(admin_router)

        self.logger.info('Start polling')
        await self.dp.start_polling(self.bot, logger=self.logger)


def _get_logger(level: int) -> logging.Logger:
    class LogFilter(logging.Filter):
        def filter(self, record):
            record.service = 'courses-bot'
            return True

    log = logging.getLogger('courses-bot')
    log.setLevel(level * 10)

    stream_handler = logging.StreamHandler(sys.stdout)

    log_format = "%(levelname)-8s %(filename)s %(asctime)s %(lineno)d %(message)s"
    formatter = jsonlogger.JsonFormatter(
        fmt=log_format, json_ensure_ascii=False
    )

    stream_handler.setFormatter(formatter)

    log.addHandler(stream_handler)
    log.addFilter(LogFilter())

    return log


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--postgres_url',
        default=os.getenv('POSTGRES_URL')
    )

    parser.add_argument(
        '--admin_chat',
        default=os.getenv('ADMIN_CHAT')
    )

    parser.add_argument(
        '--token',
        default=os.getenv('TOKEN')
    )

    parser.add_argument(
        '--loglevel',
        default=2,
        type=int
    )

    return parser


if __name__ == "__main__":
    _args = _parse_args().parse_args()
    _logger = _get_logger(_args.loglevel)

    service = Service(_logger, _args)

    try:
        asyncio.run(service.start())

    except KeyboardInterrupt:
        _logger.info('Force stopping')

    except Exception as ex:
        _logger.critical('Critical error', extra={
            'ex': ex
        })
