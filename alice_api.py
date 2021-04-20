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

GOOD_PHRASES = []


# ______________________________________________________________--DATABASE--_______________________________________

def fill_good_phrases():
    global GOOD_PHRASES
    try:
        sqlite_connection = sqlite3.connect('DB_alice.db')
        cursor = sqlite_connection.cursor()
        sql_select_query = """SELECT * FROM advices"""
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        cursor.close()
        for el in records:
            GOOD_PHRASES.append(el[1])
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)


def new_user(session_id):
    try:
        sqlite_connection = sqlite3.connect('DB_alice.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """INSERT INTO sessions
                              ('session_id', 'geo')
                              VALUES
                              (\"%s\", '');""" % session_id
        cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)


def check_entity(session_id):
    try:
        sqlite_connection = sqlite3.connect('DB_alice.db')
        cursor = sqlite_connection.cursor()
        sql_select_query = """SELECT * FROM sessions WHERE session_id=\"%s\"""" % session_id
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        cursor.close()
        return records[0]
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)
        return None


def add_geo(session_id, geo):
    try:
        sqlite_connection = sqlite3.connect('DB_alice.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """UPDATE sessions SET 'geo' = \"%s\" WHERE session_id = \"%s\"""" % (geo, session_id)
        cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)


def add_coords(session_id, coords_str):
    try:
        sqlite_connection = sqlite3.connect('DB_alice.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """UPDATE sessions SET 'coord_A' = \"%s\" WHERE session_id = \"%s\"""" % (
            coords_str[0], session_id)
        cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()

        sqlite_connection = sqlite3.connect('DB_alice.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """UPDATE sessions SET 'coord_B' = \"%s\" WHERE session_id = \"%s\"""" % (
            coords_str[1], session_id)
        cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()

    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)
    except Exception as e:
        logging.warning("Ошибка при выделении координат", e, coords_str)


# ______________________________________________________________--DATABASE--_______________________________________


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
    ses_id = req['session']['session_id']
    if req['request']['original_utterance']:
        try:
            if req['request']['command'] == "найти ближайшие остановки":
                if check_entity(ses_id)[2] is not None:
                    bus_request = 'http://www.brodim.ru/bus-stop/' + str(check_entity(ses_id)[2]) + '/' + str(
                        check_entity(ses_id)[3])
                    link_bus = str(requests.get(bus_request).json()['link'])
                    res['response']['text'] = "Я нашла ближайшие остановки"
                    res["response"]["buttons"] = [
                        {
                            "url": "%s" % link_bus,
                            'title': "Посмотреть на карте",
                            "payload": {},
                        },
                        {
                            'title': "Выбрать другой город",
                        },
                    ]
                else:
                    res['response']['text'] = "Для начала ты должен сказать мне свой город"
            elif req['request']['command'] == 'выбрать другой город':
                res['response']['text'] = "Для нового маршута, просто сообщи свой город"
            elif 'алиса, что ты умеешь' in req['request']['command'] or 'что ты умеешь' in req['request']['command']:
                res['response']['text'] = 'Я могу спланировать тебе прогулку!' + '\n' + \
                                          'Просто скажи мне город, и я проложу тебе маршрут.' + '\n' + \
                                          'Если хочешь, то можешь ещё посмотреть на карте ближайшие остановки'
            elif 'помощь' in req['request']['command']:
                res['response']['text'] = \
                    'Я могу спланировать тебе прогулку!' + '\n' + \
                    'Просто скажи мне город, и я проложу тебе маршрут, а также дам совет для отличной прогулки.' + '\n' + \
                    'Чтобы увидеть ближайшие остановки, нажми на кнопку "Найти ближайшие остановки".' + '\n' + \
                    'Если тебе не понравился проложенный маршрут, то можешь нажать кнопку "Построить новый маршрут".' \
                    'Тогда навык покажет тебе карту с новым маршрутом!'
            else:
                if req['request']['command'] == "построить новый маршут" and check_entity(ses_id)[1] != '':
                    city_geo = check_entity(ses_id)[1]
                else:
                    city_geo = search_city(req['request']["nlu"]["entities"])[0]
                    add_geo(session_id=ses_id, geo=city_geo)
                map_request = 'http://www.brodim.ru/ai-quotes/city_in=' + city_geo
                link_map = str(requests.get(map_request).json()['link'])
                coords = link_map[link_map.find('=') + 1:].split(';')
                add_coords(session_id=ses_id, coords_str=coords)
                res['response']['text'] = GOOD_PHRASES[rndI(0, len(GOOD_PHRASES) - 1)]
                res["response"]["buttons"] = [
                    {
                        "url": "%s" % link_map,
                        'title': "Перейти на карту",
                        "payload": {},
                    },
                    {
                        'title': "Построить новый маршут",
                    },
                    {
                        'title': "Найти ближайшие остановки",
                    }
                ]
        except Exception as e:
            res['response']['text'] = error_message() + "\n Просто назови свой город"
            logging.warning("Ошибка при работе при обработке ответа", e)
    else:
        # # Если это первое сообщение — представляемся
        res['response']['text'] = first_meet()
        new_user(ses_id)


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
    fill_good_phrases()
    try:
        app.run(host='192.168.1.116', port=5200)
    except OSError:
        app.run(host='192.168.1.82', port=5200)
    # app.run(host='localhost', port=5200)
