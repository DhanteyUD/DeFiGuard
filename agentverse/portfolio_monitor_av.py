from uagents import Agent, Context, Model
from datetime import datetime, timezone
from typing import List, Dict
from web3 import Web3
import aiohttp
import asyncio


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


portfolio_agent = Agent(
    name="portfolio_monitor",
    mailbox=True  # type: ignore[arg-type]
)

print(f"Portfolio Monitor Agent Address: {portfolio_agent.address}")


async def fetch_token_price(token_symbol: str) -> Dict:  # type: ignore[arg-type]
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
    Get real wallet balances using Web3
    """
    chain_rpc = {
        "ethereum": "https://mainnet.infura.io/v3/YOUR_INFURA_KEY",
        "bsc": "https://bsc-dataseed.binance.org/",
        "polygon": "https://polygon-rpc.com"
    }

    rpc_url = chain_rpc.get(chain.lower())
    if not rpc_url:
        raise ValueError(f"No RPC URL configured for chain {chain}")

    web3 = Web3(Web3.HTTPProvider(rpc_url))
    wallet_checksum = Web3.to_checksum_address(wallet)

    if not web3.isConnected():
        raise ConnectionError(f"Unable to connect to {chain} RPC")

    # Get native balance (ETH, BNB, MATIC)
    native_balance = web3.eth.get_balance(wallet_checksum)
    native_balance_eth = web3.fromWei(native_balance, "ether")

    balances = [{
        "token": chain.lower(),
        "symbol": "ETH" if chain.lower() == "ethereum" else chain.upper(),
        "balance": float(native_balance_eth),
        "chain": chain
    }]

    # Optional: Add ERC20 token balances using contract ABI
    # Example for USDC
    erc20_tokens = {
        "ethereum": {
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        }
    }

    if chain.lower() in erc20_tokens:
        for symbol, addr in erc20_tokens[chain.lower()].items():
            contract = web3.eth.contract(address=addr, abi=[
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                }
            ])
            token_balance = contract.functions.balanceOf(wallet).call()
            decimals = 6 if symbol == "USDC" else 18
            balances.append({
                "token": symbol,
                "symbol": symbol,
                "balance": token_balance / (10 ** decimals),
                "chain": chain
            })

    #     print(f"Fetching wallet balances for {wallet}")
    #
    #
    #     # Demo data - replace with actual blockchain queries
    #     demo_balances = [
    #         {
    #             "token": "ethereum",
    #             "symbol": "ETH",
    #             "balance": 2.5,
    #             "chain": chain
    #         },
    #         {
    #             "token": "usd-coin",
    #             "symbol": "USDC",
    #             "balance": 5000,
    #             "chain": chain
    #         }
    #     ]
    #

    # Fetch USD prices for all tokens
    enriched_balances = []
    for asset in balances:
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


async def add_portfolio_key(ctx: Context, key: str):
    """Add portfolio key to the master list"""
    keys = ctx.storage.get("portfolio_keys") or []
    if key not in keys:
        keys.append(key)
        ctx.storage.set("portfolio_keys", keys)


async def get_all_portfolios(ctx: Context) -> Dict[str, dict]:
    """Fetch all portfolios"""
    keys = ctx.storage.get("portfolio_keys") or []
    portfolios = {}
    for key in keys:
        value = ctx.storage.get(key)
        if value:
            portfolios[key] = value
    return portfolios


@portfolio_agent.on_message(model=Portfolio)
async def register_portfolio(ctx: Context, sender: str, msg: Portfolio):
    """Register a new portfolio for monitoring"""
    ctx.logger.info(f"📝 Registering portfolio for user: {msg.user_id}")

    ctx.storage.set(f"portfolio_{msg.user_id}", {
        "wallets": msg.wallets,
        "chains": msg.chains,
        "registered_at": msg.timestamp,
        "owner": sender
    })

    await ctx.send(sender, MessageResponse(message=f"Portfolio registered for {msg.user_id}"))
    await scan_portfolio(ctx, msg.user_id)


async def scan_portfolio(ctx: Context, user_id: str):
    """Scan portfolio and create snapshot"""
    portfolio = ctx.storage.get(f"portfolio_{user_id}")
    if not portfolio:
        ctx.logger.warning(f"Portfolio {user_id} not found")
        return

    all_assets = []
    total_value = 0

    for wallet in portfolio["wallets"]:
        for chain in portfolio["chains"]:
            try:
                balances = await get_wallet_balance(wallet, chain)
                all_assets.extend(balances)
                total_value += sum(b["value_usd"] for b in balances)
            except Exception as e:
                ctx.logger.error(f"Error scanning {wallet} on {chain}: {e}")

    risk_score = calculate_risk_score(all_assets)

    snapshot = {
        "user_id": user_id,
        "total_value_usd": total_value,
        "assets": all_assets,
        "timestamp": datetime.now(timezone.utc),
        "risk_score": risk_score
    }

    user_snapshots = ctx.storage.get(f"snapshots_{user_id}") or []
    user_snapshots.append(snapshot)
    ctx.storage.set(f"snapshots_{user_id}", user_snapshots)

    ctx.logger.info(
        f"📊 Portfolio snapshot created: "
        f"${total_value:.2f}, Risk: {risk_score:.2%}"
    )

    risk_agent_address = "agent1qwwc3jwx0x6z0sk07029n9ngztsrapcc0ngdwy8swzq50tt7t0nf726tmkm"
    if risk_agent_address:
        await ctx.send(risk_agent_address, snapshot)  # type: ignore[arg-type]

    return snapshot


@portfolio_agent.on_interval(period=300.0)  # Every 5 minutes
async def monitor_portfolios(ctx: Context):
    """Periodically scan all registered portfolios"""
    portfolios = await get_all_portfolios(ctx)

    if not portfolios:
        return

    ctx.logger.info(f"🔄 Monitoring {len(portfolios)} portfolio(s)...")

    for key, _ in portfolios.items():
        user_id = key.replace("portfolio_", "")
        try:
            await scan_portfolio(ctx, user_id)
            await asyncio.sleep(2)
        except Exception as e:
            ctx.logger.error(f"Error monitoring {user_id}: {e}")


@portfolio_agent.on_event("startup")
async def startup(ctx: Context):
    portfolios = await get_all_portfolios(ctx)
    ctx.logger.info("=" * 60)
    ctx.logger.info("🛡️  DeFiGuard Portfolio Monitor Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {portfolio_agent.address}")
    ctx.logger.info(f"Loaded {len(portfolios)} portfolios from storage")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    portfolio_agent.run()
