def classify_intent(message: str) -> str:
    """
    A simple keyword-based intent classifier.
    Since we are using Copilot Studio as the brain, this helps route to Supabase 
    before sending the context to Copilot.
    """
    msg = message.lower()
    
    if any(word in msg for word in ["food", "eat", "restaurant", "cuisine", "hungry", "cafe"]):
        return "find_food"
    if any(word in msg for word in ["store", "shop", "buy", "purchase", "clothing", "electronics"]):
        return "find_store"
    if any(word in msg for word in ["direction", "where", "how to get", "location", "floor", "map"]):
        return "get_directions"
    if any(word in msg for word in ["toilet", "bathroom", "restroom", "atm", "parking", "elevator", "lift"]):
        return "find_facility"
    if any(word in msg for word in ["event", "show", "happen", "happening", "today", "concert", "movie"]):
        return "get_events"
    
    return "customer_support"
