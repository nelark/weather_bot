from typing import Optional, List, Tuple
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks import UserLocationCallback, NextPageCallback, PreviousPageCallback
from settings import (
    user_callback_weather,
    user_callback_add_location,
    user_callback_help,
    user_callback_location,
    user_callback_back_to_main_keyboard,
    user_callback_weather_by_name_way,
    user_callback_weather_by_coord_way,
    user_callback_addloc_by_name_way,
    user_callback_addloc_by_coord_way,
    database,
)


class UserLocationsKeyboardCreator:
    KB_SIZE = 6
    ADJUST_SIZE = 3

    @classmethod
    async def get_player_locations_keyboard(
        cls,
        user_id: int,
        page: int,
    ) -> Optional[InlineKeyboardMarkup]:
        locations = await cls._get_page_locations(user_id, page)
        if not locations:
            return None
        total_pages = len(locations)

        location_buttons = [
            [
                InlineKeyboardButton(
                    text=location,
                    callback_data=UserLocationCallback(location_name=location).pack(),
                )
            ]
            for location in locations
        ]

        nav_buttons = cls._create_navigation_buttons(page, total_pages)

        builder = InlineKeyboardBuilder(location_buttons + [nav_buttons])
        builder.adjust(cls.ADJUST_SIZE)

        return builder.as_markup()

    @classmethod
    async def _get_page_locations(cls, user_id: int, page: int) -> List[str]:
        all_locations = await database.get_user_locations(user_id)
        if not all_locations:
            return []

        # Разбиваем на страницы
        chunks = [
            all_locations[i : i + cls.KB_SIZE]
            for i in range(0, len(all_locations), cls.KB_SIZE)
        ]

        if page < 1 or page > len(chunks):
            return []

        return chunks[page - 1]

    @classmethod
    def _create_navigation_buttons(
        cls, current_page: int, total_pages: int
    ) -> List[InlineKeyboardButton]:
        buttons = []

        if current_page > 1:
            buttons.append(
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=PreviousPageCallback(cur_page=current_page).pack(),
                )
            )

        buttons.append(
            InlineKeyboardButton(
                text="📱 Меню", callback_data=user_callback_back_to_main_keyboard.pack()
            )
        )

        if current_page < total_pages:
            buttons.append(
                InlineKeyboardButton(
                    text="Вперед ➡️",
                    callback_data=NextPageCallback(cur_page=current_page).pack(),
                )
            )

        return buttons


def get_main_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Помощь 🤔", callback_data=user_callback_help.pack()
            ),
            InlineKeyboardButton(
                text="Узнать погоду 🌤️", callback_data=user_callback_weather.pack()
            ),
        ],
        [
            InlineKeyboardButton(
                text="Мои локации 🌍", callback_data=user_callback_location.pack()
            ),
            InlineKeyboardButton(
                text="Добавить локацию 📰",
                callback_data=user_callback_add_location.pack(),
            ),
        ],
    ]

    inline_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    return inline_kb


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Меню 📱",
                callback_data=user_callback_back_to_main_keyboard.pack(),
            )
        ],
    ]

    inline_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    return inline_kb


def get_check_weather_way_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="По имени 📰",
                callback_data=user_callback_weather_by_name_way.pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="По локации/координатам 🌏",
                callback_data=user_callback_weather_by_coord_way.pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Меню 📱",
                callback_data=user_callback_back_to_main_keyboard.pack(),
            )
        ],
    ]

    inline_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    return inline_kb


def get_add_location_way_keyboard() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="По имени 📰",
                callback_data=user_callback_addloc_by_name_way.pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="По локации/координатам 🌏",
                callback_data=user_callback_addloc_by_coord_way.pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Меню 📱",
                callback_data=user_callback_back_to_main_keyboard.pack(),
            )
        ],
    ]

    inline_kb = InlineKeyboardMarkup(inline_keyboard=kb)
    return inline_kb
