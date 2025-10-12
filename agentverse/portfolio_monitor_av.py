"""
DeFiGuard Portfolio Monitor Agent - Agentverse Deployment Version
This is a standalone, self-contained version ready for Agentverse deployment
"""

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from datetime import datetime, timezone
from typing import List, Dict
import os
import aiohttp
import asyncio

# ============================================
# DATA MODELS
# ============================================

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

# ============================================
# AGENT CONFIGURATION (AGENTVERSE)
# ============================================

# Create Portfolio Monitor Agent for Agentverse
# Note: No port or endpoint - uses mailbox instead
portfolio_agent = Agent(
    name="portfolio_monitor",
    seed=os.getenv("PORTFOLIO_AGENT_SEED"), # Set this in Agentverse UI
    mailbox="https://agentverse.ai/mailbox"  # Required for Agentverse
)

# Fund agent (will use Agentverse wallet)
fund_agent_if_low(str(portfolio_agent.wallet.address()))

# ============================================
# STORAGE
# ============================================

# In-memory storage (Agentverse agents restart, so use external DB in production)
portfolios_db = {}
snapshots_db = []

print(f"Portfolio Monitor Agent Address: {portfolio_agent.address}")

# ============================================
# HELPER FUNCTIONS
# ============================================

async def fetch_token_price(token_symbol: str) -> Dict:
    """Fetch token price from CoinGecko API"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": token_symbol.lower(),
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    token_data = data.get(token_symbol.lower(), {})
                    return {
                        "price": token_data.get("usd", 0),
                        "change_24h": token_data.get("usd_24h_change", 0)
                    }
    except Exception as e:
        print(f"Error fetching price: {e}")

    return {"price": 0, "change_24h": 0}

async def get_wallet_balance(wallet: str, chain: str) -> List[Dict]:
    """
    Get wallet balances
    NOTE: Using demo data for hackathon
    In production, integrate with Web3 providers
    """

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
        }
    ]

    # Fetch real prices
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
    """Calculate basic risk score (0-1)"""
    if not assets:
        return 0.0

    total_value = sum(a["value_usd"] for a in assets)
    if total_value == 0:
        return 0.0

    # Concentration risk (Herfindahl index)
    concentration = sum((a["value_usd"] / total_value) ** 2 for a in assets)

    # Volatility risk (based on 24h change)
    avg_volatility = sum(abs(a.get("change_24h", 0)) for a in assets) / len(assets)
    volatility_score = min(avg_volatility / 20, 1)

    # Combined risk score
    risk_score = (concentration * 0.4) + (volatility_score * 0.6)

    return min(risk_score, 1.0)

# ============================================
# MESSAGE HANDLERS
# ============================================

@portfolio_agent.on_message(model=Portfolio)
async def register_portfolio(ctx: Context, sender: str, msg: Portfolio):
    """Register a new portfolio for monitoring"""
    ctx.logger.info(f"📝 Registering portfolio for user: {msg.user_id}")

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
            try:
                balances = await get_wallet_balance(wallet, chain)
                all_assets.extend(balances)
                total_value += sum(b["value_usd"] for b in balances)
            except Exception as e:
                ctx.logger.error(f"Error scanning {wallet} on {chain}: {e}")

    # Calculate risk score
    risk_score = calculate_risk_score(all_assets)

    # Create snapshot
    snapshot = {
        "user_id": user_id,
        "total_value_usd": total_value,
        "assets": all_assets,
        "timestamp": datetime.now(timezone.utc),
        "risk_score": risk_score
    }

    snapshots_db.append(snapshot)

    ctx.logger.info(
        f"📊 Portfolio snapshot created: "
        f"${total_value:.2f}, Risk: {risk_score:.2%}"
    )

    # Send to Risk Analysis Agent (configure address in Agentverse)
    # RISK_AGENT_ADDRESS = "agent1qz3y..."  # Set this after deploying Risk Agent
    # if RISK_AGENT_ADDRESS:
    #     await ctx.send(RISK_AGENT_ADDRESS, snapshot)

    return snapshot

# ============================================
# PERIODIC MONITORING
# ============================================

@portfolio_agent.on_interval(period=300.0)  # Every 5 minutes
async def monitor_portfolios(ctx: Context):
    """Periodically scan all registered portfolios"""
    if not portfolios_db:
        return

    ctx.logger.info(f"🔄 Monitoring {len(portfolios_db)} portfolio(s)...")

    for user_id in list(portfolios_db.keys()):
        try:
            await scan_portfolio(ctx, user_id)
            await asyncio.sleep(2)  # Rate limiting
        except Exception as e:
            ctx.logger.error(f"Error monitoring {user_id}: {e}")

# ============================================
# STARTUP
# ============================================

@portfolio_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info("🛡️  DeFiGuard Portfolio Monitor Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {portfolio_agent.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("=" * 60)

# ============================================
# RUN AGENT
# ============================================

if __name__ == "__main__":
    portfolio_agent.run()