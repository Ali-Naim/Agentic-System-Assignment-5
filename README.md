# Map Agent Project

An **AI Agent** that connects to **MCP-compatible map servers** to perform real-world geographic actions using external APIs like **OpenStreetMap (OSM)** and **OSRM**.

---

## Features
- **OSM Server** (`servers/osm_server.py`)  
  - `geocode` – Get coordinates from an address  
  - `reverse_geocode` – Get address from coordinates  
  - `search_poi` – Find points of interest

- **OSRM Server** (`servers/osrm_server.py`)  
  - `route` – Get directions between locations  
  - `nearest` – Find the nearest road  
  - `table` – Compute travel times/distances

- **Assistant Agent** (`agents/assistant_agent.py`)  
  Routes user prompts to the right MCP tool and interprets responses.

---

## Setup

1. Prepare the virtual environment


```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```


2. Run the MCP server


```bash
python app/mcp_server.py #or uvicorn app.mcp_server:app --reload --host 0.0.0.0 --port 8000
```


3. Run the main LLM Agent


```bash
python main.py
```