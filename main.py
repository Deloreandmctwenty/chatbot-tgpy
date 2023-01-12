import requests
from bs4 import BeautifulSoup as x
import telebot

URL = "TOPSECRET"
APIK = # smth

def pars(url):

    get = requests.get(URL)
    # ниже проверка на положительный ответ от сервера (вывод: 200)
    # print(get.status_code)

    conversion = x(get.text, "html.parser") # пропускаем код в htmlпарсер из библиотеки BeautifulSoup

    game_news = conversion.find_all("div", class_="post")
    return [i.text for i in game_news]

newslist = pars(URL)

bot = telebot.TeleBot(APIK)

@bot.message_handler(commands=["НАЧАТЬ"])

def wellcome(mes):
    bot.send_message(mes.chat.id, "Привет, введи лбую цифру, чтобы просмотреть инровую новость.")

@bot.message_handler(content_types=["text"])
def new(mes):
    if mes.text.lower() in "1234567890":
        bot.send_message(mes.chat.id, newslist[0])
        del newslist[0]
    else:
        bot.send_message(mes.chat.id, "Введи цифру")
bot.polling()
