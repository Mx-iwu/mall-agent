import os
from fastapi import FastAPI
from supabase import create_client
from dotenv import load_dotenv

# Load local .env for local testing (Railway sets its own env vars)
load_dotenv()

app = FastAPI()

# Environment Variables (Set these in Railway Dashboard)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ndmbiwwgwfyugezunbxz.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_KEY:
    print("WARNING: SUPABASE_SERVICE_ROLE_KEY is not set.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/deals")
def get_deals():
    response = supabase.table("deals").select("*").execute()
    return response.data

@app.get("/events")
def get_events():
    response = supabase.table("events").select("*").execute()
    return response.data

@app.get("/")
def home():
    return {"status": "Mall Manager API is running", "endpoints": ["/deals", "/events"]}
