from flask import Flask, request, render_template
from flask_restful import Api, Resource, reqparse
import requests
from random import choice

app = Flask(__name__)
api = Api(app)


class Quote(Resource):
    def find_object(self, city_in):
        city = city_in
        city_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" \
                       + city + "&format=json"
        city_response = requests.get(city_request).json()
        city_coord = city_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        coord = city_coord.split()
        string_coord = coord[0] + "," + coord[1]

        name_object1 = 'общественный транспорт'
        name_object2 = 'кафе'
        name_object3 = 'развлечение'
        bus_coord = self.find_concret_object(string_coord, name_object1)
        cafe_coord = self.find_concret_object(bus_coord, name_object2)
        fun_coord = self.find_concret_object(cafe_coord, name_object3)
        final_string = bus_coord + ';' + cafe_coord + ';' + fun_coord
        return final_string

    def get(self, city_in):
        data = self.find_object(city_in)
        return data, 201

    def post(self, city_in):
        data = self.find_object(city_in)
        return data, 201

    def find_concret_object(self, center, name_object):
        data_coord = []
        object_request = "https://search-maps.yandex.ru/v1/?text=" + name_object + "&type=biz&lang=ru_RU&ll=" + \
                         center + "&spn=0.552069,0.400552&results=10&apikey=6633a817-a99a-4d17-b557-a77557303ccc"
        object_response = requests.get(object_request)
        json_response = object_response.json()
        for i in json_response['features']:
            coord_object = i['geometry']['coordinates']
            data_coord.append(coord_object)
        bus_coord = choice(data_coord)
        bus_coord_string = str(bus_coord[0]) + ',' + str(bus_coord[1])
        return bus_coord_string


api.add_resource(Quote, "/ai-quotes", "/ai-quotes/", "/ai-quotes/<string:city_in>")
if __name__ == '__main__':
    app.run(debug=True)