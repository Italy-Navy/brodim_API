from pprint import pprint

from flask import Flask
from flask import request
from random import randint as rndI
import logging
import json

app = Flask(__name__)

logging.basicConfig(
    filename='alice.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


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


def parser(input_dict):
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
            # pprint(OUT)
        except KeyError:
            pass
        try:
            pars_entity = intents["pars_entity"]["slots"]
            OUT["rest"] = parser_validator(pars_entity, tokens=tokens, word="rest")
            OUT["what"] = parser_validator(pars_entity, tokens=tokens, word="what")
            OUT["where"] = parser_validator(pars_entity, tokens=tokens, word="where")
        except KeyError:
            pass
        try:
            pars_purpose = intents["pars_purpose"]["slots"]
            OUT["rest"] = parser_validator(pars_purpose, tokens=tokens, word="rest")
            OUT["what"] = parser_validator(pars_purpose, tokens=tokens, word="what")
            OUT["where"] = parser_validator(pars_purpose, tokens=tokens, word="where")
        except KeyError:
            pass
        if OUT != dict():
            return OUT
    except KeyError:
        return None


def first_meet():
    meeting_Arr = [
        "Привет, я бот помощник, сегодня я помогу тебе выбрать место для отдыха",
        "Где ты хочешь отдохнуть?",
        "Планируешь свидание?",
        "Было бы неплохо прогуляться сегодня"
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
    if req['request']['original_utterance']:
        MAIN_DICT = parser(req)
        if MAIN_DICT is None:
            res['response']['text'] = error_message()
        else:
            if MAIN_DICT["where"] is None:
                res['response']['text'] = "Хорошо, где ты живёшь?"
            else:
                res['response']['text'] = str(MAIN_DICT)
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
    # app.run(host='192.168.1.116', port=5200)
    app.run(host='192.168.1.82', port=5200)
    app.run(host='localhost', port=5200)
