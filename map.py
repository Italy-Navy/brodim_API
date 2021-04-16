import logging

from flask import Flask, render_template
from flask import request

app = Flask(__name__)

logging.basicConfig(
    filename='map.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)


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
    return render_template('map.html', dots=points)


if __name__ == '__main__':
    try:
        app.run(host='192.168.1.116', port=4620)
    except OSError:
        app.run(host='192.168.1.82', port=4620)
    # app.run(host='localhost', port=5200)
