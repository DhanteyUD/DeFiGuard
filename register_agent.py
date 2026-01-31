import os
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

# export AGENTVERSE_KEY="your-copied-key"
# export AGENT_SEED_PHRASE="your-alert-agent-seed"
# python register_agent.py

register_chat_agent(
    "DeFiGuard-2.0",
    "https://defiguard-production.up.railway.app/submit",
    active=True,
    credentials=RegistrationRequestCredentials(
        agentverse_api_key=os.environ["AGENTVERSE_KEY"],
        agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"],
    ),
)

print("✅ Agent registered successfully!")
print("Check Agentverse dashboard to see your agent.")