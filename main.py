import os
from fastapi import FastAPI, HTTPException, Query
from supabase import create_client
from dotenv import load_dotenv
from pydantic import BaseModel
import googlemaps
from typing import Optional, List

# Load local .env for local testing (Railway sets its own env vars)
load_dotenv()

# Project Metadata for Copilot Studio Generative AI
app = FastAPI(
    title="Mall Assistant Data API",
    description="Provides real-time information about mall deals, store offers, events, and user history.",
    version="1.1.0"
)

# Environment Variables (Set these in Railway Dashboard)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize client safely to avoid startup crashes
supabase = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully.")
    else:
        print("❌ CRITICAL: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing!")
except Exception as e:
    print(f"❌ CRITICAL: Failed to initialize Supabase client: {e}")

# Initialize Google Maps client
gmaps = None
if GOOGLE_MAPS_API_KEY:
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    print("✅ Google Maps client initialized.")

# --- Pydantic Models ---
class UserCreate(BaseModel):
    name: str
    phone_number: str
    email: str
    last_activity: Optional[str] = None

class Order(BaseModel):
    id: str
    user_id: str
    item_name: str
    status: str
    order_date: str

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
    summary="Get Mall Directions",
    description="Provides detailed directions from a given origin to a specific store or location in the mall using Google Maps."
)
def get_directions(origin: str, destination: str):
    if not gmaps:
        return {"error": "Google Maps API not configured. Check GOOGLE_MAPS_API_KEY."}
    try:
        directions_result = gmaps.directions(origin, destination, mode="walking")
        if not directions_result:
            return {"error": "No route found."}
        return directions_result
    except Exception as e:
        return {"error": f"Google Maps error: {e}"}

@app.get("/", include_in_schema=False)
def home():
    status = "UP" if (supabase and gmaps) else "PARTIAL_CONFIG"
    return {
        "status": status,
        "supabase_initialized": bool(supabase),
        "google_maps_initialized": bool(gmaps),
        "endpoints": ["/deals", "/events", "/user", "/orders", "/directions"]
    }
