from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str
    
    COPILOT_STUDIO_SECRET: str
    OPENAI_API_KEY: str = "optional"
    
    model_config = SettingsConfigDict(env_file=r"c:\Users\HomePC\Downloads\Mall Manager agent\mallmate_ai\.env")

settings = Settings()
