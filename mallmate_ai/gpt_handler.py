import httpx
import asyncio
from .config import settings

DIRECT_LINE_URL = "https://directline.botframework.com/v3/directline"

async def generate_mall_response(user_query: str, intent: str, database_results: list) -> str:
    """
    Generate a conversational response by calling the Copilot Studio Direct Line API.
    Sends user query and database context as a single prompt.
    """
    
    # Construct a rich message that includes context for Copilot Studio
    context_message = f"""
    [SYSTEM CONTEXT: You are MallMate AI, the WhatsApp concierge.]
    [USER QUERY: {user_query}]
    [DETECTED INTENT: {intent}]
    [DATABASE RESULTS: {database_results}]
    
    Please provide a helpful, WhatsApp-friendly response to the user based on the above information.
    """
    
    headers = {
        "Authorization": f"Bearer {settings.COPILOT_STUDIO_SECRET}",
        "Content-Type": "application/json"
    }
    
    try:
        # 1. Start a conversation
        with httpx.Client() as client:
            conv_resp = client.post(f"{DIRECT_LINE_URL}/conversations", headers=headers)
            conv_resp.raise_for_status()
            conversation = conv_resp.json()
            conversation_id = conversation["conversationId"]
            
            # 2. Send the message (activity)
            activity_url = f"{DIRECT_LINE_URL}/conversations/{conversation_id}/activities"
            activity_payload = {
                "locale": "en-EN",
                "type": "message",
                "from": {"id": "user1"},
                "text": context_message
            }
            send_resp = client.post(activity_url, headers=headers, json=activity_payload)
            send_resp.raise_for_status()
            
            # 3. Poll for the response (In a real app, you'd use websockets or handle multiple activities)
            # For simplicity, we'll wait a moment and then get activities.
            await asyncio.sleep(2) # Give Copilot a moment to think
            
            get_resp = client.get(activity_url, headers=headers)
            get_resp.raise_for_status()
            activities = get_resp.json().get("activities", [])
            
            # Find the last message from the bot
            bot_responses = [a["text"] for a in activities if a["from"]["id"] != "user1" and "text" in a]
            
            if bot_responses:
                return bot_responses[-1]
            
            return "I'm processing your request, but I couldn't get a final answer from my brain right now. 🧪"

    except Exception as e:
        print(f"Copilot Studio Error: {e}")
        return "I’m having trouble connecting to my central brain right now. Please try again in a moment! 🛠️"
