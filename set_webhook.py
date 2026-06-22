#!/usr/bin/env python3
"""
تنظیم Webhook تلگرام به Appwrite Function
اجرا: python set_webhook.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FUNCTION_URL = os.getenv("FUNCTION_URL", "")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN در .env موجود نیست!")
    exit(1)

if not FUNCTION_URL:
    print("❌ FUNCTION_URL در .env موجود نیست!")
    print("   ابتدا URL Appwrite Function را در .env قرار دهید:")
    print("   FUNCTION_URL=https://<your-appwrite-function-url>")
    exit(1)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
payload = {
    "url": FUNCTION_URL,
    "drop_pending_updates": True
}

print(f"📡 در حال تنظیم Webhook...")
print(f"   URL: {FUNCTION_URL}")

resp = requests.post(url, json=payload, timeout=30)
data = resp.json()

if data.get("ok"):
    print("✅ Webhook با موفقیت تنظیم شد!")
    print(f"   Result: {data.get('result')}")
    print(f"   Description: {data.get('description')}")
else:
    print("❌ خطا در تنظیم Webhook:")
    print(f"   {data}")
