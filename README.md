# Map Agent Project


This project implements two map-server "tools" as Python modules and integrates them with a simple AssistantAgent that routes queries to the servers. It follows MCP-like conventions: each server exposes a `ServerParams` dataclass and at least three operations. The project includes example scripts and simple tests.


Supported servers
- `servers/osm_server.py` — OpenStreetMap-backed tool (Nominatim + Overpass)
- operations: `geocode`, `reverse_geocode`, `search_poi`
- `servers/osrm_server.py` — OSRM-backed tool (public demo OSRM server)
- operations: `route`, `nearest`, `table`


Other files
- `agents/assistant_agent.py` — AssistantAgent that routes user queries to servers
- `main.py` — small interactive CLI for demoing the assistant
- `tests/test_servers.py` — simple smoke tests / example usages
- `requirements.txt` — Python dependencies


## How to run
1. Create a virtualenv and activate it (Python 3.9+ recommended)


```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```


2. Run demo interactive assistant


```bash
python main.py
```


3. Run tests / example script


```bash
python tests/test_servers.py
```


## Configuration
No API keys required for public Nominatim/Overpass/OSRM demo endpoints in the examples. If you need to use a hosted or private OSRM instance, set OSRM_BASE_URL in `servers/osrm_server.py` or via environment variable.


Please respect the usage policies of the public services used (Nominatim, Overpass, OSRM demo) — use reasonable request rates.
