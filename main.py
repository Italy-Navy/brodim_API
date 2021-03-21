from flask import Flask
from flask_restful import Api, Resource, reqparse
import requests

app = Flask(__name__)
api = Api(app)


class Quote(Resource):
    def find_object(self, city_in, object_in):
        city = city_in
        city_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + city + "&format=json"
        city_response = requests.get(city_request).json()
        city_coord = city_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        coord = city_coord.split()
        string_coord = coord[0] + "," + coord[1]

        name_object = object_in
        coord_data = []
        object_request = "https://search-maps.yandex.ru/v1/?text=" + name_object + "&type=biz&lang=ru_RU&ll=" + string_coord + "&spn=0.552069,0.400552&results=5&apikey=6633a817-a99a-4d17-b557-a77557303ccc"
        object_response = requests.get(object_request)
        json_response = object_response.json()
        map_request = "https://static-maps.yandex.ru/1.x/?ll=" + string_coord + "&spn=0.01,0.01&l=map,skl&pt="
        for i in json_response['features']:
            coord_object = i['geometry']['coordinates']
            coord_data.append(coord_object)
        return coord_data

    def get(self, city_in, object_in):
        data = self.find_object(city_in, object_in)
        return data, 201

    def post(self, city_in, object_in):
        data = self.find_object(city_in, object_in)
        return data, 201


api.add_resource(Quote, "/ai-quotes", "/ai-quotes/", "/ai-quotes/<string:city_in>/<string:object_in>")
if __name__ == '__main__':
    app.run(debug=True)