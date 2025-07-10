from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from settings import weather_api
from keyboards import get_main_keyboard, get_back_to_main_keyboard
from settings import user_callback_help, user_callback_back_to_main_keyboard


class TextMessages:
    # мне лень полностью писать /help, большей части комманд тут нет
    TEXT_HELP = """
<b>Список команд 📰</b>

<b>/weather_name  имя локации:</b> <i>погода в локации по названию.</i>

При вводе названия локации желательно оставлять как можно больше деталей:
- государство
- регион
- населенный пункт и т.д

<i><b>Пример использования:</b></i>
<i>    /weather_name Россия, Московская область, Москва</i>

<b>/weather_coord  широта  долгота:</b> <i>погода в локации по координатам.</i>

При вводе десятичных чисел необходимо в качестве разделителя использовать точку.

<i><b>Пример использования:</b></i>
<i>    /weather_coord 55.7522 37.6156</i>
    """

    TEXT_MENU = "<b>Меню 😎</b>"


main_router: Router = Router()


@main_router.message(CommandStart())
@main_router.message(Command("menu"))
async def cmd_menu_handler(message: Message) -> None:
    await message.answer(TextMessages.TEXT_MENU, reply_markup=get_main_keyboard())


@main_router.message(Command("help"))
async def cmd_help_handler(message: Message) -> None:
    await message.answer(TextMessages.TEXT_HELP)


@main_router.callback_query(F.data == user_callback_back_to_main_keyboard.pack())
async def callback_menu_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        TextMessages.TEXT_MENU, reply_markup=get_main_keyboard()
    )


@main_router.callback_query(F.data == user_callback_help.pack())
async def callback_help_handler(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        TextMessages.TEXT_HELP, reply_markup=get_back_to_main_keyboard()
    )
