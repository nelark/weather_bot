import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from settings import database, BOT_TOKEN

from routers import (
    main_router,
    saving_location_router,
    checking_locations_router,
    checking_weather_router,
    catching_unknown_updates_router,
)

dp = Dispatcher()


async def main() -> None:

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_routers(
        main_router,
        saving_location_router,
        checking_locations_router,
        checking_weather_router,
        catching_unknown_updates_router,
    )

    await database.initialize()

    await dp.start_polling(bot, allowed_updates=["callback_query", "message"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
