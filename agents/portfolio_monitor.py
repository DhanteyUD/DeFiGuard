from uagents import Agent, Context, Model
# from uagents.setup import fund_agent_if_low
from datetime import datetime, timezone
from typing import List, Dict
import os
from dotenv import load_dotenv
import aiohttp
import asyncio
import json

load_dotenv()


# Data Models
class Portfolio(Model):
    user_id: str
    wallets: List[str]
    chains: List[str]
    timestamp: str


class AssetBalance(Model):
    token: str
    balance: float
    value_usd: float
    chain: str
    price: float
    change_24h: float


class PortfolioSnapshot(Model):
    user_id: str
    total_value_usd: float
    assets: List[Dict]
    timestamp: str
    risk_score: float


class MessageResponse(Model):
    message: str


# Create Portfolio Monitor Agent
portfolio_agent = Agent(
    name="portfolio_monitor",
    seed=os.getenv("PORTFOLIO_AGENT_SEED", "portfolio_demo_seed"),
    port=8000,
    endpoint=["http://localhost:8000/submit"],
    # mailbox=False  # type: ignore[arg-type]
)

# fund_agent_if_low(str(portfolio_agent.wallet.address()))

# In-memory storage (use database in production)
portfolios_db = {}
snapshots_db = []

print(f"Portfolio Monitor Agent Address: {portfolio_agent.address}")


# Helper functions
async def fetch_token_price(token_symbol: str) -> Dict:
    """Fetch token price from CoinGecko"""
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": token_symbol.lower(),
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                token_data = data.get(token_symbol.lower(), {})
                return {
                    "price": token_data.get("usd", 0),
                    "change_24h": token_data.get("usd_24h_change", 0)
                }

    except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
        print(f"⚠️ Failed to fetch price for {token_symbol}: {e}")
        return {"price": 0, "change_24h": 0}


async def get_wallet_balance(wallet: str, chain: str) -> List[Dict]:
    """Simulate getting wallet balances (integrate with Web3 in production)"""

    print(f"Fetching wallet balances for {wallet}")

    # Demo data - replace with actual blockchain queries
    demo_balances = [
        {
            "token": "ethereum",
            "symbol": "ETH",
            "balance": 2.5,
            "chain": chain
        },
        {
            "token": "usd-coin",
            "symbol": "USDC",
            "balance": 5000,
            "chain": chain
        },
        {
            "token": "polygon",
            "symbol": "MATIC",
            "balance": 1500,
            "chain": chain
        }
    ]

    # Fetch prices
    enriched_balances = []
    for asset in demo_balances:
        price_data = await fetch_token_price(asset["token"])
        enriched_balances.append({
            "token": asset["symbol"],
            "balance": asset["balance"],
            "price": price_data["price"],
            "value_usd": asset["balance"] * price_data["price"],
            "change_24h": price_data["change_24h"],
            "chain": asset["chain"]
        })

    return enriched_balances


def calculate_risk_score(assets: List[Dict]) -> float:
    """Calculate basic risk score based on volatility and concentration"""
    if not assets:
        return 0.0

    total_value = sum(a["value_usd"] for a in assets)
    if total_value == 0:
        return 0.0

    # Concentration risk (Herfindahl index)
    concentration = sum((a["value_usd"] / total_value) ** 2 for a in assets)

    # Volatility risk (based on 24h change)
    avg_volatility = sum(abs(a.get("change_24h", 0)) for a in assets) / len(assets)
    volatility_score = min(avg_volatility / 20, 1)  # Normalize to 0-1

    # Combined risk score
    risk_score = (concentration * 0.4) + (volatility_score * 0.6)

    return min(risk_score, 1.0)


# Message Handlers
@portfolio_agent.on_message(model=Portfolio)
async def register_portfolio(ctx: Context, sender: str, msg: Portfolio):
    """Register a new portfolio for monitoring"""
    ctx.logger.info(f"Registering portfolio for user: {msg.user_id}")

    # Store portfolio
    portfolios_db[msg.user_id] = {
        "wallets": msg.wallets,
        "chains": msg.chains,
        "registered_at": msg.timestamp,
        "owner": sender
    }

    # Send confirmation
    await ctx.send(sender, MessageResponse(message=f"Portfolio registered for {msg.user_id}"))

    # Trigger initial snapshot
    await scan_portfolio(ctx, msg.user_id)


async def scan_portfolio(ctx: Context, user_id: str):
    """Scan portfolio and create snapshot"""
    if user_id not in portfolios_db:
        ctx.logger.warning(f"Portfolio {user_id} not found")
        return

    portfolio = portfolios_db[user_id]
    all_assets = []
    total_value = 0

    # Scan each wallet on each chain
    for wallet in portfolio["wallets"]:
        for chain in portfolio["chains"]:
            balances = await get_wallet_balance(wallet, chain)
            all_assets.extend(balances)
            total_value += sum(b["value_usd"] for b in balances)

    # Calculate basic risk score (0-1)
    risk_score = calculate_risk_score(all_assets)

    # Create snapshot
    snapshot = PortfolioSnapshot(
        user_id=user_id,
        total_value_usd=total_value,
        assets=all_assets,
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=risk_score
    )

    snapshots_db.append(snapshot)

    ctx.logger.info(f"Portfolio snapshot: ${total_value:.2f}, Risk: {risk_score:.2f}")

    # Send to Risk Analysis Agent
    risk_agent_address = os.getenv("RISK_AGENT_ADDRESS", "")
    if risk_agent_address:
        await ctx.send(risk_agent_address, snapshot)

    return snapshot


# Periodic monitoring
@portfolio_agent.on_interval(period=300.0)  # Every 5 minutes
async def monitor_portfolios(ctx: Context):
    """Periodically scan all registered portfolios"""
    ctx.logger.info(f"Monitoring {len(portfolios_db)} portfolios...")

    for user_id in portfolios_db:
        await scan_portfolio(ctx, user_id)


@portfolio_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Portfolio Monitor Agent started!")
    ctx.logger.info(f"Agent address: {portfolio_agent.address}")


if __name__ == "__main__":
    portfolio_agent.run()
