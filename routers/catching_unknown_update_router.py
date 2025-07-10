from aiogram import Router
from aiogram.types import Message, CallbackQuery

catching_unknown_updates_router = Router()


@catching_unknown_updates_router.message()
async def catch_unknown_message(message: Message):
    await message.answer("Неизвестная команда")


@catching_unknown_updates_router.callback_query()
async def catch_unknown_message(callback: CallbackQuery):
    await callback.answer("Ошибка")
