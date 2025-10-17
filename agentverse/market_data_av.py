from uagents import Agent, Context, Model
from datetime import datetime, timezone
from typing import Dict, List, Optional
import aiohttp
import asyncio
import inspect
from typing import Any


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


class ErrorResponse(Model):
    error: str


market_agent = Agent(
    name="market_data",
    seed="pBli5u3yYGKKUCmY52CqWYrhAQtPDam_H7A_1KFKtow",
    port=8003,
    mailbox=True
)

print(f"Market Data Agent Address: {market_agent.address}")

_memory_store = {
    "market_cache": {},
    "last_prices": {}
}


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
    """Fetch comprehensive token data from CoinGecko"""
    url = f"{COINGECKO_API}/coins/{token_id}"
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

                    return {
                        "id": token_id,
                        "symbol": data.get("symbol", "").upper(),
                        "name": data.get("name", ""),
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
                else:
                    return {"id": token_id, "error": f"API returned {response.status}"}
    except Exception as e:
        return {"id": token_id, "error": str(e)}


async def fetch_multiple_prices(token_ids: List[str]) -> Dict:
    """Fetch prices for multiple tokens efficiently"""
    url = f"{COINGECKO_API}/simple/price"
    params = {
        "ids": ",".join(token_ids),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return {}


def detect_significant_change(token: str, current_price: float, last_prices: Dict, threshold: float = 10.0) -> Optional[
    MarketAlert]:
    """Detect significant price changes"""
    if token in last_prices and current_price > 0:
        previous_price = last_prices[token]
        if previous_price > 0:
            change_percent = ((current_price - previous_price) / previous_price) * 100

            if abs(change_percent) >= threshold:
                severity = "high" if abs(change_percent) >= 20 else "medium"
                direction = "increased" if change_percent > 0 else "decreased"

                return MarketAlert(
                    alert_type="significant_price_change",
                    token=token,
                    message=f"{token} price {direction} by {abs(change_percent):.2f}%",
                    severity=severity
                )

    # Update last price
    last_prices[token] = current_price
    return None


def detect_volume_spike(token_data: Dict) -> Optional[MarketAlert]:
    """Detect unusual volume spikes"""
    if "total_volume" in token_data and "market_cap" in token_data:
        volume = token_data["total_volume"]
        market_cap = token_data["market_cap"]

        if market_cap > 0:
            volume_ratio = volume / market_cap

            # Volume > 50% of market cap is unusual
            if volume_ratio > 0.5:
                return MarketAlert(
                    alert_type="volume_spike",
                    token=token_data.get("symbol", token_data["id"]),
                    message=f"Unusual volume spike: {volume_ratio:.1%} of market cap",
                    severity="medium"
                )

    return None


@market_agent.on_message(model=MarketDataRequest)
async def handle_market_request(ctx: Context, sender: str, msg: MarketDataRequest):
    """Handle market data requests"""
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

                alert_agent_address = "agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun"

                if "current_price" in token_data and "error" not in token_data:
                    alert = detect_significant_change(
                        token_id,
                        token_data["current_price"],
                        last_prices
                    )
                    if alert:
                        ctx.logger.warning(f"⚠️  Alert: {alert.message}")
                        await ctx.send(alert_agent_address, alert)

                    volume_alert = detect_volume_spike(token_data)
                    if volume_alert:
                        ctx.logger.warning(f"⚠️  Alert: {volume_alert.message}")
                        await ctx.send(alert_agent_address, volume_alert)

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


@market_agent.on_interval(period=300.0)  # Every 5 minutes
async def update_market_data(ctx: Context):
    """Periodically update market data for monitored tokens"""

    market_cache = await safe_get(ctx, "market_cache")
    last_prices = await safe_get(ctx, "last_prices")

    if not market_cache:
        return

    ctx.logger.info(f"🔄 Updating market data for {len(market_cache)} tokens")

    token_ids = list(market_cache.keys())
    updated_data = await fetch_multiple_prices(token_ids)

    # Check for significant changes
    for token_id, data in updated_data.items():
        if "usd" in data:
            alert = detect_significant_change(token_id, data["usd"], last_prices, threshold=5.0)
            if alert:
                ctx.logger.warning(f"📈 Market alert: {alert.message}")

                alert_agent_address = "agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun"
                await ctx.send(alert_agent_address, alert)

                await safe_set(ctx, "market_cache", market_cache)
                await safe_set(ctx, "last_prices", last_prices)


@market_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info("📊 DeFiGuard Market Data Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {market_agent.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("🔗 Connected to CoinGecko API")
    ctx.logger.info("=" * 60)

    await safe_set(ctx, "market_cache", await safe_get(ctx, "market_cache"))
    await safe_set(ctx, "last_prices", await safe_get(ctx, "last_prices"))


if __name__ == "__main__":
    market_agent.run()
