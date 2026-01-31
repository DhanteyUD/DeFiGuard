from uagents import Agent, Context, Model
from datetime import datetime, timezone
from typing import Dict, List, Optional
import aiohttp
import asyncio
import inspect
from typing import Any
import os
from dotenv import load_dotenv

load_dotenv()


class MarketDataRequest(Model):
    token_ids: List[str]
    request_type: str  # "price", "volume", "market_cap", "all"


class MarketDataResponse(Model):
    data: Dict
    timestamp: str


class MarketAlert(Model):
    alert_type: str
    token: str
    message: str
    severity: str
    chain: str


class ErrorResponse(Model):
    error: str


market_agent_av = Agent(
    name="market_data",
    mailbox=True
)

print(f"Market Data Agent Address: {market_agent_av.address}")

_memory_store = {
    "market_cache": {},
    "last_prices": {}
}

SOLANA_TOKEN_IDS = {
    # Native
    "solana": "solana",
    "sol": "solana",

    # Major DeFi
    "raydium": "raydium",
    "ray": "raydium",
    "orca": "orca",
    "jupiter": "jupiter-exchange-solana",
    "jup": "jupiter-exchange-solana",
    "marinade": "marinade",
    "mnde": "marinade",
    "jito": "jito-governance-token",
    "pyth": "pyth-network",

    # Liquid Staking
    "msol": "msol",
    "jitosol": "jito-staked-sol",

    # Stablecoins (Solana versions)
    "usdc-solana": "usd-coin",
    "usdt-solana": "tether",

    # Meme Coins
    "bonk": "bonk",
    "wif": "dogwifcoin",
    "dogwifhat": "dogwifcoin",
    "popcat": "popcat",
    "myro": "myro",
    "wen": "wen-4",
    "slerf": "slerf",
    "bome": "book-of-meme",
}

# EVM Token mappings
EVM_TOKEN_IDS = {
    # Major tokens
    "ethereum": "ethereum",
    "eth": "ethereum",
    "bitcoin": "bitcoin",
    "btc": "bitcoin",
    "bnb": "binancecoin",
    "matic": "matic-network",
    "polygon": "matic-network",
    "arbitrum": "arbitrum",
    "arb": "arbitrum",
    "optimism": "optimism",
    "op": "optimism",
    "avalanche": "avalanche-2",
    "avax": "avalanche-2",

    # Stablecoins
    "usdc": "usd-coin",
    "usdt": "tether",
    "dai": "dai",
    "busd": "binance-usd",

    # DeFi
    "uniswap": "uniswap",
    "uni": "uniswap",
    "aave": "aave",
    "compound": "compound-governance-token",
    "comp": "compound-governance-token",
    "curve": "curve-dao-token",
    "crv": "curve-dao-token",
    "maker": "maker",
    "mkr": "maker",
    "lido": "lido-dao",
    "ldo": "lido-dao",
}

# Combined token ID resolver
ALL_TOKEN_IDS = {**EVM_TOKEN_IDS, **SOLANA_TOKEN_IDS}


def resolve_token_id(token: str) -> str:
    token_lower = token.lower().strip()
    return ALL_TOKEN_IDS.get(token_lower, token_lower)


def get_token_chain(token_id: str) -> str:
    if token_id in SOLANA_TOKEN_IDS or token_id in SOLANA_TOKEN_IDS.values():
        return "solana"
    return "evm"


async def _maybe_await(value):
    if inspect.isawaitable(value):
        return await value
    return value


async def safe_get(ctx, key: str) -> Any:
    storage = getattr(ctx, "storage", None)
    if storage is not None:
        try:
            value = await _maybe_await(storage.get(key))
            if value is not None:
                return value
        except (AttributeError, TypeError) as e:
            ctx.logger.warning(f"⚠️ Storage get failed ({key}): {e}")
        except asyncio.CancelledError:
            raise
    return _memory_store.get(key, {})


async def safe_set(ctx, key: str, value: Any):
    storage = getattr(ctx, "storage", None)
    if storage is not None:
        try:
            result = storage.set(key, value)
            if inspect.isawaitable(result):
                await result
            return
        except (AttributeError, TypeError) as e:
            ctx.logger.warning(f"⚠️ Storage set failed ({key}): {e}")
        except asyncio.CancelledError:
            raise

    _memory_store[key] = value
    ctx.logger.debug(f"💾 Stored {key} in memory fallback")


COINGECKO_API = "https://api.coingecko.com/api/v3"


async def fetch_token_data(token_id: str) -> Dict:
    resolved_id = resolve_token_id(token_id)

    url = f"{COINGECKO_API}/coins/{resolved_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    market_data = data.get("market_data", {})

                    platforms = data.get("platforms", {})
                    chain = "solana" if "solana" in platforms else "evm"

                    return {
                        "id": resolved_id,
                        "original_id": token_id,
                        "symbol": data.get("symbol", "").upper(),
                        "name": data.get("name", ""),
                        "chain": chain,
                        "current_price": market_data.get("current_price", {}).get("usd", 0),
                        "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                        "total_volume": market_data.get("total_volume", {}).get("usd", 0),
                        "price_change_24h": market_data.get("price_change_percentage_24h", 0),
                        "price_change_7d": market_data.get("price_change_percentage_7d", 0),
                        "price_change_30d": market_data.get("price_change_percentage_30d", 0),
                        "ath": market_data.get("ath", {}).get("usd", 0),
                        "atl": market_data.get("atl", {}).get("usd", 0),
                        "circulating_supply": market_data.get("circulating_supply", 0),
                        "total_supply": market_data.get("total_supply", 0),
                    }
                elif response.status == 404:
                    return {"id": token_id, "error": f"Token '{token_id}' not found on CoinGecko"}
                else:
                    return {"id": token_id, "error": f"API returned {response.status}"}
    except asyncio.TimeoutError:
        return {"id": token_id, "error": "Request timeout"}
    except Exception as e:
        return {"id": token_id, "error": str(e)}


async def fetch_multiple_prices(token_ids: List[str]) -> Dict:
    resolved_ids = [resolve_token_id(tid) for tid in token_ids]

    url = f"{COINGECKO_API}/simple/price"
    params = {
        "ids": ",".join(resolved_ids),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()

                    result = {}
                    for orig_id, resolved_id in zip(token_ids, resolved_ids):
                        if resolved_id in data:
                            result[orig_id] = data[resolved_id]
                            result[orig_id]["chain"] = get_token_chain(resolved_id)

                    return result
                return {}
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {}


def detect_significant_change(
        token: str,
        current_price: float,
        last_prices: Dict,
        threshold: float = 10.0,
        chain: str = "evm"
) -> Optional[MarketAlert]:
    if token in last_prices and current_price > 0:
        previous_price = last_prices[token]
        if previous_price > 0:
            change_percent = ((current_price - previous_price) / previous_price) * 100

            if abs(change_percent) >= threshold:
                severity = "high" if abs(change_percent) >= 20 else "medium"
                direction = "increased" if change_percent > 0 else "decreased"

                chain_emoji = "◎" if chain == "solana" else "⟠"

                return MarketAlert(
                    alert_type="significant_price_change",
                    token=token,
                    message=f"{chain_emoji} {token} price {direction} by {abs(change_percent):.2f}%",
                    severity=severity,
                    chain=chain
                )

    last_prices[token] = current_price
    return None


def detect_volume_spike(token_data: Dict) -> Optional[MarketAlert]:
    if "total_volume" in token_data and "market_cap" in token_data:
        volume = token_data["total_volume"]
        market_cap = token_data["market_cap"]
        chain = token_data.get("chain", "evm")

        if market_cap > 0:
            volume_ratio = volume / market_cap

            # Solana meme coins often have higher volume ratios
            threshold = 0.7 if chain == "solana" else 0.5

            if volume_ratio > threshold:
                chain_emoji = "◎" if chain == "solana" else "⟠"

                return MarketAlert(
                    alert_type="volume_spike",
                    token=token_data.get("symbol", token_data["id"]),
                    message=f"{chain_emoji} Unusual volume spike: {volume_ratio:.1%} of market cap",
                    severity="medium",
                    chain=chain
                )

    return None


def detect_solana_meme_volatility(token_data: Dict) -> Optional[MarketAlert]:
    chain = token_data.get("chain", "evm")
    if chain != "solana":
        return None

    symbol = token_data.get("symbol", "").upper()
    price_change_24h = token_data.get("price_change_24h", 0)

    # Known Solana meme coins
    meme_coins = {"BONK", "WIF", "POPCAT", "MYRO", "WEN", "SLERF", "BOME"}

    if symbol in meme_coins and abs(price_change_24h) > 30:
        direction = "pumped" if price_change_24h > 0 else "dumped"
        severity = "high" if abs(price_change_24h) > 50 else "medium"

        return MarketAlert(
            alert_type="meme_coin_volatility",
            token=symbol,
            message=f"◎ Solana meme coin {symbol} {direction} {abs(price_change_24h):.1f}% in 24h",
            severity=severity,
            chain="solana"
        )

    return None


@market_agent_av.on_message(model=MarketDataRequest)
async def handle_market_request(ctx: Context, sender: str, msg: MarketDataRequest):
    ctx.logger.info(f"📊 Received request for {len(msg.token_ids)} tokens")

    try:
        market_cache = await safe_get(ctx, "market_cache")
        last_prices = await safe_get(ctx, "last_prices")

        if msg.request_type == "price":
            data = await fetch_multiple_prices(msg.token_ids)
        else:
            data = {}
            for token_id in msg.token_ids:
                token_data = await fetch_token_data(token_id)
                data[token_id] = token_data

                ALERT_AGENT_ADDRESS = "agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun"

                if "current_price" in token_data and "error" not in token_data:
                    chain = token_data.get("chain", "evm")

                    alert = detect_significant_change(
                        token_id,
                        token_data["current_price"],
                        last_prices,
                        chain=chain
                    )
                    if alert:
                        ctx.logger.warning(f"⚠️ Alert: {alert.message}")
                        await ctx.send(ALERT_AGENT_ADDRESS, alert)

                    # Volume spike alert
                    volume_alert = detect_volume_spike(token_data)
                    if volume_alert:
                        ctx.logger.warning(f"⚠️ Alert: {volume_alert.message}")
                        await ctx.send(ALERT_AGENT_ADDRESS, volume_alert)

                    # NEW: Solana meme coin volatility alert
                    meme_alert = detect_solana_meme_volatility(token_data)
                    if meme_alert:
                        ctx.logger.warning(f"⚠️ Alert: {meme_alert.message}")
                        await ctx.send(ALERT_AGENT_ADDRESS, meme_alert)

                await asyncio.sleep(1.5)

        market_cache.update(data)
        await safe_set(ctx, "market_cache", market_cache)
        await safe_set(ctx, "last_prices", last_prices)

        # Send response
        response = MarketDataResponse(
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        ctx.logger.info(f"✅ Market data sent for {len(data)} tokens")
        await ctx.send(sender, response)

    except Exception as e:
        ctx.logger.error(f"❌ Error fetching market data: {e}")
        await ctx.send(sender, ErrorResponse(error=str(e)))


@market_agent_av.on_interval(period=300.0)  # Every 5 minutes
async def update_market_data(ctx: Context):
    market_cache = await safe_get(ctx, "market_cache")
    last_prices = await safe_get(ctx, "last_prices")

    if not market_cache:
        return

    ctx.logger.info(f"🔄 Updating market data for {len(market_cache)} tokens")

    token_ids = list(market_cache.keys())
    updated_data = await fetch_multiple_prices(token_ids)

    for token_id, data in updated_data.items():
        if "usd" in data:
            chain = data.get("chain", get_token_chain(token_id))

            alert = detect_significant_change(
                token_id,
                data["usd"],
                last_prices,
                threshold=5.0,
                chain=chain
            )
            if alert:
                ctx.logger.warning(f"📈 Market alert: {alert.message}")

                ALERT_AGENT_ADDRESS = "agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun"
                await ctx.send(ALERT_AGENT_ADDRESS, alert)

    await safe_set(ctx, "market_cache", market_cache)
    await safe_set(ctx, "last_prices", last_prices)


@market_agent_av.on_event("startup")
async def startup(ctx: Context):
    solana_tokens = len(SOLANA_TOKEN_IDS) // 2
    evm_tokens = len(EVM_TOKEN_IDS) // 2

    ctx.logger.info("=" * 60)
    ctx.logger.info("📊 DeFiGuard Market Data Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {market_agent_av.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("🔗 Connected to CoinGecko API")
    ctx.logger.info(f"◎  Solana tokens mapped: ~{solana_tokens}")
    ctx.logger.info(f"⟠  EVM tokens mapped: ~{evm_tokens}")
    ctx.logger.info("🚨 Alerts: Price change, Volume spike, Meme volatility")
    ctx.logger.info("=" * 60)

    await safe_set(ctx, "market_cache", await safe_get(ctx, "market_cache"))
    await safe_set(ctx, "last_prices", await safe_get(ctx, "last_prices"))


if __name__ == "__main__":
    market_agent_av.run()
