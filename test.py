import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

if "HF_TOKEN" not in os.environ:
    print("❌ HF_TOKEN not found in environment")
    sys.exit(1)

# Initialize OpenAI client for HuggingFace Router
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

MODEL = "meta-llama/Llama-3.3-70B-Instruct:together"

# Conversation memory
messages = [
    {
        "role": "system",
        "content": "You are a helpful, precise, and technical AI assistant."
    }
]

print("💬 LLaMA CLI Chat")
print("Type 'exit' or 'quit' to leave\n")

try:
    while True:
        user_input = input("You ▶ ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("\n👋 Exiting chat")
            break

        if not user_input:
            continue

        messages.append({
            "role": "user",
            "content": user_input
        })

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        assistant_reply = response.choices[0].message.content
        messages.append({
            "role": "assistant",
            "content": assistant_reply
        })

        print("\nAI ▶", assistant_reply, "\n")

except KeyboardInterrupt:
    print("\n\n🛑 Interrupted. Bye.")
