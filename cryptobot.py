#!/usr/bin/python3
#-*- coding utf-8 -*-

import json
import config
import telebot
import requests
from bs4 import BeautifulSoup as BS
import re


bot = telebot.TeleBot(config.token)

cities = { 'moscow': 'москва',
           'kishinev': 'кишинев',
           'ryazan': 'рязань',
           'skopin': 'скопин',
           'shilovo': 'шилово',
           }
list_cities = [city for city in cities]

def get_ya():
    header = {'User-agent': 'Chrome/84.0.4147.86'}
    r = requests.get(f"https://ru.investing.com/equities/yandex?cid=102063",headers=header)
    r1 = requests.get(f"https://ru.investing.com/equities/yandex",headers=header)
    html = BS(r.content, 'html.parser')
    html1 = BS(r1.content, 'html.parser')
    acc = html.find_all(attrs={"data-test": "instrument-price-last"})
    acc_change = html.find_all(attrs={"data-test": "instrument-price-change-percent"})[0]
    acc_change = str(acc_change)
    acc = str(acc[0])
    acc = re.findall(r'(?<=instrument-price-last">).*(?=</span)', acc)
    acc_change = re.findall(r'(?<=instrument-price-change-percent">).*(?=<)', acc_change)[0]
    acc_change = re.findall(r'(?<=>).*(?=<)', acc_change)[0]
    acc = acc[0]
    acc1 = html1.find_all(attrs={"data-test": "instrument-price-last"})[0]
    acc1_change = html1.find_all(attrs={"data-test": "instrument-price-change-percent"})[0]
    acc1_change = str(acc1_change)
    acc1 = str(acc1)
    acc1 = re.findall(r'(?<=instrument-price-last">).*(?=<)', acc1)
    acc1_change = re.findall(r'(?<=instrument-price-change-percent">).*(?=<)', acc1_change)[0]
    acc1_change = re.findall(r'(?<=>).*(?=<)', acc1_change)[0]
    acc1 = acc1[0]
    return_value = f"{acc} руб. {acc_change} %, {acc1} $ {acc1_change} %"

    return return_value

def get_usd():
    header = {'User-agent': 'Chrome/84.0.4147.86'}
    r = requests.get(f"https://ru.investing.com/currencies/usd-rub",headers=header)
    bs = BS(r.content, 'html.parser')
    bs_test = bs.find_all('div', {'class': 'top bold inlineblock'})
    bs_change = bs_test[0].get_text().split()
    bs_change = bs_change[2]
    html = BS(r.content, 'html.parser')
    acc = html.find_all(attrs={"id": "last_last"})
    acc = str(acc[0])
    acc = re.findall(r'(?<=last_last">).*(?=</span)', acc)
    acc = acc[0]
    return_value = f"{acc} руб., {bs_change}"
    
    return return_value

def get_weather(city):
    r = requests.get(f"https://sinoptik.ua/погода-{city}")
    html = BS(r.content, 'html.parser')
    for el in html.select('#content'):
        a = str(el.select('.today-temp'))
        temp = re.findall(r'(?<=>).*(?=<)', a )[0]
        t_min = el.select('.temperature .min')[0].text
        t_max = el.select('.temperature .max')[0].text
        text = el.select('.wDescription .description')[0].text
    return temp, text

def get_crypto(money):
    virtual_money = {
    'eth': 'pid-1061443-last',
    'bts': 'pid-1057391-last'
    }
    url = 'https://ru.investing.com/crypto/'
    header = {'User-agent': 'Chrome/84.0.4147.86'}
    r = requests.get(f"{url}", headers=header)
    html = BS(r.content, 'html.parser')
    acc = html.find_all("a", class_= virtual_money[money])
    price = acc[0].get_text()
    return price + ' $'


def gen_message(city, username):
    return f"Привет {username}, погода на сегодня:\
 {get_weather(cities[city])[0]}\n{get_weather(cities[city])[1]}"


@bot.message_handler(commands=['start', 'help'])
def main(message):
	bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}, это погодный бот, допустимые города:\
\n{', '.join(list_cities)}")

@bot.message_handler(commands=['kishinev'])
def main(message):
        bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}, погода на сегодня:\
 {get_weather(cities['kishinev'])[0]}\n{get_weather(cities['kishinev'])[1]}")

@bot.message_handler(commands=['ya'])
def main(message):
    bot.send_message(message.chat.id, f"{message.from_user.first_name}, стоимость одной акции яндекса:\
 {get_ya()}")

@bot.message_handler(commands=['usd'])
def main(message):
    bot.send_message(message.chat.id, f"{message.from_user.first_name}, стоимость доллара в рублях:\
 {get_usd()}")

@bot.message_handler(commands=['btc'])
def main(message):
    bot.send_message(message.chat.id, f"{message.from_user.first_name}, стоимость одного биткоина:\
 {get_crypto('bts')}")

@bot.message_handler(commands=['eth'])
def main(message):
    bot.send_message(message.chat.id, f"{message.from_user.first_name}, стоимость одного эфира:\
 {get_crypto('eth')}")




@bot.message_handler(content_types=['text'])
def send_text(message):
    msg = message.text.lower()
    if msg[1::] in cities:
        msg = msg[1::]
        bot.send_message(message.chat.id, gen_message(msg, message.from_user.first_name))
        print(message.chat.id)


if __name__ == "__main__":
    bot.polling(none_stop=True)
