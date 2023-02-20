import logging
import asyncio
import aiohttp
import os

from modules import database
from modules import processor
from aiogram import Bot, Dispatcher, types
from geopy import geocoders


bot = Bot(token=os.environ["BOT_TOKEN"])
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.row(types.KeyboardButton("\U0001F9ED Отправить местоположение", request_location=True))
    await message.reply("Здравствуйте, разрешите боту получать Вашу геолокацию или напишите название города, чтобы получить сведения о погоде.", reply_markup=keyboard)


@dp.message_handler(commands="stop")
async def cmd_stop(message: types.Message):
    database.delete_user(message.from_user.id)
    await message.reply("Сессия остановлена")


@dp.message_handler(commands="weather")
async def cmd_weather(message: types.Message):
    db = database.read_database()
    user_id = str(message.from_user.id)
    if user_id not in db:
        await message.reply("Для начала, укажите ваше местоположение")
        return

    async with aiohttp.ClientSession() as session:
        url = processor.API_STR.format(lat=db[user_id]["latitude"], long=db[user_id]["longitude"])
        url += "&current_weather=true"
        res = await (await session.get(url)).json()
        if res.get("error"):
            await message.reply("Что-то пошло не так...")
            return

        res = res["current_weather"]
        temperature = int(res["temperature"])
        windspeed = int(res["windspeed"])
        weathercode = res["weathercode"]

        response = f"<b>Текущая погода:</b>\n\n" \
                   f"* Погода: <b>{processor.WEATHER_CODES.get(weathercode, 'Ядерная зима')}</b>\n" \
                   f"* Температура: <b>{temperature}°C</b>\n" \
                   f"* Скорость ветра: <b>{windspeed / 3.6:.1f} м/с</b>"
        try:
            await message.reply(response, parse_mode="HTML")
        except Exception:
            pass


@dp.message_handler(content_types=[types.ContentType.LOCATION])
async def location_received(message: types.Message):
    lat, long = message.location.latitude, message.location.longitude
    database.update_user(message.from_user.id, lat, long)
    await message.reply("Сохранено")


def geo_pos(city: str):
    geolocator = geocoders.Nominatim(user_agent="telebot")
    return geolocator.geocode(city).latitude, geolocator.geocode(city).longitude


@dp.message_handler(content_types=[types.ContentType.TEXT])
async def text_location_received(message: types.Message):
    lat, long = geo_pos(message.text)
    database.update_user(message.from_user.id, lat, long)
    await message.reply("Сохранено")


async def main():
    asyncio.create_task(processor.process_weather(bot))
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
