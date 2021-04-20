function init () {
    var points_arr = {{points_arr}}
    var myMap = new ymaps.Map('map', {
            center: points_arr[0],
            zoom: 10
        }, {
            searchControlProvider: 'yandex#search'
        }),
        objectManager = new ymaps.ObjectManager({
            // Чтобы метки начали кластеризоваться, выставляем опцию.
            clusterize: true,
            // ObjectManager принимает те же опции, что и кластеризатор.
            gridSize: 32,
            clusterDisableClickZoom: true
        });

    // Чтобы задать опции одиночным объектам и кластерам,
    // обратимся к дочерним коллекциям ObjectManager.


    for(var i =0; i < points_arr.length; i++){
        myMap.geoObjects.add(new ymaps.Placemark(points_arr[i], {
        }));
    }


}

ymaps.ready(init);