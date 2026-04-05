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
    description="Provides real-time information about mall deals, store offers, events, and user history with Mapbox Directions.",
    version="1.2.0"
)

# Environment Variables (Set these in Railway Dashboard)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

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
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {"access_token": MAPBOX_ACCESS_TOKEN, "limit": 1}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            return data["features"][0]["center"]  # [longitude, latitude]
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
    "/user",
    summary="Find Existing User Profile",
    description="Search for a user by name, email, or phone number to recognize an existing customer."
)
def get_user(identifier: str):
    if not supabase:
        return {"error": "Database not initialized."}
    try:
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
        existing = supabase.table("users").select("*").eq("phone_number", user.phone_number).execute()
        data = {
            "name": user.name,
            "phone_number": user.phone_number,
            "email": user.email,
            "last_activity": user.last_activity
        }
        if existing.data:
            response = supabase.table("users").update(data).eq("phone_number", user.phone_number).execute()
        else:
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
    summary="Get Mall Directions",
    description="Provides walking directions between two mall locations (origin and destination) using Mapbox."
)
def get_directions(origin: str, destination: str):
    if not MAPBOX_ACCESS_TOKEN:
        return {"error": "Mapbox Access Token not configured. Check MAPBOX_ACCESS_TOKEN."}
    
    # 1. Geocode both locations
    start_coords = get_coordinates(origin)
    end_coords = get_coordinates(destination)
    
    if not start_coords or not end_coords:
        return {"error": f"Could not find coordinates for {origin} or {destination}."}
    
    # 2. Get directions from Mapbox
    # Format: lon,lat;lon,lat
    coords_str = f"{start_coords[0]},{start_coords[1]};{end_coords[0]},{end_coords[1]}"
    url = f"https://api.mapbox.com/directions/v5/mapbox/walking/{coords_str}"
    params = {
        "access_token": MAPBOX_ACCESS_TOKEN,
        "geometries": "geojson",
        "steps": "true"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Mapbox API error: {response.text}"}

@app.get("/", include_in_schema=False)
def home():
    status = "UP" if (supabase and MAPBOX_ACCESS_TOKEN) else "PARTIAL_CONFIG"
    return {
        "status": status,
        "supabase_initialized": bool(supabase),
        "mapbox_initialized": bool(MAPBOX_ACCESS_TOKEN),
        "endpoints": ["/deals", "/events", "/user", "/orders", "/directions"]
    }
