from dataclasses import dataclass
from typing import Dict, Any, List
import requests


@dataclass
class ServerParams:
    name: str
    base_nominatim: str
    base_overpass: str
    commands: List[str]


class OSMServer:
    def __init__(self, base_nominatim: str = "https://nominatim.openstreetmap.org", base_overpass: str = "https://overpass-api.de/api"):
        self.params = ServerParams(
            name='osm_nominatim_overpass',
            base_nominatim=base_nominatim,
            base_overpass=base_overpass,
            commands=['geocode', 'reverse_geocode', 'search_poi']
        )
        self.session = requests.Session()
        # Nominatim requires a valid user-agent
        self.session.headers.update({'User-Agent': 'map-agent-project/1.0 (example@example.com)'})

    def geocode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Geocode a free text address using Nominatim."""
        q = params.get('q') or params.get('address') or params.get('query')
        if not q:
            return {'error': 'missing query for geocode'}
        url = f"{self.params.base_nominatim}/search"
        r = self.session.get(url, params={'q': q, 'format': 'json', 'limit': 5})
        r.raise_for_status()
        return {'results': r.json()}

    def reverse_geocode(self, params: Dict[str, Any]) -> Dict[str, Any]:
        lat = params.get('lat')
        lon = params.get('lon')
        if lat is None or lon is None:
            return {'error': 'missing lat/lon for reverse_geocode'}
        url = f"{self.params.base_nominatim}/reverse"
        r = self.session.get(url, params={'lat': lat, 'lon': lon, 'format': 'json'})
        r.raise_for_status()
        return {'result': r.json()}

    def search_poi(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search POIs using Overpass. Accepts either 'query' + 'near' or 'q' text.

        Example: search_poi({'query':'restaurant','near':'Beirut'})
        """
        query = params.get('query') or params.get('q')
        near = params.get('near')
        if not query:
            return {'error': 'missing query for search_poi'}

        # Build a minimal Overpass query. This is a simple example; in real systems,
        # you'll want to construct safer and more robust queries.
        if near:
            # geocode 'near' to get a bounding box
            geocode_resp = self.geocode({'q': near})
            if 'results' in geocode_resp and geocode_resp['results']:
                r0 = geocode_resp['results'][0]
                bbox = r0.get('boundingbox')  # [south, north, west, east]
                if bbox:
                    s, n, w, e = bbox[0], bbox[1], bbox[2], bbox[3]
                    bbox_str = f"{s},{w},{n},{e}"
                else:
                    bbox_str = None
            else:
                bbox_str = None
        else:
            bbox_str = None

        overpass_query = '[out:json][timeout:25];'
        if bbox_str:
            overpass_query += f'(' \
                               f'node["amenity"~"{query}"]({bbox_str});' \
                               f'way["amenity"~"{query}"]({bbox_str});' \
                               f'relation["amenity"~"{query}"]({bbox_str});' \
                               f');'
        else:
            # fallback: global search; beware of heavy queries
            overpass_query += f'(' \
                               f'node["amenity"~"{query}"];' \
                               f'way["amenity"~"{query}"];' \
                               f'relation["amenity"~"{query}"];' \
                               f');'
        overpass_query += 'out center 20;'

        url = f"{self.params.base_overpass}/interpreter"
        r = self.session.post(url, data={'data': overpass_query})
        r.raise_for_status()
        return {'results': r.json()}
