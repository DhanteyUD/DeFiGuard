# 📊 DeFiGuard Market Data Agent

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
![tag:solana](https://img.shields.io/badge/solana-9945FF)

## 📊 Overview

The **Market Data Agent** is DeFiGuard's real-time market intelligence provider. It aggregates cryptocurrency price data, volume metrics, and market indicators from trusted sources, enabling other agents to make informed decisions with up-to-date market context.

**Now with full Solana token support!** ◎

---

## 🎯 Agent Details

- **Agent Name**: `market_data`
- **Agent Address**: `agent1qgwdvuucfhpvucqdru0gnrwc2zqf0ak5u24rvxua9flcazctmdvdsyrr8qq`
- **Network**: Fetch.ai Mainnet (Agentverse)
- **Data Sources**: CoinGecko API v3, Jupiter API (Solana)
- **Update Frequency**: Every 5 minutes
- **Version**: 2.0.0-solana
- **Status**: ✅ Active

---

## 🔧 Capabilities

### Real-Time Market Data
- ✅ **Live Price Feeds** - Current USD prices for 10,000+ tokens
- ✅ **Solana Token Prices** - SPL tokens via Jupiter/CoinGecko ◎
- ✅ **Volume Tracking** - 24-hour trading volume monitoring
- ✅ **Market Cap Data** - Total and circulating market capitalization
- ✅ **Price Change Analysis** - 24h, 7d, and 30d percentage changes
- ✅ **Historical Extremes** - All-time high (ATH) and all-time low (ATL)

### Solana-Specific Features (NEW) ◎
- ✅ **Meme Coin Tracking** - BONK, WIF, POPCAT, and more
- ✅ **LST Prices** - mSOL, jitoSOL, bSOL liquid staking tokens
- ✅ **DEX Volume** - Jupiter, Raydium, Orca trading volume
- ✅ **Meme Volatility Alerts** - Special thresholds for Solana meme coins

### Anomaly Detection
- ✅ **Significant Price Changes** - Alerts on >10% moves
- ✅ **Volume Spikes** - Detects unusual trading activity
- ✅ **Market Manipulation Warnings** - Identifies suspicious patterns
- ✅ **Pump & Dump Detection** - Flags coordinated price movements
- ✅ **Solana Meme Volatility** - Special alerts for meme coins ◎

### Data Types

**Quick Price Check:**
- Fast, lightweight price queries
- Multiple tokens in single request
- 24-hour change included

**Comprehensive Analysis:**
- Full market statistics
- Supply metrics
- Price history
- Market rankings

---

## 📡 Message Protocol

### ➡️ Input: Market Data Request

Request market data for specific tokens:

```json
{
  "token_ids": ["bitcoin", "ethereum", "solana", "bonk"],
  "request_type": "all",
  "chain": "mixed"
}
```

**Request Types:**
- `price` - Quick price check only
- `volume` - Trading volume data
- `market_cap` - Market capitalization
- `all` - Complete market data

**Chain Types (NEW):**
- `evm` - EVM chain tokens only
- `solana` - Solana tokens only
- `mixed` - All chains (default)

### ⬅️ Output: Market Data Response

Comprehensive market intelligence:

```json
{
  "data": {
    "bitcoin": {
      "id": "bitcoin",
      "symbol": "BTC",
      "name": "Bitcoin",
      "chain": "evm",
      "current_price": 45000.00,
      "market_cap": 850000000000,
      "total_volume": 25000000000,
      "price_change_24h": 3.5,
      "price_change_7d": -2.1,
      "price_change_30d": 12.8,
      "ath": 69000.00,
      "atl": 67.81,
      "circulating_supply": 19500000,
      "total_supply": 21000000
    },
    "solana": {
      "id": "solana",
      "symbol": "SOL",
      "name": "Solana",
      "chain": "solana",
      "current_price": 145.00,
      "market_cap": 62000000000,
      "total_volume": 2500000000,
      "price_change_24h": 5.2,
      "price_change_7d": 12.3,
      "price_change_30d": 28.5,
      "ath": 260.00,
      "atl": 0.50,
      "circulating_supply": 430000000,
      "total_supply": 570000000
    },
    "bonk": {
      "id": "bonk",
      "symbol": "BONK",
      "name": "Bonk",
      "chain": "solana",
      "current_price": 0.00002345,
      "market_cap": 1500000000,
      "total_volume": 450000000,
      "price_change_24h": 25.5,
      "price_change_7d": -15.2,
      "price_change_30d": 85.0,
      "is_meme_coin": true,
      "volatility_warning": true
    }
  },
  "timestamp": "2025-10-12T10:40:00Z",
  "chains_included": ["evm", "solana"]
}
```

---

## 🚨 Market Alerts

### Alert Types

**1. Significant Price Change**
```json
{
  "alert_type": "significant_price_change",
  "token": "ethereum",
  "chain": "evm",
  "message": "ETH price increased by 15.3%",
  "severity": "high"
}
```

**2. Volume Spike**
```json
{
  "alert_type": "volume_spike",
  "token": "BTC",
  "chain": "evm",
  "message": "Unusual volume: 65% of market cap",
  "severity": "medium"
}
```

**3. Solana Meme Volatility (NEW) ◎**
```json
{
  "alert_type": "meme_volatility",
  "token": "BONK",
  "chain": "solana",
  "message": "◎ Solana meme coin BONK moved 45% in 24h",
  "severity": "high",
  "is_meme_coin": true
}
```

### Alert Thresholds

**Standard Price Changes:**
- Medium Alert: ≥10% change
- High Alert: ≥20% change

**Solana Meme Coin Price Changes (NEW):**
- Medium Alert: ≥30% change
- High Alert: ≥50% change
- Note: Higher thresholds due to expected meme volatility

**Volume Anomalies:**
- Medium Alert: Volume >50% of market cap
- High Alert: Volume >100% of market cap

---

## 🔄 Data Collection Workflow

```
1. Receive Data Request
         ↓
2. Parse Token IDs & Detect Chain Type
         ↓
3. Check Cache (5-min TTL)
         ↓
4a. Cache Hit?
    → Return Cached Data
         ↓
4b. Cache Miss?
    → Route to appropriate API:
      • EVM tokens → CoinGecko API
      • Solana tokens → Jupiter + CoinGecko
         ↓
5. Rate Limiting (1.5s delay)
         ↓
6. Detect Anomalies
   - Price changes
   - Volume spikes
   - Meme coin volatility ◎
         ↓
7. Generate Alerts
         ↓
8. Update Cache
         ↓
9. Send Response
         ↓
10. Notify Alert Agent (if needed)
```

---

## 🔗 Agent Communication

### Receives Requests From:
- **Portfolio Monitor Agent** - Token price queries (EVM + Solana)
- **Risk Analysis Agent** - Market context data
- **Fraud Detection Agent** - Token legitimacy checks
- **External Clients** - Direct data requests

### Sends Data/Alerts To:
- **Requesting Agent** - Market data response
- **Alert Agent** (`agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l`) - Market anomaly alerts

### Connected Agents:
| Agent             | Address                                                             | Purpose            |
|-------------------|---------------------------------------------------------------------|--------------------|
| Portfolio Monitor | `agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f` | Wallet scanning    |
| Risk Analysis     | `agent1qtrn82fz9tnspwudzrjr7mm9ncwvavjse5xcv7j9t06gajmdxq0yg38dyx5` | Risk calculation   |
| Alert Agent       | `agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l` | User notifications |
| Fraud Detection   | `agent1q0x3wcul6azlcu4wy5khce9hklav28ea9f8kjqcq649rs4jat5kc7zxarn6` | Token analysis     |

---

## 📊 Supported Tokens

### ◎ Solana Ecosystem (NEW)

**Native & Infrastructure:**
- Solana (SOL)
- Wrapped SOL (wSOL)

**Liquid Staking Tokens:**
- Marinade SOL (mSOL)
- Jito SOL (jitoSOL)
- BlazeStake SOL (bSOL)

**DeFi Tokens:**
- Raydium (RAY)
- Jupiter (JUP)
- Orca (ORCA)
- Marinade (MNDE)
- Jito (JTO)
- Pyth (PYTH)

**Meme Coins (High Volatility):**
- Bonk (BONK) ⚠️
- dogwifhat (WIF) ⚠️
- Popcat (POPCAT) ⚠️
- Myro (MYRO) ⚠️
- Wen (WEN) ⚠️
- Book of Meme (BOME) ⚠️

**Stablecoins:**
- USDC (Solana)
- USDT (Solana)

### ⟠ EVM Ecosystem

**Major Cryptocurrencies:**
- Bitcoin (BTC)
- Ethereum (ETH)
- Binance Coin (BNB)
- Cardano (ADA)
- Polkadot (DOT)
- ...and 10,000+ more

**Stablecoins:**
- USDC, USDT, DAI, BUSD
- Frax, UST, TUSD

**DeFi Tokens:**
- Uniswap, Aave, Compound
- Curve, Yearn, Synthetix
- PancakeSwap, SushiSwap

---

## 🗺️ Token ID Mapping

### Solana Token Mapping (NEW)

The agent automatically maps Solana token symbols to CoinGecko IDs:

```python
SOLANA_TOKEN_MAP = {
    # Native
    "sol": "solana",
    "solana": "solana",
    
    # Meme Coins
    "bonk": "bonk",
    "wif": "dogwifhat",
    "popcat": "popcat",
    "myro": "myro",
    "wen": "wen-4",
    "bome": "book-of-meme",
    "slerf": "slerf",
    
    # DeFi
    "ray": "raydium",
    "jup": "jupiter-exchange-solana",
    "orca": "orca",
    "mnde": "marinade",
    "jto": "jito-governance-token",
    "pyth": "pyth-network",
    
    # LSTs
    "msol": "marinade-staked-sol",
    "jitosol": "jito-staked-sol",
    "bsol": "blazestake-staked-sol",
    
    # Stablecoins
    "usdc-sol": "usd-coin",
    "usdt-sol": "tether",
}
```

---

## 🚀 Usage Example

### Request Quick Prices (Multi-chain)

```python
from uagents import Agent, Context, Model

class MarketDataRequest(Model):
    token_ids: list[str]
    request_type: str
    chain: str = "mixed"

client = Agent(name="market_client", mailbox=True)

@client.on_event("startup")
async def get_prices(ctx: Context):
    # Request both EVM and Solana tokens
    request = MarketDataRequest(
        token_ids=["bitcoin", "ethereum", "solana", "bonk", "jup"],
        request_type="price",
        chain="mixed"
    )
    
    await ctx.send(
        "agent1qgwdvuucfhpvucqdru0gnrwc2zqf0ak5u24rvxua9flcazctmdvdsyrr8qq",
        request
    )

@client.on_message(model=MarketDataResponse)
async def handle_response(ctx: Context, sender: str, msg: MarketDataResponse):
    ctx.logger.info(f"Received market data: {msg.data}")
    
    # Check for Solana meme coin alerts
    for token, data in msg.data.items():
        if data.get("is_meme_coin") and data.get("volatility_warning"):
            ctx.logger.warning(f"◎ Meme coin alert: {token}")

if __name__ == "__main__":
    client.run()
```

### Request Solana-Only Data

```python
request = MarketDataRequest(
    token_ids=["solana", "bonk", "wif", "jup", "ray"],
    request_type="all",
    chain="solana"
)
```

### Request Comprehensive Data

```python
request = MarketDataRequest(
    token_ids=["bitcoin", "ethereum", "solana"],
    request_type="all"
)
```

---

## 📈 Data Quality & Reliability

### API Integration

| Source           | Coverage          | Use Case               |
|------------------|-------------------|------------------------|
| CoinGecko API v3 | 10,000+ tokens    | Primary price source   |
| Jupiter API      | Solana DEX prices | Real-time Solana swaps |
| Raydium API      | Solana LP data    | Liquidity information  |

### Caching Strategy
- **Cache Duration**: 5 minutes
- **Cache Invalidation**: Time-based
- **Solana Meme Coins**: 2-minute cache (faster updates)
- **Benefits**: Reduced API calls, faster responses
- **Trade-off**: Slight data staleness acceptable

### Error Handling
- Automatic retry on failure (max 3 attempts)
- Graceful degradation on API errors
- Cached data served during outages
- Fallback to secondary API for Solana tokens
- Detailed error logging

---

## 🔍 Monitoring & Logs

### Key Log Messages
- `📊 Received request for {count} tokens` - Request received
- `◎ Solana tokens detected: {tokens}` - Solana routing
- `✅ Market data sent for {count} tokens` - Response sent
- `⚠️ Alert: {message}` - Anomaly detected
- `◎ Meme volatility: {token} {change}%` - Meme coin alert
- `🔄 Updating market data for {count} tokens` - Periodic update
- `❌ Error fetching market data` - API failure

### Performance Metrics
| Metric                    | Value       |
|---------------------------|-------------|
| Average response (cached) | < 1 second  |
| Average response (fresh)  | < 3 seconds |
| Solana token response     | < 2 seconds |
| Cache hit rate            | ~80%        |
| API success rate          | 99.5%       |

---

## 🛠️ Technical Stack

- **Framework**: Fetch.ai uAgents `v0.22.10`
- **HTTP Client**: aiohttp (async)
- **Data Sources**: 
  - CoinGecko API v3
  - Jupiter API (Solana) ◎
  - Raydium API (Solana) ◎
- **Caching**: In-memory dictionary
- **Rate Limiting**: Time-based delays
- **Concurrency**: Handles 50+ simultaneous requests

---

## 📊 Data Format Standards

### Token Identifier Format

**EVM Tokens (CoinGecko IDs):**
- ✅ Correct: `"bitcoin"`, `"ethereum"`, `"usd-coin"`
- ❌ Incorrect: `"BTC"`, `"ETH"`, `"USDC"` (these are symbols)

**Solana Tokens (NEW):**
- ✅ Correct: `"solana"`, `"bonk"`, `"wif"`, `"jup"`
- ✅ Also accepted: `"sol"`, `"dogwifhat"`, `"jupiter"`
- Auto-mapped to CoinGecko IDs internally

### Price Precision
- Prices: Up to 8 decimal places
- Meme coins: Up to 12 decimal places ◎
- Percentages: Up to 2 decimal places
- Market cap: Whole numbers (USD)

### Timestamp Format
- ISO 8601: `"2025-10-12T10:40:00Z"`
- Timezone: UTC

---

## 🎯 Use Cases

### Portfolio Valuation (Multi-chain)
Request prices for all tokens (EVM + Solana) to calculate total value.

### Risk Assessment
Detect high volatility periods by tracking 24h price changes.

### Solana Meme Coin Monitoring ◎
Track volatile meme coins with special alerting thresholds.

### Market Sentiment
Analyze volume spikes to identify market interest or manipulation.

### Token Screening
Check market cap and liquidity before investing.

### Alert Generation
Automatically notify users of significant market movements.

### Cross-Chain Analysis
Compare performance across Solana and EVM ecosystems.

---

## 🔐 Security & Rate Limits

### API Key Management
- **Demo**: Uses public CoinGecko API (no key required)
- **Production**: Upgrade to API key for higher limits
- **Key Storage**: Environment variables (not hardcoded)

### Rate Limiting

| API       | Free Tier     | Strategy   |
|-----------|---------------|------------|
| CoinGecko | 50 calls/min  | 1.5s delay |
| Jupiter   | 100 calls/min | 1s delay   |
| Raydium   | 60 calls/min  | 1.2s delay |

### Data Validation
- Response format validation
- Null value handling
- Type checking
- Error boundary protection
- Solana address format validation

---

## 📈 Performance Optimization

### Batch Requests
Request multiple tokens in single call:
```python
token_ids=["bitcoin", "ethereum", "solana", "bonk", "jup"]
```

Instead of individual requests:
```python
# ❌ Inefficient: 5 API calls
for token in ["bitcoin", "ethereum", "solana", "bonk", "jup"]:
    request = MarketDataRequest(token_ids=[token], ...)
```

### Chain-Specific Optimization
```python
# Request Solana tokens together for optimal routing
solana_request = MarketDataRequest(
    token_ids=["solana", "bonk", "wif", "jup"],
    chain="solana"
)
```

### Caching Best Practices
- Cache frequently requested tokens
- 5-minute TTL balances freshness vs load
- 2-minute TTL for meme coins (higher volatility)
- Automatic cache warming for popular tokens

---

## 🤝 Integration with DeFiGuard Ecosystem

This agent is part of the **DeFiGuard Multi-Agent System**:

1. **Portfolio Monitor** - Uses prices for valuation (EVM + Solana)
2. **Risk Analysis** - Uses volatility data + MeTTa reasoning
3. **Alert Agent** - Receives market alerts
> 4. **Market Data** ← You are here (Data provider)
5. **Fraud Detection** - Uses volume for analysis + RugCheck

**Chains Supported:** 13 total (◎ Solana + ⟠ 12 EVM)

---

## 🆕 What's New in v2.0.0-solana

- ◎ **Solana token support** - SOL, meme coins, DeFi tokens, LSTs
- ◎ **Jupiter API integration** - Real-time Solana DEX prices
- ◎ **Meme coin tracking** - BONK, WIF, POPCAT, and more
- ◎ **Meme volatility alerts** - Special thresholds (30%/50%)
- ◎ **Token ID mapping** - Auto-map Solana symbols to CoinGecko
- ◎ **Faster meme updates** - 2-minute cache for meme coins
- 🔗 **Chain parameter** - Filter by chain type
- 🔗 **Cross-chain batching** - Efficient multi-chain requests
- 📊 **Enhanced response** - Chain type in response data

---

## 📞 API Documentation

### CoinGecko API Reference
- **Docs**: https://www.coingecko.com/api/documentation
- **Status**: https://status.coingecko.com/
- **Support**: support@coingecko.com

### Jupiter API Reference ◎
- **Docs**: https://station.jup.ag/docs/apis/price-api
- **Status**: https://status.jup.ag/

### Rate Limit Information
| Tier       | CoinGecko | Jupiter |
|------------|-----------|---------|
| Free       | 50/min    | 100/min |
| Pro        | 500/min   | 500/min |
| Enterprise | Custom    | Custom  |

---

## 📞 Support & Contact

- **GitHub**: [DeFiGuard Repository](https://github.com/DhanteyUD/DeFiGuard)

## 📄 License

MIT License - Open Source

---

**Powered by ASI Alliance** | **Built with CoinGecko & Jupiter APIs** | **Real-Time Multi-Chain Market Intelligence**

*Updated: February 2026 | Version 2.0.0-solana*