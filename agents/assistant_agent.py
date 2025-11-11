from typing import Any, Dict

class AssistantAgent:
    """Very small AssistantAgent that routes user queries to tool instances.

    Behavior is keyword-based (simple intent detection):
    - 'geocode', 'address' -> osm.geocode
    - 'reverse', 'lat' -> osm.reverse_geocode
    - 'poi', 'search', 'near' -> osm.search_poi
    - 'route', 'directions' -> osrm.route
    - 'nearest' -> osrm.nearest
    - 'table', 'matrix' -> osrm.table

    This is intentionally simple so it can be used as an example of integrating tools.
    """

    def __init__(self, tools: Dict[str, Any]):
        # tools: e.g. {'osm': osm_server_instance, 'osrm': osrm_server_instance}
        self.tools = tools

    def handle(self, user_text: str) -> Any:
        txt = user_text.lower()
        # intent routing
        if 'geocode' in txt or 'address' in txt and 'reverse' not in txt:
            return self.tools['osm'].geocode(self._param_from_text(txt))
        if 'reverse' in txt or ('lat' in txt and 'lon' in txt) or ('latitude' in txt):
            return self.tools['osm'].reverse_geocode(self._param_from_text(txt))
        if 'poi' in txt or 'near' in txt or 'search' in txt:
            return self.tools['osm'].search_poi(self._param_from_text(txt))
        if 'route' in txt or 'directions' in txt:
            return self.tools['osrm'].route(self._param_from_text(txt))
        if 'nearest' in txt and 'route' not in txt:
            return self.tools['osrm'].nearest(self._param_from_text(txt))
        if 'table' in txt or 'matrix' in txt:
            return self.tools['osrm'].table(self._param_from_text(txt))

        # fallback: try to geocode first then route if contains 'to'
        if ' to ' in txt and any(k in txt for k in ('route','directions','drive')):
            return self.tools['osrm'].route(self._param_from_text(txt))

        # default: try geocode
        return self.tools['osm'].geocode(self._param_from_text(txt))

    def _param_from_text(self, txt: str) -> Dict[str, Any]:
        # Extremely simple param extractor for demo purposes.
        # Attempt to detect coordinates formatted like 'lat,lon'
        import re
        m = re.search(r"(-?\d+\.\d+),\s*(-?\d+\.\d+)", txt)
        if m:
            return {'lat': float(m.group(1)), 'lon': float(m.group(2)), 'q': txt}
        # detect 'from X to Y'
        m2 = re.search(r"from (.+) to (.+)", txt)
        if m2:
            return {'from': m2.group(1).strip(), 'to': m2.group(2).strip(), 'q': txt}
        # detect 'search for restaurant near beirut'
        m3 = re.search(r"search for (.+) near (.+)", txt)
        if m3:
            return {'query': m3.group(1).strip(), 'near': m3.group(2).strip(), 'q': txt}
        return {'q': txt}
