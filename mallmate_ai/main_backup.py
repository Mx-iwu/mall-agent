from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from mallmate_ai.intents import classify_intent
from mallmate_ai.database import (
    get_restaurants_by_cuisine,
    get_stores_by_category,
    get_facilities,
    get_events
)
from mallmate_ai.gpt_handler import generate_mall_response
from mallmate_ai.utils import create_twilio_response

app = FastAPI(title="MallMate AI")

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Twilio Webhook for incoming WhatsApp messages.
    Accepts application/x-www-form-urlencoded.
    """
    form_data = await request.form()
    user_message = form_data.get("Body", "")
    user_number = form_data.get("From", "")
    
    # 1. Detect Intent
    intent = classify_intent(user_message)
    
    # 2. Query Supabase based on intent
    database_results = []
    try:
        if intent == "find_food":
            # Extract cuisine or just general food search
            database_results = get_restaurants_by_cuisine("") 
        elif intent == "find_store":
            database_results = get_stores_by_category("")
        elif intent == "find_facility":
            database_results = get_facilities("")
        elif intent == "get_events":
            database_results = get_events()
        # "get_directions" and "customer_support" may not need direct DB queries here 
        # but let GPT handle the logic with what we have.
    except Exception as e:
        print(f"Database Query Error: {e}")
        database_results = []

    # 3. Generate GPT Response
    generated_text = await generate_mall_response(user_message, intent, database_results)
    
    # 4. Return Twilio XML (TwiML)
    twiml_response = create_twilio_response(generated_text)
    
    return Response(content=twiml_response, media_type="application/xml")

@app.get("/")
async def root():
    return {"message": "MallMate AI is running. Webhook at /webhook"}
