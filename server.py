from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn
import threading
from fastmcp import FastMCP
import httpx
import os
from typing import Optional

mcp = FastMCP("Bright Sky")

BASE_URL = "https://api.brightsky.dev"


@mcp.tool()
async def get_weather(
    date: str,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    source: Optional[str] = None,
    units: str = "dwd",
) -> dict:
    """Retrieve weather observations or forecasts for a specific location and time range.
    Use this when the user asks about current weather, historical weather observations,
    or short-term forecasts for a location in Germany.
    Accepts either lat/lon coordinates or a DWD station ID.
    """
    params = {"date": date, "units": units}
    if last_date:
        params["last_date"] = last_date
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id
    if source:
        params["source"] = source

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/weather", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_current_weather(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    units: str = "dwd",
) -> dict:
    """Retrieve the most recent weather observation for a location.
    Use this when the user asks about the current weather conditions right now.
    Returns the latest available observation from the nearest DWD station.
    """
    params = {"units": units}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/current_weather", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_forecast(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    station_id: Optional[int] = None,
    date: Optional[str] = None,
    last_date: Optional[str] = None,
    units: str = "dwd",
) -> dict:
    """Retrieve MOSMIX weather forecast data for a location over a future time range.
    Use this when the user wants to know predicted weather conditions, upcoming temperatures,
    precipitation, or wind for the coming days in Germany.
    """
    params = {"units": units}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if station_id is not None:
        params["station_id"] = station_id
    if date:
        params["date"] = date
    if last_date:
        params["last_date"] = last_date

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/forecast", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def find_stations(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    max_dist: Optional[int] = 50000,
    name: Optional[str] = None,
) -> dict:
    """Find DWD weather stations near a given location or search by name.
    Use this when the user wants to know which weather stations are available in an area,
    or when you need to look up a station ID before fetching weather data.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if max_dist is not None:
        params["max_dist"] = max_dist
    if name:
        params["name"] = name

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/stations", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_alerts(
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    warn_cell_id: Optional[int] = None,
) -> dict:
    """Retrieve active weather alerts and warnings issued by DWD for a specific location.
    Use this when the user asks about weather warnings, severe weather events, storms,
    or any official weather alerts currently in effect for an area in Germany.
    """
    params = {}
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if warn_cell_id is not None:
        params["warn_cell_id"] = warn_cell_id

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/alerts", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_radar(
    date: Optional[str] = None,
    last_date: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
    distance: Optional[int] = None,
) -> dict:
    """Retrieve radar precipitation data for Germany, including current and recent
    precipitation intensity across a geographic area. Use this when the user asks about
    rainfall radar, precipitation maps, or where it is currently raining in Germany.
    """
    params = {}
    if date:
        params["date"] = date
    if last_date:
        params["last_date"] = last_date
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon
    if distance is not None:
        params["distance"] = distance

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/radar", params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_synop(
    date: str,
    last_date: Optional[str] = None,
    station_id: Optional[int] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
) -> dict:
    """Retrieve raw SYNOP meteorological observation reports from DWD stations.
    Use this when the user or a technical workflow needs raw synoptic observation data
    including pressure, visibility, cloud cover, and other detailed meteorological
    parameters not available in standard weather observations.
    """
    params = {"date": date}
    if last_date:
        params["last_date"] = last_date
    if station_id is not None:
        params["station_id"] = station_id
    if lat is not None:
        params["lat"] = lat
    if lon is not None:
        params["lon"] = lon

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/synop", params=params)
        response.raise_for_status()
        return response.json()




_SERVER_SLUG = "brightsky"

def _track(tool_name: str, ua: str = ""):
    try:
        import urllib.request, json as _json
        data = _json.dumps({"slug": _SERVER_SLUG, "event": "tool_call", "tool": tool_name, "user_agent": ua}).encode()
        req = urllib.request.Request("https://www.volspan.dev/api/analytics/event", data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass

async def health(request):
    return JSONResponse({"status": "ok", "server": mcp.name})

async def tools(request):
    registered = await mcp.list_tools()
    tool_list = [{"name": t.name, "description": t.description or ""} for t in registered]
    return JSONResponse({"tools": tool_list, "count": len(tool_list)})

mcp_app = mcp.http_app(transport="streamable-http")

class _FixAcceptHeader:
    """Ensure Accept header includes both types FastMCP requires."""
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            accept = headers.get(b"accept", b"").decode()
            if "text/event-stream" not in accept:
                new_headers = [(k, v) for k, v in scope["headers"] if k != b"accept"]
                new_headers.append((b"accept", b"application/json, text/event-stream"))
                scope = dict(scope, headers=new_headers)
        await self.app(scope, receive, send)

app = _FixAcceptHeader(Starlette(
    routes=[
        Route("/health", health),
        Route("/tools", tools),
        Mount("/", mcp_app),
    ],
    lifespan=mcp_app.lifespan,
))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
