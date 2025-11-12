# app/mcp_server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uvicorn
import json

from servers.osm_server import OSMServer
from servers.osrm_server import OSRMServer


# Initialize FastAPI
app = FastAPI(title="Map Agent MCP Server", description="A minimal MCP server exposing OSM and OSRM map tools.")


# Enable CORS (useful for web-based testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Instantiate map servers
osm = OSMServer()
osrm = OSRMServer()


# ---------- Data Models ----------

class GeocodeRequest(BaseModel):
    q: str  # location name or address


class RouteRequest(BaseModel):
    from_addr: str
    to_addr: str


# ---------- MCP-Like Metadata Endpoint ----------

@app.get("/server/params")
def server_params() -> Dict[str, Any]:
    """Return available map servers and their exposed commands (MCP-like description)."""
    return {
        "servers": {
            "osm": {
                "description": "OpenStreetMap-based geocoding service.",
                "commands": ["geocode"],
                "endpoint": "/osm/geocode",
                "schema": GeocodeRequest.schema()
            },
            "osrm": {
                "description": "Open Source Routing Machine for driving routes.",
                "commands": ["route"],
                "endpoint": "/osrm/route",
                "schema": RouteRequest.schema()
            }
        }
    }


# ---------- OSM Geocoding Endpoint ----------

@app.post("/osm/geocode")
def osm_geocode(req: GeocodeRequest):
    """Convert a location name into coordinates using OpenStreetMap (Nominatim)."""
    if not req.q:
        raise HTTPException(status_code=400, detail="Missing 'q' (query/address)")
    try:
        print(f"[INFO] Geocode request for: {req.q}")
        result = osm.geocode({"q": req.q})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")


# ---------- OSRM Routing Endpoint ----------

@app.post("/osrm/route")
def osrm_route(req: RouteRequest):
    """Find a driving route between two locations."""
    if not (req.from_addr and req.to_addr):
        raise HTTPException(status_code=400, detail="Both 'from_addr' and 'to_addr' are required.")

    print(f"[INFO] Routing request: from {req.from_addr} to {req.to_addr}")

    try:
        # Step 1: Geocode both addresses
        from_coords = osm.geocode({"q": req.from_addr})
        to_coords = osm.geocode({"q": req.to_addr})

        # print(f"[INFO] Routing request: from {from_coords} to {to_coords}")

        if not from_coords or not to_coords:
            raise HTTPException(status_code=400, detail="Could not geocode one or both addresses.")

        beirut_result = next(
            (r for r in from_coords["results"] if "لبنان" in r["display_name"] or "Lebanon" in r["display_name"]),
            from_coords["results"][0]
        )
        from_coord = (
            float(beirut_result["lon"]),
            float(beirut_result["lat"])
        )

        tripoli_result = next(
            (r for r in to_coords["results"] if "لبنان" in r["display_name"] or "Lebanon" in r["display_name"]),
            to_coords["results"][0]  # fallback
        )

        to_coord = (
            float(tripoli_result["lon"]),
            float(tripoli_result["lat"])
        )
        print(f"[INFO] Routing from {from_coord} to {to_coord}")

        # Step 3: Request route from OSRM
        route_data = osrm.route({"coordinates": [from_coord, to_coord]})
        return route_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing failed: {str(e)}")


# ---------- Server Runner ----------

if __name__ == "__main__":
    print("🚀 Starting MCP Map Server on http://localhost:8000 ...")
    uvicorn.run("app.mcp_server:app", host="0.0.0.0", port=8000, reload=True)
