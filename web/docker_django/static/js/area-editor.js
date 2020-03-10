'use strict';

$(document).ready(function () {
    
    var ae_model = {};
    
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function intiMap(idMap) { // init map control

        var model = {
            map: null,
            borderGJ: {},
            map_id: '#' + idMap,
            data: {
                app_id: -1,
                polygons: [],
            }
        };

        var startPoint = [50.4546600, 30.5238000];

        var map = L.map(
            idMap, {editable: true}).setView(startPoint, 5);

        L.tileLayer(
            'http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
            {
                maxZoom: 20,
                attribution: 'Data \u00a9 <a href="http://www.openstreetmap.org/copyright"> OpenStreetMap Contributors </a> Tiles \u00a9 HOT'
            }).addTo(map);

        model.borderLayer = L.geoJSON().addTo(map);

    var group = new L.featureGroup();
    model.borderLayer.addTo(group);

        $.getJSON('/static/sources/ukraine.geojson').success(function (data) {
            model.borderGJ = data;
            model.borderLayer.addData(model.borderGJ);

            map.fitBounds(group.getBounds());
        });

        model.map = map;

        return model;
    }

    function clearAreas() {
        if (ae_model.data.polygons.length > 0) {
            for (var i = 0; i < ae_model.data.polygons.length; i++) {
                ae_model.map.removeLayer(ae_model.data.polygons[i].polygon);
            }
        }

        ae_model.map.polygons = [];
        ae_model.map.app_id = -1;
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", window.CSRF_TOKEN);
            }
        }
    });

    $('.js-add-area').click(function (e) { // add new editable polygon to the map
        var polygon = ae_model.map.editTools.startPolygon();
        ae_model.data.polygons.push({'polygon': polygon});

        return false;
    });

    $('.js-clear-area').click(function (e) {// clear all polygon data on the map
        clearAreas();

        return false;
    });

    //$('.js-save-area').click(function (e) { // prepare existing polygons data for saving

    $('#resolution_rada_project-create-form').submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');

        var polygons = [];

        for (var i = 0; i < ae_model.data.polygons.length; i++) {
            var poly = ae_model.data.polygons[i].polygon;

            var polyPaths = [];
            for (var j = 0; j < poly._latlngs.length; j++) {
                var path = poly._latlngs[j];

                var pathPoints = [];

                for (var k = 0; k < path.length; k++) {
                    var point = path[k];
                    if (point.lat && point.lng) {
                        pathPoints.push([point.lat, point.lng]);
                    }
                }

                if (pathPoints.length) {
                    polyPaths.push(pathPoints);
                }

            }

            if (polyPaths.length) {
                polygons.push({'id': ae_model.data.polygons[i].id, 'polygon': polyPaths});
            }
        }

        var data = {
            'app_id': ae_model.data.app_id,
            'polygons': polygons
        };

        // TODO send to back
        $.ajax({
            type: 'POST',
            url: url,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            data: JSON.stringify(data),
            success: function (data) {
                var messages = '';
                if (data.success == 0) {
                    messages = 'Помилка: ';
                    alert(messages + data.messages);
                }

                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            },
            error: function (jqXHR, textStatus, error) {
                console.log(jqXHR.responseText + ' | ' + textStatus + ' | ' + error);
            }
        });
    });

    ae_model = intiMap('map');

    var eservice_id = $(ae_model.map_id).data('eservice-id');
    if (eservice_id) {
        clearAreas();
        loadAreas(eservice_id);
    }

    function loadAreas(eservice_id) {
        var options = { // https://leafletjs.com/reference-1.4.0.html#polyline-option
            color: '#ff3232',
            fillColor: '#ff3232',
            fillOpacity: 0.5
        };

        var data = {
            'eservice_id': eservice_id
        };

        $.ajax({
            type: "POST",
            url: '/eservice/nadra/areas',
            data: JSON.stringify(data),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function (data) {

                ae_model.data.app_id = data.app_id || -1;

                var group = new L.featureGroup();
                for (var i = 0; i < data.polygons.length; i++) {
                    var poly = data.polygons[i];

                    var polygon = L.polygon(poly.poly, options).addTo(ae_model.map);
                    polygon.addTo(group);

                    // polygon.enableEdit();
                    //
                    // var polygonInfo = polygon.bindPopup('Завантаження...'); // initial text
                    // polygonInfo.__loaded = 0; // load only one times
                    // polygonInfo.__ploygon_id = polygonInfo._leaflet_id; // only for test
                    //
                    // polygonInfo.on('click', loadPolygonInfo); // bind load dynamic info to click

                    ae_model.data.polygons.push({
                        'id': poly.id,
                        'polygon' : polygon
                    });
                }

                ae_model.map.fitBounds(group.getBounds());
                // var zoom = ae_model.map.getZoom();
                // ae_model.map.setZoom(zoom > 1 ? zoom - 1 : zoom);
            },
            error: function (jqXHR, textStatus, error) {
                console.log(jqXHR.responseText + ' | ' + textStatus + ' | ' + error);
            }
        });
    }

});