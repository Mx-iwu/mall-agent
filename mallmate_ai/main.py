from fastapi import FastAPI
from supabase import create_client

app = FastAPI()

SUPABASE_URL = "https://ndmbiwwgwfyugezunbxz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5kbWJpnddnd2Z5dWdlenVuanh6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzEzMzA5OSwiZXhwIjoyMDU4NzA5MDk5fQ.eByS_l6x4S_L5_x4S_L5_x4S_L5_x4S_L5_x4S_L5_x4"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/deals")
def get_deals():
    response = supabase.table("deals").select("*").execute()
    return response.data

@app.get("/events")
def get_events():
    response = supabase.table("events").select("*").execute()
    return response.data
