from pprint import pprint

from flask import Flask
import requests
from flask import request
from random import randint as rndI
import logging
import json

import sqlite3

app = Flask(__name__)

logging.basicConfig(
    filename='bot_alice.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


def first_meet():
    meeting_Arr = [
        "В каком городе хотите построить маршрут?",
        "В каком городе планируете прогулку?",
        "В каком городе хотите погулять?",
        "В каком городе планируете провести время?",
        "В каком городе хотите провести встречу?",
        "В каком городе планируете погулять?",
    ]
    return meeting_Arr[rndI(0, len(meeting_Arr) - 1)]


def error_message():
    meeting_Arr = [
        "Извини, я тебя не поняла.",
        "Можешь повторить?",
        "Я тебя не поняла.",
        "Попробуй сказать по-другому.",
    ]
    return meeting_Arr[rndI(0, len(meeting_Arr) - 1)]


def search_city(arr):
    CITY = []
    for el in arr:
        if el["type"] == "YANDEX.GEO":
            CITY.append(el['value']['city'])
    return CITY


def handle_dialog(res, req):
    if req['request']['original_utterance']:
        try:
            map_request = 'http://www.brodim.ru/ai-quotes/city_in=' + search_city(req['request']["nlu"]["entities"])[0]
            link = str(requests.get(map_request).json()['link'])
            res['response']['text'] = "Я подготвила прогулку для тебя в случайном месте твоего города"
            res["response"]["buttons"] = [
                {
                    "url": "%s" % link,
                    'title': "Перейти на карту",
                    "payload": {},
                },
                {
                    'title': "Построить новый маршут",
                }
            ]
        except Exception as e:
            res['response']['text'] = error_message() + "\n Просто назови свой город"
    else:
        # # Если это первое сообщение — представляемся
        res['response']['text'] = first_meet()


@app.route('/', methods=['POST'])
def main():
    # # Создаем ответ
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    # # Заполняем необходимую информацию
    handle_dialog(response, request.json)
    return json.dumps(response)


if __name__ == '__main__':
    try:
        app.run(host='192.168.1.116', port=5200)
    except OSError:
        app.run(host='192.168.1.82', port=5200)
    # app.run(host='localhost', port=5200)
