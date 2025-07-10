from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from settings import (
    weather_api,
    user_callback_weather,
    user_callback_weather_by_name_way,
    user_callback_weather_by_coord_way,
)
from keyboards import get_check_weather_way_keyboard, get_back_to_main_keyboard


class TextMessages:
    # Общие сообщения
    RESPONSE_EXCEPTION = "<i>Ошибка при обработке запроса</i>"
    LOCATION_NOT_FOUND = "<i>Не удалось распознать локацию :(. Попробуйте снова!</i>"
    TECH_ISSUES = "<b>Тех.неполадки</b>"

    # Сообщения для weather_coord
    ENTER_COORDS = "<i>Введите координаты!</i>"
    WRONG_COORDS_FORMAT = "<i>Неверный формат команды.</i>"
    INVALID_COORDS = "<i>Неверные аргументы команды. Также обратите внимание на то, что десятичные числа должны быть записаны с точкой, а не с запятой.</i>"

    # Сообщения для состояний
    SELECT_METHOD = "<b>Выберите способ определения погоды</b>"
    ENTER_LOCATION_NAME = "<b>Введите название локации\nДля отмены напишите /cancel</b>"
    ENTER_COORDS_OR_LOCATION = "<b>Введите координаты локации или отправьте свое местоположение\nДля отмены напишите /cancel</b>"
    LOCATION_NOT_DETERMINED = "<b>Не удалось определить локацию :(</b>"
    CANCEL_SUCCESS = "<i>Действие успешно отменено!</i>"


class HandleCheckingWeather(StatesGroup):
    waiting_for_name = State()
    waiting_for_coord = State()


checking_weather_router = Router()


@checking_weather_router.message(Command("cancel"), HandleCheckingWeather.waiting_for_name)
@checking_weather_router.message(
    Command("cancel"), HandleCheckingWeather.waiting_for_coord
)
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer(TextMessages.CANCEL_SUCCESS)
    await state.clear()


@checking_weather_router.message(Command("weather_name"))
async def cmd_get_weather_by_name(message: Message, command: CommandObject):
    name_location = command.args

    try:
        if name_location is not None:
            output = await weather_api.get_weather_in_location_by_name(name_location)
            if output:
                await message.answer(output)
                return
    except Exception as e:
        print(e)
        await message.answer(TextMessages.RESPONSE_EXCEPTION)
        return

    await message.answer(TextMessages.LOCATION_NOT_FOUND)


@checking_weather_router.message(Command("weather_coord"))
async def cmd_get_weather_by_coord(message: Message, command: CommandObject):
    coords = command.args

    if not coords:
        await message.answer(TextMessages.ENTER_COORDS)
        return

    coords = coords.split()
    if len(coords) != 2:
        await message.answer(TextMessages.WRONG_COORDS_FORMAT)
        return

    try:
        lat = float(coords[0])
        lon = float(coords[1])
        coord = (lat, lon)
    except ValueError:
        await message.answer(TextMessages.INVALID_COORDS)
        return

    try:
        output = await weather_api.get_weather_in_location_by_coord(coord)
    except Exception as e:
        print(e)
        await message.answer(TextMessages.RESPONSE_EXCEPTION)
        return

    if output:
        await message.answer(output)
    else:
        await message.answer(TextMessages.LOCATION_NOT_FOUND)


@checking_weather_router.callback_query(F.data == user_callback_weather.pack())
async def callback_get_weather(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        TextMessages.SELECT_METHOD, reply_markup=get_check_weather_way_keyboard()
    )


@checking_weather_router.callback_query(F.data == user_callback_weather_by_name_way.pack())
async def callback_get_weather_by_name(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.message.edit_text(
        TextMessages.ENTER_LOCATION_NAME, reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(HandleCheckingWeather.waiting_for_name)


@checking_weather_router.callback_query(
    F.data == user_callback_weather_by_coord_way.pack()
)
async def callback_get_weather_by_coord(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.message.edit_text(
        TextMessages.ENTER_COORDS_OR_LOCATION, reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(HandleCheckingWeather.waiting_for_coord)


@checking_weather_router.message(HandleCheckingWeather.waiting_for_name)
async def state_get_name_location(message: Message, state: FSMContext):
    text = message.text

    try:
        weather = await weather_api.get_weather_in_location_by_name(text)
        if weather:
            await message.answer(weather, reply_markup=get_back_to_main_keyboard())
        else:
            await message.answer(
                TextMessages.LOCATION_NOT_DETERMINED,
                reply_markup=get_back_to_main_keyboard(),
            )
    except Exception as e:
        await message.answer(
            TextMessages.TECH_ISSUES, reply_markup=get_back_to_main_keyboard()
        )
        print(e)
    finally:
        await state.clear()


@checking_weather_router.message(HandleCheckingWeather.waiting_for_coord)
async def state_get_coord_location(message: Message, state: FSMContext):
    location = message.location
    text = message.text

    try:
        if location:
            lat = message.location.latitude
            lon = message.location.longitude
            coord = (lat, lon)

            weather = await weather_api.get_weather_in_location_by_coord(coord)
            if weather:
                await message.answer(weather, reply_markup=get_back_to_main_keyboard())
            else:
                await message.answer(
                    TextMessages.LOCATION_NOT_DETERMINED,
                    reply_markup=get_back_to_main_keyboard(),
                )
        elif text:
            text = text.split()
            if len(text) == 2:
                try:
                    lat = float(text[0])
                    lon = float(text[1])
                    coord = (lat, lon)

                    weather = await weather_api.get_weather_in_location_by_coord(coord)
                    if weather:
                        await message.answer(
                            weather, reply_markup=get_back_to_main_keyboard()
                        )
                    else:
                        await message.answer(
                            TextMessages.LOCATION_NOT_DETERMINED,
                            reply_markup=get_back_to_main_keyboard(),
                        )
                    await state.clear()
                except ValueError:
                    await message.answer(
                        TextMessages.INVALID_COORDS,
                        reply_markup=get_back_to_main_keyboard(),
                    )
            else:
                await message.answer(
                    TextMessages.ENTER_COORDS, reply_markup=get_back_to_main_keyboard()
                )
                return
    except Exception as e:
        await message.answer(
            TextMessages.TECH_ISSUES, reply_markup=get_back_to_main_keyboard()
        )
        print(e)
