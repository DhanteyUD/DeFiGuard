"""
DeFiGuard Integration Tests
Run these tests to verify all agents are working correctly
"""

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from uagents import Agent, Model, Context
from agents.portfolio_monitor import Portfolio
from agents.risk_analysis import RiskAnalysisRequest
from agents.fraud_detection import TokenAnalysisRequest
from agents.market_data import MarketDataRequest
from datetime import datetime, timezone
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


class GenericMessage(Model):
    content: dict


# Test agent
test_agent = Agent(
    name="test_client",
    seed="test_agent_seed_123",
    port=9000,
    endpoint=["http://localhost:9000/submit"]
)

print(f"Test Agent Address: {test_agent.address}")

# Store addresses from .env
PORTFOLIO_AGENT = os.getenv("PORTFOLIO_AGENT_ADDRESS", "")
RISK_AGENT = os.getenv("RISK_AGENT_ADDRESS", "")
FRAUD_AGENT = os.getenv("FRAUD_AGENT_ADDRESS", "")
MARKET_AGENT = os.getenv("MARKET_AGENT_ADDRESS", "")


@test_agent.on_event("startup")
async def run_tests(ctx: Context):
    """Run comprehensive system tests"""
    ctx.logger.info("=" * 60)
    ctx.logger.info("Starting DeFiGuard Tests")
    ctx.logger.info("=" * 60)

    await asyncio.sleep(3)  # Wait for agents to be ready

    # Test 1: Portfolio Registration
    ctx.logger.info("\n📝 Test 1: Portfolio Registration")
    if PORTFOLIO_AGENT:
        portfolio = Portfolio(
            user_id="test_user_001",
            wallets=["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"],
            chains=["ethereum", "polygon"],
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        await ctx.send(PORTFOLIO_AGENT, portfolio)
        ctx.logger.info("✓ Portfolio registration message sent")
    else:
        ctx.logger.error("✗ Portfolio agent address not configured")

    await asyncio.sleep(2)

    # Test 2: Risk Analysis Request
    ctx.logger.info("\n🔍 Test 2: Risk Analysis")
    if RISK_AGENT:
        risk_request = RiskAnalysisRequest(
            user_id="test_user_001",
            total_value_usd=50000.0,
            assets=[
                {
                    "token": "ETH",
                    "balance": 10.0,
                    "value_usd": 20000.0,
                    "price": 2000.0,
                    "change_24h": 5.2,
                    "chain": "ethereum"
                },
                {
                    "token": "USDC",
                    "balance": 30000.0,
                    "value_usd": 30000.0,
                    "price": 1.0,
                    "change_24h": 0.1,
                    "chain": "ethereum"
                }
            ],
            timestamp=datetime.now(timezone.utc).isoformat(),
            risk_score=0.3
        )
        await ctx.send(RISK_AGENT, risk_request)
        ctx.logger.info("✓ Risk analysis request sent")
    else:
        ctx.logger.error("✗ Risk agent address not configured")

    await asyncio.sleep(2)

    # Test 3: Market Data Request
    ctx.logger.info("\n📊 Test 3: Market Data Fetch")
    if MARKET_AGENT:
        market_request = MarketDataRequest(
            token_ids=["bitcoin", "ethereum", "usd-coin"],
            request_type="all"
        )
        await ctx.send(MARKET_AGENT, market_request)
        ctx.logger.info("✓ Market data request sent")
    else:
        ctx.logger.error("✗ Market agent address not configured")

    await asyncio.sleep(2)

    # Test 4: Fraud Detection
    ctx.logger.info("\n🕵️ Test 4: Fraud Detection")
    if FRAUD_AGENT:
        fraud_request = TokenAnalysisRequest(
            token_address="0x1234567890abcdef1234567890abcdef12345678",
            chain="ethereum"
        )
        await ctx.send(FRAUD_AGENT, fraud_request)
        ctx.logger.info("✓ Fraud detection request sent")
    else:
        ctx.logger.error("✗ Fraud agent address not configured")

    ctx.logger.info("\n" + "=" * 60)
    ctx.logger.info("All tests dispatched! Check agent logs for responses.")
    ctx.logger.info("=" * 60)


# Message handlers for test responses
@test_agent.on_message(model=GenericMessage)
async def handle_response(ctx: Context, sender: str, msg: GenericMessage):
    """Handle responses from agents"""
    ctx.logger.info(f"\n📨 Response received from {sender[:16]}...")
    ctx.logger.info(f"Message type: {type(msg).__name__}")

    # Pretty print based on message type
    if hasattr(msg, '__dict__'):
        ctx.logger.info("Response content:")
        for key, value in msg.__dict__.items():
            if not key.startswith('_'):
                ctx.logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    print("🧪 Starting DeFiGuard Tests...")
    print(f"Test Agent Address: {test_agent.address}")
    print("\nMake sure all DeFiGuard agents are running!")
    print("Run 'python main.py' in another terminal first.\n")
    test_agent.run()
