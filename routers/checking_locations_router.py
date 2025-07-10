from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards import UserLocationsKeyboardCreator, get_main_keyboard
from settings import user_callback_location, database, weather_api
from callbacks import UserLocationCallback, PreviousPageCallback, NextPageCallback


class LocationTextMessages:
    NO_LOCATIONS = "<b>У вас пока нет локаций</b>"
    LOCATIONS_TITLE = "<b>Ваши локации</b>"
    TECH_ISSUES = "<b>Тех.неполадки</b>"
    SOMETHING_WRONG = "<b>Что-то пошло не так!</b>"
    CANT_SCROLL = "Невозможно пролистнуть"


checking_locations_router = Router()


@checking_locations_router.message(Command("locations"))
async def cmd_check_locations(message: Message):
    try:
        user_id = message.chat.id
        page = 1
        kb = await UserLocationsKeyboardCreator.get_player_locations_keyboard(
            user_id, page
        )

        if not kb:
            await message.answer(
                LocationTextMessages.NO_LOCATIONS, reply_markup=get_main_keyboard()
            )
            return

        await message.answer(
            LocationTextMessages.LOCATIONS_TITLE,
            reply_markup=kb,
        )
    except Exception as e:
        await message.answer(
            LocationTextMessages.TECH_ISSUES, reply_markup=get_main_keyboard()
        )
        print(e)


@checking_locations_router.callback_query(F.data == user_callback_location.pack())
async def callback_check_locations(callback: CallbackQuery):
    try:
        user_id = callback.message.chat.id
        page = 1
        kb = await UserLocationsKeyboardCreator.get_player_locations_keyboard(
            user_id, page
        )

        if not kb:
            await callback.message.edit_text(
                LocationTextMessages.NO_LOCATIONS, reply_markup=get_main_keyboard()
            )
            return

        await callback.message.edit_text(
            LocationTextMessages.LOCATIONS_TITLE,
            reply_markup=kb,
        )
    except Exception as e:
        await callback.message.edit_text(
            LocationTextMessages.TECH_ISSUES, reply_markup=get_main_keyboard()
        )
        print(e)


@checking_locations_router.callback_query(F.data.contains(UserLocationCallback.__prefix__))
async def callback_check_location(callback: CallbackQuery):
    try:
        data = callback.data.split(":")
        user_id = callback.message.chat.id
        location = data[1]

        coord = await database.get_location_coordinates(location, user_id)
        weather = await weather_api.get_weather_in_location_by_coord(coord)
        if not weather:
            await callback.message.edit_text(LocationTextMessages.SOMETHING_WRONG)
        await callback.message.edit_text(weather, reply_markup=get_main_keyboard())

    except Exception as e:
        await callback.message.edit_text(
            LocationTextMessages.TECH_ISSUES, reply_markup=get_main_keyboard()
        )
        print(e)


@checking_locations_router.callback_query(F.data.contains(NextPageCallback.__prefix__))
async def callback_next_page(callback: CallbackQuery):
    try:
        data = callback.data.split(":")
        user_id = callback.message.chat.id
        cur_page = int(data[1])

        kb = await UserLocationsKeyboardCreator.get_player_locations_keyboard(
            user_id, cur_page + 1
        )
        if kb:
            await callback.message.edit_text(
                LocationTextMessages.LOCATIONS_TITLE,
                reply_markup=kb,
            )
        else:
            await callback.answer(LocationTextMessages.CANT_SCROLL)

    except Exception as e:
        await callback.message.edit_text(
            LocationTextMessages.TECH_ISSUES, reply_markup=get_main_keyboard()
        )
        print(e)


@checking_locations_router.callback_query(F.data.contains(PreviousPageCallback.__prefix__))
async def callback_previous_page(callback: CallbackQuery):
    try:
        data = callback.data.split(":")
        user_id = callback.message.chat.id
        cur_page = int(data[1])

        kb = await UserLocationsKeyboardCreator.get_player_locations_keyboard(
            user_id, cur_page - 1
        )
        if kb:
            await callback.message.edit_text(
                LocationTextMessages.LOCATIONS_TITLE,
                reply_markup=kb,
            )
        else:
            await callback.answer(LocationTextMessages.CANT_SCROLL)

    except Exception as e:
        await callback.message.edit_text(
            LocationTextMessages.TECH_ISSUES, reply_markup=get_main_keyboard()
        )
        print(e)
