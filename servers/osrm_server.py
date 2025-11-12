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
        """
        Compute a route between two points.

        Accepts:
        - {'from': 'origin address', 'to': 'destination address'}  → will geocode via Nominatim
        - {'coordinates': [(lon, lat), (lon, lat)]}               → direct coordinates

        Returns:
        - JSON response from OSRM /route endpoint
        """

        coords = params.get("coordinates")

        print("[DEBUG] OSRM route called with params:", params)

        # If no direct coordinates are given, try to geocode 'from' and 'to'
        if not coords and "from" in params and "to" in params:
            try:
                from servers.osm_server import OSMServer
                osm = OSMServer()
                g1 = osm.geocode({"q": params["from"]})
                g2 = osm.geocode({"q": params["to"]})
                p1 = g1["results"][0]
                p2 = g2["results"][0]
                coords = [
                    (float(p1["lon"]), float(p1["lat"])),
                    (float(p2["lon"]), float(p2["lat"]))
                ]
            except Exception as e:
                return {"error": f"failed to geocode from/to: {e}"}

        # Validate we have at least two points
        if not coords or len(coords) < 2:
            return {"error": "need at least two coordinates for route"}

        # Build coordinate string in OSRM format: lon,lat;lon,lat
        coord_str = ";".join([f"{c[0]},{c[1]}" for c in coords])

        print("[DEBUG] OSRM route coord_str:", coord_str)
        
        url = f"{self.params.base_url}/route/v1/driving/{coord_str}"

        try:
            response = self.session.get(url, params={
                "overview": "simplified",
                "alternatives": "false",
                "steps": "false"
            })
            response.raise_for_status()
            return {"result": response.json()}
        except Exception as e:
            return {"error": f"OSRM request failed: {e}"}


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
