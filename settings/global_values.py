import os

from settings.settings import Settings
from database import SqlliteDatabase
from api import WeatherApi
from callbacks import UserCallback

# иницилизация настроек для получения некоторых констант
settings = Settings()

# константы для иницилизации ключевых частей бота
DATABASE_FILE_PATH = os.path.join("resourses", "sqlite.db")
BOT_TOKEN = settings.bot_token.get_secret_value()
WEATHER_API_TOKEN = settings.weather_api_token.get_secret_value()

database = SqlliteDatabase(DATABASE_FILE_PATH)
weather_api = WeatherApi(WEATHER_API_TOKEN)

# callbacks для main_keyboard(меню)
user_callback_help = UserCallback(action="show_help")
user_callback_weather = UserCallback(action="check_weather")
user_callback_location = UserCallback(action="show_locations")
user_callback_add_location = UserCallback(action="add_location")
user_callback_back_to_main_keyboard = UserCallback(action="back_to_main_keyboard")

# callbacks для check_weather_way_keyboard
user_callback_weather_by_name_way = UserCallback(action="check_weather_by_name")
user_callback_weather_by_coord_way = UserCallback(action="check_weather_by_coord")

# callbacks для add_location_way_keyboard
user_callback_addloc_by_name_way = UserCallback(action="add_location_by_name")
user_callback_addloc_by_coord_way = UserCallback(action="add_location_by_coord")