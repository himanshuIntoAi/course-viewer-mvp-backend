# app/config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = "postgresql://postgres.rzzvwxmsqeghuuhrbjql:tM29gzcG9Qf8RX1x@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

settings = Settings()