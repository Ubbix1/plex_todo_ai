import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ✅ FIX 1: correct variable name
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = "meta-llama/Llama-3.3-70B-Instruct:together"

if not HF_TOKEN:
    raise RuntimeError("❌ HF_TOKEN not found in environment")

URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "Return ONLY valid JSON. Keys: title, time, date, repeat, priority."},
        {"role": "user", "content": "Add gym every weekday at 6am"}
    ],
    "max_tokens": 150,
    "temperature": 0.1
}

response = requests.post(URL, headers=headers, json=payload, timeout=60)

print("Status:", response.status_code)
print("Raw response text:")
print(response.text)

# ✅ FIX 2: parse JSON only if safe
try:
    data = response.json()
    print("\nParsed JSON:")
    print(data)
except Exception:
    print("\n⚠️ Response is not JSON (this is normal for errors)")
