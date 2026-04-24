import random
import httpx
from fastmcp import FastMCP
from mangum import Mangum

mcp = FastMCP("ds5220-demo")

@mcp.tool
def roll_dice(sides: int = 6, count: int = 1) -> list[int]:
    """Roll `count` dice with `sides` faces each."""
    return [random.randint(1, sides) for _ in range(count)]

@mcp.tool
def get_weather(city: str) -> dict:
    """Current temperature (F) and conditions for a city."""
    geo = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
    ).json()
    if not geo.get("results"):
        return {"error": f"city not found: {city}"}
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]
    weather = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "temperature_unit": "fahrenheit",
        },
    ).json()
    return weather["current_weather"]

# FastMCP exposes a Starlette ASGI app for the streamable-http transport;
# Mangum adapts any ASGI app to the Lambda event/context interface.
handler = Mangum(mcp.http_app())
