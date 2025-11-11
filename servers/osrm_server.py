from dataclasses import dataclass
from typing import Dict, Any
import os
import requests


@dataclass
class ServerParams:
    name: str
    base_url: str
    commands: list


class OSRMServer:
    def __init__(self, base_url: str = None):
        base_url = base_url or os.getenv('OSRM_BASE_URL') or 'https://router.project-osrm.org'
        self.params = ServerParams(name='osrm', base_url=base_url, commands=['route', 'nearest', 'table'])
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'map-agent-project/1.0'})

    def route(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compute a route between two points. Accepts either:
        - {'from': 'origin address', 'to': 'destination address'} (will attempt geocode via Nominatim if present)
        - {'coordinates': [(lon,lat),(lon,lat)]}
        """
        coords = params.get('coordinates')
        if not coords and 'from' in params and 'to' in params:
            # try to geocode using Nominatim through simple HTTP call
            from servers.osm_server import OSMServer
            osm = OSMServer()
            g1 = osm.geocode({'q': params['from']})
            g2 = osm.geocode({'q': params['to']})
            try:
                p1 = g1['results'][0]
                p2 = g2['results'][0]
                coords = [(float(p1['lon']), float(p1['lat'])), (float(p2['lon']), float(p2['lat']))]
            except Exception:
                return {'error': 'failed to geocode from/to'}

        if not coords or len(coords) < 2:
            return {'error': 'need at least two coordinates for route'}

        # build coordinates string lon,lat;lon,lat
        coord_str = ';'.join([f"{c[0]},{c[1]}" for c in coords])
        url = f"{self.params.base_url}/route/v1/driving/{coord_str}"
        r = self.session.get(url, params={'overview': 'simplified', 'alternatives': 'false', 'steps': 'false'})
        r.raise_for_status()
        return {'result': r.json()}

    def nearest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        lat = params.get('lat') or (params.get('coordinates') and params['coordinates'][0][1])
        lon = params.get('lon') or (params.get('coordinates') and params['coordinates'][0][0])
        if lat is None or lon is None:
            return {'error': 'missing lat/lon for nearest'}
        url = f"{self.params.base_url}/nearest/v1/driving/{lon},{lat}"
        r = self.session.get(url)
        r.raise_for_status()
        return {'result': r.json()}

    def table(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Build a duration/distance matrix for given coordinates
        coords = params.get('coordinates')
        if not coords or len(coords) < 2:
            return {'error': 'need at least two coordinates for table'}
        coord_str = ';'.join([f"{c[0]},{c[1]}" for c in coords])
        url = f"{self.params.base_url}/table/v1/driving/{coord_str}"
        r = self.session.get(url)
        r.raise_for_status()
        return {'result': r.json()}
