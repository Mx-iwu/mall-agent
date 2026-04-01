from twilio.twiml.messaging_response import MessagingResponse

def create_twilio_response(generated_text: str) -> str:
    """Helper to return TwiML for Twilio messaging response."""
    response = MessagingResponse()
    response.message(generated_text)
    return str(response)
