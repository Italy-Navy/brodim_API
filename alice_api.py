from pprint import pprint

from flask import Flask
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


# ______________________________________________________________--DATABASE--_______________________________________
def new_user(session_id):
    try:
        sqlite_connection = sqlite3.connect('session_data.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """INSERT INTO session_data
                              ('session_id', 'where', 'rest', 'what')
                              VALUES
                              (\"%s\", '', '', '');""" % session_id
        count = cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)


def check_entity(session_id):
    try:
        sqlite_connection = sqlite3.connect('session_data.db')
        cursor = sqlite_connection.cursor()
        sql_select_query = """SELECT * FROM session_data WHERE session_id=\"%s\"""" % session_id
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        cursor.close()
        return records[0]
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)
        return None


def add_where(session_id, where):
    try:
        sqlite_connection = sqlite3.connect('session_data.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """UPDATE session_data SET 'where' = \"%s\" WHERE session_id = \"%s\"""" % (where, session_id)
        count = cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)



def add_rest(session_id, rest):
    try:
        sqlite_connection = sqlite3.connect('session_data.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """UPDATE session_data SET 'rest' = \"%s\" WHERE session_id = \"%s\"""" % (rest, session_id)
        count = cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)


def add_what(session_id, what):
    try:
        sqlite_connection = sqlite3.connect('session_data.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """UPDATE session_data SET what = \"%s\" WHERE session_id = \"%s\"""" % (what, session_id)
        count = cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        logging.warning("Ошибка при работе с SQLite", error)


# ______________________________________________________________--DATABASE--_______________________________________

def clean_place_arr(A):
    for el in A:
        if len(el) < 2:
            A.remove(el)
    return " ".join(A)


def parser_validator(help_dict, tokens, word):
    try:
        return dict(
            value=help_dict[word]["value"],
            tokens=clean_place_arr(
                tokens[help_dict[word]["tokens"]["start"]:help_dict[word]["tokens"]["end"]])
        )
    except KeyError:
        return None


def parser(input_dict, session_id):
    OUT = dict()
    try:
        tokens = input_dict["request"]["nlu"]['tokens']  # вывели результат на экран
        intents = input_dict["request"]["nlu"]['intents']
        # pprint(tokens)
        try:
            all_entity = intents["all_entity"]["slots"]
            OUT["rest"] = parser_validator(all_entity, tokens=tokens, word="rest")
            OUT["what"] = parser_validator(all_entity, tokens=tokens, word="what")
            OUT["where"] = parser_validator(all_entity, tokens=tokens, word="where")
            #logging.warning(OUT, session_id)
            if OUT["rest"] is not None:
                add_rest(session_id, OUT["rest"]["tokens"])
            if OUT["what"] is not None:
                add_rest(session_id, OUT["what"]["tokens"])
            if OUT["where"] is not None:
                add_rest(session_id, OUT["where"]["tokens"])
            # pprint(OUT)
        except KeyError:
            pass
        try:
            pars_entity = intents["pars_entity"]["slots"]
            OUT["rest"] = parser_validator(pars_entity, tokens=tokens, word="rest")
            OUT["what"] = parser_validator(pars_entity, tokens=tokens, word="what")
            OUT["where"] = parser_validator(pars_entity, tokens=tokens, word="where")
            #logging.warning(OUT, session_id)
            if OUT["rest"] is not None:
                add_rest(session_id, OUT["rest"]["tokens"])
            if OUT["what"] is not None:
                add_rest(session_id, OUT["what"]["tokens"])
            if OUT["where"] is not None:
                add_rest(session_id, OUT["where"]["tokens"])
        except KeyError:
            pass
        try:
            pars_purpose = intents["pars_purpose"]["slots"]
            OUT["rest"] = parser_validator(pars_purpose, tokens=tokens, word="rest")
            OUT["what"] = parser_validator(pars_purpose, tokens=tokens, word="what")
            OUT["where"] = parser_validator(pars_purpose, tokens=tokens, word="where")
            #logging.warning(OUT, session_id)
            if OUT["rest"] is not None:
                add_rest(session_id, OUT["rest"]["tokens"])
            if OUT["what"] is not None:
                add_what(session_id, OUT["what"]["tokens"])
            if OUT["where"] is not None:
                add_where(session_id, OUT["where"]["tokens"])
        except KeyError:
            pass
        if OUT != dict():
            return "Done"
    except KeyError:
        return None


def first_meet():
    meeting_Arr = [
        """Привет, я бот помощник, сегодня я помогу тебе выбрать место для отдыха \nПросто скажи "хочу прогуляться" и я тебе помогу""",
        """Где ты хочешь отдохнуть? \nПопробуй спросить меня о лучших местах для отдыха""",
        """Планируешь свидание? \nЯ разбираюсь в этом лучше всех""",
        """Было бы неплохо прогуляться сегодня \n Я попытаюсь подобрать тебе лучшую дорогу"""
    ]
    return meeting_Arr[rndI(0, len(meeting_Arr) - 1)]


def error_message():
    meeting_Arr = [
        "Извини, я тебя не поняла",
        "Можешь повторить?",
        "Я бот, который составляет план прогулки. Я тебя не поняла",
        "Попробуй сказать по-другому, я тебя не поняла",
    ]
    return meeting_Arr[rndI(0, len(meeting_Arr) - 1)]


def handle_dialog(res, req):
    session_id = req["session"]["session_id"]
    if req['request']['original_utterance']:
        is_good = parser(req, session_id)
        if is_good is None:
            res['response']['text'] = error_message()
        else:
            chck_BD = check_entity(session_id)
            if chck_BD is None:
                res['response']['text'] = first_meet()
            else:
                id, where, rest, what = chck_BD
                if where == "":
                    res['response']['text'] = "Хорошо, назови свой город"
                elif rest == "":
                    res['response']['text'] = "Хорошо, куда ты бы хотел сходить"
                elif what == "":
                    res['response']['text'] = "Какая цель прогулки?"
                else:
                    res['response']['text'] = "У меня есть вся информация"
    else:
        # # Если это первое сообщение — представляемся
        new_user(session_id)
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
    #app.run(host='localhost', port=5200)
