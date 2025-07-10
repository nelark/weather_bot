from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from settings import (
    weather_api,
    database,
    user_callback_add_location,
    user_callback_addloc_by_coord_way,
    user_callback_addloc_by_name_way,
)
from keyboards import get_add_location_way_keyboard, get_back_to_main_keyboard


class TextMessages:
    # Общие сообщения
    INVALID_COMMAND_FORMAT = "<i>Неверный формат команды! Введите /help</i>"
    LOCATION_NOT_FOUND = "<i>Локация не найдена :(</i>"
    LOCATION_ADDED = "<i>Локация <b>{name}</b> добавлена</i>"
    LOCATION_EXISTS = "<i>Эта локация уже существует у вас в списке</i>"
    REQUEST_ERROR = "<i>Произошла ошибка при обработке запроса</i>"
    LOCATION_PROCESSING_ERROR = "<i>Произошла ошибка при обработке локации</i>"
    ACTION_CANCELLED = "<i>Действие успешно отменено!</i>"

    # Сообщения для координат
    INVALID_COORDS = "<i>Неверные координаты. Используйте точку как разделитель.</i>"
    WRONG_COORDS_COUNT = "<i>Неверное количество аргументов для координат</i>"
    SEND_LOCATION_PROMPT = (
        "<i>Отправьте свою локацию, чтобы продолжить. Для отмены введите /cancel</i>"
    )

    # Сообщения для callback-ов
    SELECT_METHOD = "<b>Выберите способ добавления локации</b>"
    SEND_COORD_PROMPT = "<b>Отправьте координаты локации или отправьте свое местоположение\nДля отмены действия напишите /cancel</b>"
    SEND_NAME_PROMPT = (
        "<b>Введите название локации\nДля отмены действия напишите /cancel</b>"
    )

    # Аргументы команд
    INVALID_ARGUMENT = "<i>Неверный аргумент команды</i>"


class AddLocationCommandArguments:
    NAME_ARG = "name"
    COORD_ARG = "coord"


class HandleSavingLocation(StatesGroup):
    waiting_for_sending_name = State()
    waiting_for_sending_location = State()


saving_location_router = Router()


@saving_location_router.message(
    Command("cancel"), HandleSavingLocation.waiting_for_sending_location
)
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer(TextMessages.ACTION_CANCELLED)
    await state.clear()


@saving_location_router.message(
    Command("cancel"), HandleSavingLocation.waiting_for_sending_name
)
async def cmd_cancel_name(message: Message, state: FSMContext):
    await message.answer(TextMessages.ACTION_CANCELLED)
    await state.clear()


@saving_location_router.message(Command("add_location"))
async def cmd_add_location(message: Message, command: CommandObject, state: FSMContext):
    args = command.args
    user_chat_id = message.chat.id

    if not args:
        await message.answer(TextMessages.INVALID_COMMAND_FORMAT)
        return

    args = args.split()

    try:
        if args[0] == AddLocationCommandArguments.NAME_ARG and len(args) > 1:
            name_location = " ".join(args[1:])
            coords = await weather_api.get_location_coords(name_location)

            if not coords:
                await message.answer(TextMessages.LOCATION_NOT_FOUND)
                return

            success = await database.add_location(
                name=name_location, user_id=user_chat_id, lat=coords[0], lon=coords[1]
            )

            if success:
                await message.answer(
                    TextMessages.LOCATION_ADDED.format(name=name_location)
                )
            else:
                await message.answer(TextMessages.LOCATION_EXISTS)

        elif args[0] == AddLocationCommandArguments.COORD_ARG:
            if len(args) == 1:
                await message.answer(TextMessages.SEND_LOCATION_PROMPT)
                await state.set_state(HandleSavingLocation.waiting_for_sending_location)
            elif len(args) == 3:
                try:
                    lat, lon = float(args[1]), float(args[2])
                    coords = (lat, lon)
                except ValueError:
                    await message.answer(TextMessages.INVALID_COORDS)
                    return

                exists = await weather_api.exist_location_by_coord(coords)
                if not exists:
                    await message.answer(TextMessages.LOCATION_NOT_FOUND)
                    return

                location_name = await weather_api.get_location_name_by_coord(coords)
                if not location_name:
                    location_name = f"Локация ({coords[0]}, {coords[1]})"

                success = await database.add_location(
                    name=location_name,
                    user_id=user_chat_id,
                    lat=coords[0],
                    lon=coords[1],
                )

                if success:
                    await message.answer(
                        TextMessages.LOCATION_ADDED.format(name=location_name)
                    )
                else:
                    await message.answer(TextMessages.LOCATION_EXISTS)
            else:
                await message.answer(TextMessages.WRONG_COORDS_COUNT)
        else:
            await message.answer(TextMessages.INVALID_ARGUMENT)

    except Exception as e:
        await message.answer(TextMessages.REQUEST_ERROR)
        print(e)


@saving_location_router.callback_query(F.data == user_callback_add_location.pack())
async def show_add_location_keyboard(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        TextMessages.SELECT_METHOD, reply_markup=get_add_location_way_keyboard()
    )


@saving_location_router.callback_query(
    F.data == user_callback_addloc_by_coord_way.pack()
)
async def setting_state_waiting_for_sending_location(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.message.edit_text(
        TextMessages.SEND_COORD_PROMPT, reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(HandleSavingLocation.waiting_for_sending_location)


@saving_location_router.callback_query(
    F.data == user_callback_addloc_by_name_way.pack()
)
async def setting_state_waiting_for_sending_name(
    callback_query: CallbackQuery, state: FSMContext
):
    await callback_query.message.edit_text(
        TextMessages.SEND_NAME_PROMPT, reply_markup=get_back_to_main_keyboard()
    )
    await state.set_state(HandleSavingLocation.waiting_for_sending_name)


@saving_location_router.message(
    F.content_type == ContentType.LOCATION,
    HandleSavingLocation.waiting_for_sending_location,
)
async def get_user_location_and_register_it(message: Message, state: FSMContext):
    try:
        lat = message.location.latitude
        lon = message.location.longitude
        user_chat_id = message.chat.id
        coord = (lat, lon)

        name_location = await weather_api.get_location_name_by_coord(coord)
        if not name_location:
            name_location = f"Локация ({lat:.4f}, {lon:.4f})"

        success = await database.add_location(
            name=name_location, user_id=user_chat_id, lat=lat, lon=lon
        )

        if success:
            await message.answer(TextMessages.LOCATION_ADDED.format(name=name_location))
        else:
            await message.answer(TextMessages.LOCATION_EXISTS)

    except Exception as e:
        await message.answer(TextMessages.LOCATION_PROCESSING_ERROR)
        print(e)
    finally:
        await state.clear()


@saving_location_router.message(HandleSavingLocation.waiting_for_sending_location)
async def get_coord_and_register_it(message: Message, state: FSMContext):
    coords = message.text.split()
    if len(coords) != 2:
        await message.answer(TextMessages.WRONG_COORDS_COUNT)
        return

    user_chat_id = message.chat.id

    try:
        try:
            lat, lon = float(coords[0]), float(coords[1])
            coords = (lat, lon)
        except ValueError:
            await message.answer(TextMessages.INVALID_COORDS)
            return

        exists = await weather_api.exist_location_by_coord(coords)
        if not exists:
            await message.answer(TextMessages.LOCATION_NOT_FOUND)
            return

        location_name = await weather_api.get_location_name_by_coord(coords)
        if not location_name:
            location_name = f"Локация ({coords[0]}, {coords[1]})"

        success = await database.add_location(
            name=location_name,
            user_id=user_chat_id,
            lat=coords[0],
            lon=coords[1],
        )

        if success:
            await message.answer(TextMessages.LOCATION_ADDED.format(name=location_name))
        else:
            await message.answer(TextMessages.LOCATION_EXISTS)
    except Exception as e:
        print(e)
        await message.answer(TextMessages.REQUEST_ERROR)
    finally:
        await state.clear()


@saving_location_router.message(HandleSavingLocation.waiting_for_sending_name)
async def get_name_location_and_register_it(message: Message, state: FSMContext):
    name_location = message.text
    user_chat_id = message.chat.id
    coords = await weather_api.get_location_coords(name_location)

    if not coords:
        await message.answer(TextMessages.LOCATION_NOT_FOUND)
        return

    success = await database.add_location(
        name=name_location, user_id=user_chat_id, lat=coords[0], lon=coords[1]
    )

    if success:
        await message.answer(TextMessages.LOCATION_ADDED.format(name=name_location))
    else:
        await message.answer(TextMessages.LOCATION_EXISTS)
    await state.clear()
