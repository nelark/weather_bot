from aiogram.filters.callback_data import CallbackData

class UserLocationCallback(CallbackData, prefix='user_location'):
    location_name: str