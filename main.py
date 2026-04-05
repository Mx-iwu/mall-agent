import os
import requests
from fastapi import FastAPI, HTTPException, Query
from supabase import create_client
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, List

# Load local .env for local testing (Railway sets its own env vars)
load_dotenv()

# Project Metadata for Copilot Studio Generative AI
app = FastAPI(
    title="Mall Assistant Data API",
    description="Provides real-time information about mall deals, store offers, events, and user history with multi-mode Mapbox Directions.",
    version="1.3.0"
)

# Environment Variables (Set these in Railway Dashboard)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

# Virtual Mall Location: Ikeja City Mall, Lagos
MALL_LON = 3.3333
MALL_LAT = 6.5833

# Initialize Supabase client
supabase = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully.")
    else:
        print("❌ CRITICAL: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing!")
except Exception as e:
    print(f"❌ CRITICAL: Failed to initialize Supabase client: {e}")

# --- Pydantic Models ---
class UserCreate(BaseModel):
    name: str
    phone_number: str
    email: str
    last_activity: Optional[str] = None

# --- Helpers ---

def get_coordinates(address: str):
    """Converts an address or location name to coordinates using Mapbox Geocoding API."""
    if not MAPBOX_ACCESS_TOKEN:
        return None
    
    # Check if the address is already coordinates (e.g., "6.45,3.39")
    try:
        parts = address.split(",")
        if len(parts) == 2:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            return [lon, lat] # Mapbox uses [lon, lat]
    except ValueError:
        pass

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {"access_token": MAPBOX_ACCESS_TOKEN, "limit": 1}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            return data["features"][0]["center"]  # [longitude, latitude]
    return None

def fetch_mapbox_route(profile: str, start_coords: list, end_coords: list):
    """Fetches a specific route profile from Mapbox."""
    coords_str = f"{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    url = f"https://api.mapbox.com/directions/v5/mapbox/{profile}/{coords_str}"
    params = {
        "access_token": MAPBOX_ACCESS_TOKEN,
        "geometries": "geojson",
        "steps": "true",
        "overview": "full"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["routes"]:
            route = data["routes"][0]
            # Extract basic instructions
            instructions = [step["maneuver"]["instruction"] for leg in route["legs"] for step in leg["steps"]]
            return {
                "distance_meters": route["distance"],
                "duration_seconds": route["duration"],
                "instructions": instructions
            }
    return None

# --- Endpoints ---

@app.get("/deals", summary="Get Mall Deals")
def get_deals():
    if not supabase: return {"error": "DB error"}
    try:
        return supabase.table("deals").select("*").execute().data
    except Exception as e: return {"error": str(e)}

@app.get("/events", summary="Get Mall Events")
def get_events():
    if not supabase: return {"error": "DB error"}
    try:
        return supabase.table("events").select("*").execute().data
    except Exception as e: return {"error": str(e)}

@app.get("/user", summary="Find User")
def get_user(identifier: str):
    if not supabase: return {"error": "DB error"}
    try:
        for field in ["phone_number", "email", "name"]:
            res = supabase.table("users").select("*").eq(field, identifier).execute()
            if res.data: return res.data
        return {"message": "Not found"}
    except Exception as e: return {"error": str(e)}

@app.post("/user", summary="Register User")
def register_user(user: UserCreate):
    if not supabase: return {"error": "DB error"}
    try:
        data = user.dict()
        existing = supabase.table("users").select("*").eq("phone_number", user.phone_number).execute()
        if existing.data:
            return supabase.table("users").update(data).eq("phone_number", user.phone_number).execute().data
        return supabase.table("users").insert(data).execute().data
    except Exception as e: return {"error": str(e)}

@app.get("/orders", summary="Get Orders")
def get_orders(phone_number: str):
    if not supabase: return {"error": "DB error"}
    try:
        user = supabase.table("users").select("id").eq("phone_number", phone_number).execute()
        if not user.data: return {"error": "User not found"}
        return supabase.table("customer_orders").select("*").eq("user_id", user.data[0]["id"]).execute().data
    except Exception as e: return {"error": str(e)}

@app.get(
    "/directions",
    summary="Get Multi-Mode Mall Directions",
    description="Calculates both Driving and Walking directions from the user's location to Ikeja City Mall."
)
def get_directions(origin: str, destination: Optional[str] = "Ikeja City Mall"):
    if not MAPBOX_ACCESS_TOKEN:
        return {"error": "Mapbox Token missing"}
    
    # 1. Resolve coordinates
    start_coords = get_coordinates(origin)
    
    # Destination is fixed to the Mall if not specified or matching mall name
    if destination.lower() in ["ikeja city mall", "the mall", "mall"]:
        end_coords = [MALL_LON, MALL_LAT]
    else:
        end_coords = get_coordinates(destination)
    
    if not start_coords or not end_coords:
        return {"error": "Could not resolve locations."}
    
    # 2. Fetch both Driving and Walking routes
    driving_route = fetch_mapbox_route("driving", start_coords, end_coords)
    walking_route = fetch_mapbox_route("walking", start_coords, end_coords)
    
    return {
        "origin_coordinates": start_coords,
        "destination_name": destination,
        "destination_coordinates": end_coords,
        "routes": {
            "driving": driving_route,
            "walking": walking_route
        }
    }

@app.get("/", include_in_schema=False)
def home():
    return {
        "status": "UP",
        "mapbox_initialized": bool(MAPBOX_ACCESS_TOKEN),
        "mall_location": {"lat": MALL_LAT, "lon": MALL_LON},
        "endpoints": ["/deals", "/events", "/user", "/orders", "/directions"]
    }
