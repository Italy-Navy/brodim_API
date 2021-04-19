import logging
from flask import request

from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse
import requests
from random import choice

app = Flask(__name__)
api = Api(app)

logging.basicConfig(
    filename='map.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


class Quote(Resource):
    def find_object(self, city_in):
        city = city_in
        city_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" \
                       + city + "&format=json"
        city_response = requests.get(city_request).json()
        city_coord = city_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        coord = city_coord.split()
        string_coord = coord[0] + "," + coord[1]

        name_object1 = 'кафе'
        name_object2 = 'развлечение'
        cafe_coord = self.find_concret_object(string_coord, name_object1)
        fun_coord = self.find_concret_object(string_coord, name_object2)
        final_string = cafe_coord + ';' + fun_coord
        return {"link": str('http://www.brodim.ru/karta?points=%s' % final_string)}

    def get(self, city_in):
        data = self.find_object(city_in)
        return data, 201

    def post(self, city_in):
        data = self.find_object(city_in)
        return data, 201

    def find_concret_object(self, center, name_object):
        data_coord = []
        object_request = "https://search-maps.yandex.ru/v1/?text=" + name_object + "&type=biz&lang=ru_RU&ll=" + \
                         center + "&spn=0.552069,0.400552&results=4&apikey=6633a817-a99a-4d17-b557-a77557303ccc"
        object_response = requests.get(object_request)
        json_response = object_response.json()
        for i in json_response['features']:
            coord_object = i['geometry']['coordinates']
            data_coord.append(coord_object)
        bus_coord = choice(data_coord)
        bus_coord_string = str(bus_coord[1]) + ',' + str(bus_coord[0])
        return bus_coord_string


@app.route('/map_js')
def map_js():
    points = request.args.get("points")
    poin = list(points.split(';'))
    points = []
    for el in poin:
        points.append(list(map(float, el.split(','))))
    return render_template('map.js', points_arr=points)


@app.route('/karta')
def karta():
    points = request.args.get("points")
    print(points)
    return render_template('map.html', dots=points)


api.add_resource(Quote, "/ai-quotes", "/ai-quotes/", "/ai-quotes/<string:city_in>")

if __name__ == '__main__':
    try:
        app.run(host='192.168.1.116', port=5300)
    except OSError:
        app.run(host='192.168.1.82', port=5300, debug=True)
    #  app.run(host='localhost', port=5300)