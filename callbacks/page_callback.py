from aiogram.filters.callback_data import CallbackData


class NextPageCallback(CallbackData, prefix="next_page"):
    cur_page: int


class PreviousPageCallback(CallbackData, prefix="previous_page"):
    cur_page: int
