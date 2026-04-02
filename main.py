import os
from fastapi import FastAPI
from supabase import create_client
from dotenv import load_dotenv

# Load local .env for local testing (Railway sets its own env vars)
load_dotenv()

# Project Metadata for Copilot Studio Generative AI
app = FastAPI(
    title="Mall Assistant Data API",
    description="Provides real-time information about mall deals, store offers, and upcoming events.",
    version="1.0.0"
)

# Environment Variables (Set these in Railway Dashboard)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

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

@app.get("/", include_in_schema=False)
def home():
    status = "UP" if supabase else "CONFIG_ERROR"
    return {
        "status": status,
        "supabase_initialized": bool(supabase),
        "endpoints": ["/deals", "/events"]
    }
