import json
from servers.osm_server import OSMServer
from servers.osrm_server import OSRMServer


def test_osm_geocode():
    osm = OSMServer()
    out = osm.geocode({'q': 'Beirut, Lebanon'})
    print('OSM geocode results count:', len(out.get('results', [])))


def test_osm_reverse():
    osm = OSMServer()
    out = osm.reverse_geocode({'lat': 33.8938, 'lon': 35.5018})
    print('OSM reverse:', out.get('result', {}).get('display_name'))


def test_osm_poi():
    osm = OSMServer()
    out = osm.search_poi({'query': 'restaurant', 'near': 'Beirut, Lebanon'})
    print('OSM POI elements:', len(out.get('results', {}).get('elements', [])))


def test_osrm_route():
    osrm = OSRMServer()
    # Example coords: Beirut Corniche -> Hamra (approx)
    coords = [(35.5018,33.8938),(35.4820,33.8955)]
    out = osrm.route({'coordinates': coords})
    print('OSRM route code:', out.get('result', {}).get('code'))


def test_osrm_table():
    osrm = OSRMServer()
    coords = [(35.5018,33.8938),(35.4820,33.8955)]
    out = osrm.table({'coordinates': coords})
    print('OSRM table:', out.get('result', {}).get('durations'))


if __name__ == '__main__':
    print('Running tests...')
    test_osm_geocode()
    test_osm_reverse()
    test_osm_poi()
    test_osrm_route()
    test_osrm_table()
    print('Done.')