import aiohttp
from typing import Optional, Tuple


class WeatherApi:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, api_key: str = None) -> None:
        self._api_key = api_key

    @classmethod
    def get_instance(cls, api_key: str) -> "WeatherApi":
        if cls._instance is None:
            cls._instance = cls(api_key)
        return cls._instance

    async def get_weather_in_location_by_name(
        self, location_name: str
    ) -> Optional[str]:
        params = {
            "q": location_name,
            "lang": "ru",
            "units": "metric",
            "appid": self._api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.BASE_URL, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return self._format_weather_data(response_data)
                return None

    async def get_weather_in_location_by_coord(
        self, coord: Tuple[float, float]
    ) -> Optional[str]:
        if (
            len(coord) != 2
            or not isinstance(coord[0], (int, float))
            or not isinstance(coord[1], (int, float))
        ):
            return None

        lat, lon = coord[0], coord[1]

        params = {
            "lat": lat,
            "lon": lon,
            "lang": "ru",
            "units": "metric",
            "appid": self._api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.BASE_URL, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return self._format_weather_data(response_data)
                return None

    def _format_weather_data(self, weather_data: dict) -> str:
        code = weather_data.get("cod", None)

        if code == 200:
            coord = weather_data["coord"]
            main = weather_data["main"]
            weather = weather_data["weather"][0]

            location_name = weather_data["name"]
            lat, lon = coord["lat"], coord["lon"]

            temp, feels_like = main["temp"], main["feels_like"]
            description = weather["description"]
            wind_speed = weather_data["wind"]["speed"]

            return f"""
<b>Локация {location_name}</b> 🏙️

<b>Координаты 🌏</b>:
<i>широта: {lat}</i>
<i>долгота: {lon}</i>

<b>Погода ☁️</b>

<i>{description}</i>

<i>температура: {temp}℃</i>
<i>ощущается как: {feels_like}℃</i>
<i>скорость ветра: {wind_speed} м/c</i>
"""
        return "Не удалось извлечь данные :("

    async def get_location_coords(
        self, location_name: str
    ) -> Optional[Tuple[float, float]]:
        params = {
            "q": location_name,
            "lang": "ru",
            "units": "metric",
            "appid": self._api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.BASE_URL, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    coord = response_data["coord"]
                    lat, lon = coord["lat"], coord["lon"]
                    return (lat, lon)
                return None

    async def exist_location_by_coord(self, coord: Tuple[float, float]) -> bool:
        if (
            len(coord) != 2
            or not isinstance(coord[0], (int, float))
            or not isinstance(coord[1], (int, float))
        ):
            return False

        lat, lon = coord[0], coord[1]

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self._api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.BASE_URL, params=params) as response:
                return response.status == 200

    async def exist_location_by_name(self, location_name: str) -> bool:
        if not location_name:
            return False

        params = {
            "q": location_name,
            "appid": self._api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.BASE_URL, params=params) as response:
                return response.status == 200

    async def get_location_name_by_coord(
        self, coord: Tuple[float, float]
    ) -> Optional[str]:
        if (
            len(coord) != 2
            or not isinstance(coord[0], (int, float))
            or not isinstance(coord[1], (int, float))
        ):
            return None

        lat, lon = coord[0], coord[1]

        params = {
            "lat": lat,
            "lon": lon,
            "lang": "ru",
            "units": "metric",
            "appid": self._api_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.BASE_URL, params=params) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("name")
                return None
