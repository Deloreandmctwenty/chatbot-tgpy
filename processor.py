import asyncio
import aiohttp
import time
from aiogram import Bot
from modules import database


API_STR = "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&" \
          "hourly=temperature_2m,relativehumidity_2m,precipitation,weathercode,windspeed_10m&" \
          "timeformat=unixtime"

WEATHER_CODES = {
    0: "Ясно",
    1: "В основном ясно",
    2: "Частично облачно",
    3: "Пасмурно",
    45: "Туман",
    48: "Туман",
    51: "Лёгкая морось",
    53: "Умеренная морось",
    55: "Плотная морось",
    56: "Моросящий дождь",
    57: "Моросящий дождь",
    61: "Слабый дождь",
    63: "Умеренный дождь",
    65: "Сильный дождь",
    66: "Лёгкий замораживающий дождь",
    67: "Сильный замораживающий дождь",
    71: "Лёгкий снегопад",
    73: "Снегопад",
    75: "Сильный снегопад",
    77: "Град",
    80: "Незначительный ливень",
    81: "Умеренный ливень",
    82: "Сильный ливень",
    85: "Незначительный снежный ливень",
    86: "Сильный снежный ливень",
    95: "Гроза",
    96: "Гроза с небольшим градом",
    99: "Гроза с крупным градом"
}


async def process_weather(bot: Bot, update_time=300):
    last_checked = {}

    async with aiohttp.ClientSession() as session:
        while True:
            db = database.read_database()
            for user_id, info in db.items():
                user_id = int(user_id)
                url = API_STR.format(lat=info["latitude"], long=info["longitude"])
                res = await (await session.get(url)).json()
                if res.get("error"):
                    continue
                res = res["hourly"]

                current_idx = 0
                for tm in res["time"]:
                    if tm < time.time():
                        current_idx += 1
                if current_idx == len(res["time"]) or last_checked.get(user_id, 0) >= res["time"][current_idx]:
                    continue

                temperature = int(res["temperature_2m"][current_idx])
                humidity = res["relativehumidity_2m"][current_idx]
                precipitation = int(res["precipitation"][current_idx])
                windspeed = int(res["windspeed_10m"][current_idx])
                weathercode = res["weathercode"][current_idx]

                response = f"<b>Прогноз погоды на следующий час:</b>\n\n" \
                           f"* Погода: <b>{WEATHER_CODES.get(weathercode, 'Ядерная зима')}</b>\n" \
                           f"* Температура: <b>{temperature}°C</b>\n" \
                           f"* Влажность: <b>{humidity}%</b>\n" \
                           f"* Осадки: <b>{precipitation}mm</b>\n" \
                           f"* Скорость ветра: <b>{windspeed / 3.6:.1f} м/с</b>"
                try:
                    await bot.send_message(user_id, response, parse_mode="HTML")
                except Exception:
                    pass

                last_checked[user_id] = res["time"][current_idx]
            await asyncio.sleep(update_time)
