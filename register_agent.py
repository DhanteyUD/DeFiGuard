import os
from dotenv import load_dotenv

load_dotenv()

from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

AGENT_NAME = "DeFiGuard-2.0"
AGENT_URL = os.getenv("DEFIGUARD_ENDPOINT")

print(f"🚀 Registering: {AGENT_NAME}")
print(f"📍 URL: {AGENT_URL}")

try:
    register_chat_agent(
        AGENT_NAME,
        AGENT_URL,
        active=True,
        credentials=RegistrationRequestCredentials(
            agentverse_api_key=os.environ["AGENTVERSE_KEY"],
            agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"],
        ),
    )
    print("✅ Registration successful!")
    print(f"\n🎉 Your agent is now available on ASI:One!")
    print(f"   Search for: '{AGENT_NAME}'")

except Exception as e:
    print(f"❌ Registration failed: {e}")
