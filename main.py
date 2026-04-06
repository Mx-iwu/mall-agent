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

@app.get(
    "/deals", 
    summary="Get Mall Deals and Store Offers",
    description="Returns a list of all current discounts, sales, and special offers available from stores in the mall."
)
def get_deals():
    if not supabase:
        return {"error": "Database not initialized. Check Railway environment variables."}
    try:
        response = supabase.table("deals").select("*").execute()
        return response.data
    except Exception as e:
        return {"error": f"Database query failed: {e}"}

@app.get(
    "/events",
    summary="Get Mall Events and Activities",
    description="Returns a list of upcoming live events, performances, activities, and schedules happening at the mall."
)
def get_events():
    if not supabase:
        return {"error": "Database not initialized. Check Railway environment variables."}
    try:
        response = supabase.table("events").select("*").execute()
        return response.data
    except Exception as e:
        return {"error": f"Database query failed: {e}"}

@app.get(
    "/stores",
    summary="Get Store Directory",
    description="Search for fashion, sports, and accessories stores. Filter by floor or category (Fashion, Sports, Accessories, Electronics)."
)
def get_stores(category: Optional[str] = None, floor: Optional[str] = None):
    if not supabase: return {"error": "DB error"}
    query = supabase.table("stores").select("*")
    if category: query = query.eq("category", category)
    if floor: query = query.eq("floor", floor)
    try:
        return query.execute().data
    except Exception as e: return {"error": str(e)}

@app.get(
    "/dining",
    summary="Get Dining Directory",
    description="Search for food court, premium dining, and quick service outlets. Filter by floor or cuisine."
)
def get_dining(category: Optional[str] = None, cuisine: Optional[str] = None):
    if not supabase: return {"error": "DB error"}
    query = supabase.table("dining").select("*")
    if category: query = query.eq("category", category)
    if cuisine: query = query.eq("cuisine", cuisine)
    try:
        return query.execute().data
    except Exception as e: return {"error": str(e)}

@app.get(
    "/user",
    summary="Find Existing User Profile",
    description="Search for a user by name, email, or phone number."
)
def get_user(identifier: str):
    if not supabase:
        return {"error": "Database not initialized."}
    try:
        # Search by phone, email, or name
        for field in ["phone_number", "email", "name"]:
            response = supabase.table("users").select("*").eq(field, identifier).execute()
            if response.data:
                return response.data
        return {"message": "User not found."}
    except Exception as e:
        return {"error": f"Query failed: {e}"}

@app.post(
    "/user",
    summary="Register or Update User",
    description="Registers a new user or updates the details and last activity of an existing user."
)
def register_user(user: UserCreate):
    if not supabase:
        return {"error": "Database not initialized."}
    try:
        # Check if user exists (by phone)
        existing = supabase.table("users").select("*").eq("phone_number", user.phone_number).execute()
        
        data = {
            "name": user.name,
            "phone_number": user.phone_number,
            "email": user.email,
            "last_activity": user.last_activity
        }
        
        if existing.data:
            # Update
            response = supabase.table("users").update(data).eq("phone_number", user.phone_number).execute()
        else:
            # Insert
            response = supabase.table("users").insert(data).execute()
            
        return response.data
    except Exception as e:
        return {"error": f"Operation failed: {e}"}

@app.get(
    "/orders",
    summary="Get User Order History",
    description="Fetch a list of orders for a specific user identified by their phone number."
)
def get_orders(phone_number: str):
    if not supabase:
        return {"error": "Database not initialized."}
    try:
        # Find user first
        user_response = supabase.table("users").select("id").eq("phone_number", phone_number).execute()
        if not user_response.data:
            return {"error": "User not found."}
        
        user_id = user_response.data[0]["id"]
        orders_response = supabase.table("customer_orders").select("*").eq("user_id", user_id).execute()
        return orders_response.data
    except Exception as e:
        return {"error": f"Query failed: {e}"}

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
    status = "UP" if (supabase and MAPBOX_ACCESS_TOKEN) else "PARTIAL_CONFIG"
    return {
        "status": status,
        "supabase_initialized": bool(supabase),
        "mapbox_initialized": bool(MAPBOX_ACCESS_TOKEN),
        "endpoints": ["/deals", "/events", "/user", "/orders", "/directions", "/stores", "/dining"]
    }
