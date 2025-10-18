from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from datetime import datetime, timezone
from typing import List, Dict
from web3 import Web3
import aiohttp
import asyncio
import re
import os
from dotenv import load_dotenv

load_dotenv()


class Portfolio(Model):
    user_id: str
    wallets: List[str]
    chains: List[str]
    timestamp: str


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
    seed=os.getenv("PORTFOLIO_AGENT_SEED", "portfolio_agent_seed"),
    port=8000,
    endpoint="http://127.0.0.1:8000/submit",
    mailbox=True
)

fund_agent_if_low(str(portfolio_agent.wallet.address()))

print(f"Portfolio Monitor Agent Address: {portfolio_agent.address}")

CHAIN_CONFIG = {
    "ethereum": {
        "name": "Ethereum",
        "rpc": "https://eth.llamarpc.com",
        "native_token": "ethereum",
        "native_symbol": "ETH",
        "explorer": "https://etherscan.io"
    },
    "bsc": {
        "name": "BNB Smart Chain",
        "rpc": "https://bsc-dataseed.binance.org",
        "native_token": "binancecoin",
        "native_symbol": "BNB",
        "explorer": "https://bscscan.com"
    },
    "polygon": {
        "name": "Polygon",
        "rpc": "https://polygon-rpc.com",
        "native_token": "matic-network",
        "native_symbol": "MATIC",
        "explorer": "https://polygonscan.com"
    },
    "arbitrum": {
        "name": "Arbitrum",
        "rpc": "https://arb1.arbitrum.io/rpc",
        "native_token": "ethereum",
        "native_symbol": "ETH",
        "explorer": "https://arbiscan.io"
    },
    "optimism": {
        "name": "Optimism",
        "rpc": "https://mainnet.optimism.io",
        "native_token": "ethereum",
        "native_symbol": "ETH",
        "explorer": "https://optimistic.etherscan.io"
    },
    "avalanche": {
        "name": "Avalanche",
        "rpc": "https://api.avax.network/ext/bc/C/rpc",
        "native_token": "avalanche-2",
        "native_symbol": "AVAX",
        "explorer": "https://snowtrace.io"
    },
    "base": {
        "name": "Base",
        "rpc": "https://mainnet.base.org",
        "native_token": "ethereum",
        "native_symbol": "ETH",
        "explorer": "https://basescan.org"
    },
    "fantom": {
        "name": "Fantom",
        "rpc": "https://rpc.ftm.tools",
        "native_token": "fantom",
        "native_symbol": "FTM",
        "explorer": "https://ftmscan.com"
    },
    "gnosis": {
        "name": "Gnosis Chain",
        "rpc": "https://rpc.gnosischain.com",
        "native_token": "xdai",
        "native_symbol": "XDAI",
        "explorer": "https://gnosisscan.io"
    },
    "moonbeam": {
        "name": "Moonbeam",
        "rpc": "https://rpc.api.moonbeam.network",
        "native_token": "moonbeam",
        "native_symbol": "GLMR",
        "explorer": "https://moonscan.io"
    },
    "celo": {
        "name": "Celo",
        "rpc": "https://forno.celo.org",
        "native_token": "celo",
        "native_symbol": "CELO",
        "explorer": "https://celoscan.io"
    },
    "cronos": {
        "name": "Cronos",
        "rpc": "https://evm.cronos.org",
        "native_token": "crypto-com-chain",
        "native_symbol": "CRO",
        "explorer": "https://cronoscan.com"
    }
}

price_cache = {}
cache_timestamp = {}


def get_supported_chains() -> List[str]:
    return list(CHAIN_CONFIG.keys())


def validate_wallet_address(address: str) -> Dict:
    if not isinstance(address, str):
        return {"valid": False, "error": "Address must be a string"}

    address = address.strip()

    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return {"valid": False, "error": "Invalid EVM address format"}

    try:
        checksum_address = Web3.to_checksum_address(address)

        if checksum_address == "0x0000000000000000000000000000000000000000":
            return {"valid": False, "error": "Cannot use zero address"}

        return {"valid": True, "checksum": checksum_address, "error": None}
    except Exception as e:
        return {"valid": False, "error": f"Invalid address: {str(e)}"}


async def fetch_token_price_cached(token_id: str) -> Dict:
    current_time = datetime.now(timezone.utc).timestamp()

    if token_id in price_cache:
        cached_time = cache_timestamp.get(token_id, 0)
        if current_time - cached_time < 60:
            return price_cache[token_id]

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": token_id.lower(),
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    token_data = data.get(token_id.lower(), {})
                    result = {
                        "price": token_data.get("usd", 0),
                        "change_24h": token_data.get("usd_24h_change", 0),
                        "success": True
                    }

                    price_cache[token_id] = result
                    cache_timestamp[token_id] = current_time

                    return result
    except Exception as e:
        print(f"⚠️ Price fetch error: {e}")

    return {"price": 0, "change_24h": 0, "success": False}


async def get_wallet_balance_lightweight(ctx: Context, wallet: str, chain: str) -> List[Dict]:

    validation = validate_wallet_address(wallet)
    if not validation["valid"]:
        raise ValueError(f"Invalid wallet: {validation['error']}")

    wallet_checksum = validation["checksum"]
    chain_lower = chain.lower()

    if chain_lower not in CHAIN_CONFIG:
        raise ValueError(f"Unsupported chain: {chain}")

    config = CHAIN_CONFIG[chain_lower]

    try:
        web3 = Web3(Web3.HTTPProvider(
            config["rpc"],
            request_kwargs={'timeout': 5}
        ))

        native_balance_wei = web3.eth.get_balance(wallet_checksum)
        native_balance = float(web3.from_wei(native_balance_wei, "ether"))

        if native_balance < 0.0001:
            return []

        price_data = await fetch_token_price_cached(config["native_token"])

        enriched_balances = [{
            "token": config["native_symbol"],
            "balance": native_balance,
            "price": price_data["price"],
            "value_usd": native_balance * price_data["price"],
            "change_24h": price_data["change_24h"],
            "chain": chain_lower
        }]

        if enriched_balances[0]["value_usd"] > 0.01:
            ctx.logger.info(
                f"[{config['name']}] {config['native_symbol']}: "
                f"{native_balance:.4f} = ${enriched_balances[0]['value_usd']:.2f}"
            )

        return enriched_balances

    except Exception as e:
        ctx.logger.error(f"Error on {config['name']}: {str(e)[:100]}")
        return []


def calculate_risk_score(assets: List[Dict]) -> float:
    if not assets:
        return 0.0

    total_value = sum(a["value_usd"] for a in assets)
    if total_value == 0:
        return 0.0

    concentration = sum((a["value_usd"] / total_value) ** 2 for a in assets)

    # Volatility risk
    avg_volatility = sum(abs(a.get("change_24h", 0)) for a in assets) / len(assets)
    volatility_score = min(avg_volatility / 20, 1)

    unique_chains = len(set(a["chain"] for a in assets))
    chain_diversity_score = 1.0 if unique_chains == 1 else max(0.0, 1.0 - (unique_chains / 5.0))

    risk_score = (
            concentration * 0.35 +
            volatility_score * 0.45 +
            chain_diversity_score * 0.20
    )

    return min(risk_score, 1.0)


@portfolio_agent.on_message(model=Portfolio)
async def register_portfolio(ctx: Context, sender: str, msg: Portfolio):
    ctx.logger.info(f"📝 Registering portfolio for: {msg.user_id}")

    invalid_wallets = []
    valid_wallets = []

    for wallet in msg.wallets:
        validation = validate_wallet_address(wallet)
        if validation["valid"]:
            valid_wallets.append(validation["checksum"])
        else:
            invalid_wallets.append(f"{wallet}: {validation['error']}")

    if invalid_wallets:
        error_msg = "Invalid wallet(s): " + "; ".join(invalid_wallets)
        await ctx.send(sender, MessageResponse(message=error_msg))
        return

    invalid_chains = [c for c in msg.chains if c.lower() not in CHAIN_CONFIG]
    if invalid_chains:
        supported = ", ".join(get_supported_chains())
        error_msg = f"Unsupported chain(s): {', '.join(invalid_chains)}. Supported: {supported}"
        await ctx.send(sender, MessageResponse(message=error_msg))
        return

    if len(msg.chains) > 5:
        await ctx.send(
            sender,
            MessageResponse(message="⚠️ Max 5 chains on Agentverse. Please select your top chains.")
        )
        return

    portfolio_key = f"portfolio_{msg.user_id}"
    ctx.storage.set(portfolio_key, {
        "wallets": valid_wallets,
        "chains": [c.lower() for c in msg.chains],
        "registered_at": msg.timestamp,
        "owner": sender,
        "last_scan": None
    })

    keys = ctx.storage.get("portfolio_keys") or []
    if portfolio_key not in keys:
        keys.append(portfolio_key)
        ctx.storage.set("portfolio_keys", keys)

    await ctx.send(
        sender,
        MessageResponse(
            message=f"✅ Portfolio registered: {len(valid_wallets)} wallet(s), {len(msg.chains)} chain(s). Scanning starts next cycle."
        )
    )


async def scan_single_portfolio(ctx: Context, user_id: str):
    portfolio = ctx.storage.get(f"portfolio_{user_id}")
    if not portfolio:
        return None

    all_assets = []
    total_value = 0

    wallet = portfolio["wallets"][0]

    chains_to_scan = portfolio["chains"][:3]

    ctx.logger.info(f"🔍 Scanning {wallet[:10]}... on {len(chains_to_scan)} chain(s)")

    for chain in chains_to_scan:
        try:
            balances = await get_wallet_balance_lightweight(ctx, wallet, chain)
            all_assets.extend(balances)
            total_value += sum(b["value_usd"] for b in balances)

            await asyncio.sleep(0.5)

        except Exception as e:
            ctx.logger.error(f"Error on {chain}: {str(e)[:50]}")
            continue

    if not all_assets:
        ctx.logger.info(f"No assets found for {user_id}")
        return None

    risk_score = calculate_risk_score(all_assets)

    snapshot = PortfolioSnapshot(
        user_id=user_id,
        total_value_usd=total_value,
        assets=all_assets,
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=risk_score
    )

    snapshots = ctx.storage.get(f"snapshots_{user_id}") or []
    snapshots.append(snapshot.dict())
    ctx.storage.set(f"snapshots_{user_id}", snapshots[-5:])

    portfolio["last_scan"] = datetime.now(timezone.utc).isoformat()
    ctx.storage.set(f"portfolio_{user_id}", portfolio)

    ctx.logger.info(f"📊 ${total_value:.2f}, Risk: {risk_score:.2%}")

    if total_value > 1.0:
        RISK_AGENT_ADDRESS = "agent1q2stpgsyl2h5dlpq7sfk47hfnjqsw84kf6m40defdfph65ftje4e56l5a0f"
        await ctx.send(RISK_AGENT_ADDRESS, snapshot)

    return snapshot


@portfolio_agent.on_interval(period=600.0)
async def monitor_portfolios(ctx: Context):
    keys = ctx.storage.get("portfolio_keys") or []

    if not keys:
        return

    scan_index = ctx.storage.get("scan_index") or 0

    if scan_index >= len(keys):
        scan_index = 0

    if scan_index < len(keys):
        portfolio_key = keys[scan_index]
        user_id = portfolio_key.replace("portfolio_", "")

        ctx.logger.info(f"🔄 Scanning portfolio {scan_index + 1}/{len(keys)}: {user_id}")

        try:
            await scan_single_portfolio(ctx, user_id)
        except Exception as e:
            ctx.logger.error(f"Scan error for {user_id}: {str(e)[:100]}")

        scan_index += 1
        ctx.storage.set("scan_index", scan_index)

    ctx.logger.info(f"Next scan in 10 minutes (portfolio {scan_index % len(keys) + 1}/{len(keys)})")


@portfolio_agent.on_event("startup")
async def startup(ctx: Context):
    keys = ctx.storage.get("portfolio_keys") or []
    supported_chains = get_supported_chains()

    ctx.logger.info("=" * 60)
    ctx.logger.info("🛡️  DeFiGuard Portfolio Monitor (Agentverse)")
    ctx.logger.info(f"📍 Address: {portfolio_agent.address}")
    ctx.logger.info(f"📊 Portfolios: {len(keys)}")
    ctx.logger.info(f"🔗 Chains: {len(supported_chains)}")
    ctx.logger.info("⚡ Optimized for Agentverse limits")
    ctx.logger.info("🔄 Scans 1 portfolio per 10-min cycle")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    portfolio_agent.run()
