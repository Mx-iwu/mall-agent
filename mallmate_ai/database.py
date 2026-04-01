from supabase import create_client, Client
from mallmate_ai.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def get_restaurants_by_cuisine(cuisine: str):
    """Fetch restaurants from Supabase by cuisine type."""
    response = supabase.table("restaurants").select("*").ilike("cuisine", f"%{cuisine}%").execute()
    return response.data

def get_stores_by_category(category: str):
    """Fetch stores from Supabase by category."""
    response = supabase.table("stores").select("*").ilike("category", f"%{category}%").execute()
    return response.data

def get_facilities(facility_type: str):
    """Fetch facilities from Supabase by type."""
    response = supabase.table("facilities").select("*").ilike("type", f"%{facility_type}%").execute()
    return response.data

def get_events():
    """Fetch upcoming events from Supabase."""
    response = supabase.table("events").select("*").execute()
    return response.data
