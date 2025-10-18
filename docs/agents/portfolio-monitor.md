# 🛡️ DeFiGuard Portfolio Monitor

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

## 📊 Overview

The **Portfolio Monitor Agent** is the core data collection component of the DeFiGuard multi-agent risk management system. It continuously monitors DeFi portfolios across multiple blockchain networks, tracking wallet balances, native token prices, and portfolio composition with optimized performance for Agentverse deployment.

---

## 🎯 Agent Details

- **Agent Name**: `portfolio_monitor`
- **Agent Address**: `agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f`
- **Network**: Fetch.ai Testnet (Agentverse) 
- **Status**: ✅ Active  
- **Scan Interval**: 600 seconds (10 minutes)
- **Optimization**: 1 portfolio per cycle, max 3 chains per scan

---

## 🔧 Capabilities

### Core Functions
- ✅ **Multi-chain Portfolio Tracking** - Monitors wallets on 12 EVM-compatible chains
- ✅ **Automated Price Fetching** - Integrates with CoinGecko API with 60-second caching
- ✅ **Risk Score Calculation** - Computes concentration, volatility, and chain diversity metrics
- ✅ **Portfolio Snapshots** - Stores last 5 historical records per portfolio
- ✅ **Wallet Validation** - ERC-55 checksum validation with zero-address protection
- ✅ **Lightweight Scanning** - Native token tracking only (optimized for Agentverse limits)

### Supported Chains
- Ethereum Mainnet
- BNB Smart Chain (BSC)
- Polygon PoS
- Arbitrum
- Optimism
- Avalanche
- Base
- Fantom
- Gnosis Chain
- Moonbeam
- Celo
- Cronos

---

## 📡 Message Protocol

### ➡️ Input: Portfolio Registration

Send a `Portfolio` message to register a new portfolio for monitoring:

```json
{
  "user_id": "user_wallet_address_or_id",
  "wallets": [
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
  ],
  "chains": ["ethereum", "polygon", "bsc"],
  "timestamp": "2025-10-15T10:30:00Z"
}
```

**Important Notes:**
- Maximum **5 chains** per portfolio (Agentverse limit)
- Only **first wallet** is scanned per cycle
- Wallets are validated with ERC-55 checksum
- Invalid chains/wallets return error via `MessageResponse`

### ⬅️ Output: Portfolio Snapshot

Automatically sends snapshots to Risk Analysis Agent (only if `total_value_usd > $1.00`):

```json
{
  "user_id": "user_wallet_address_or_id",
  "total_value_usd": 50000.00,
  "assets": [
    {
      "token": "ETH",
      "balance": 10.0,
      "value_usd": 20000.00,
      "price": 2000.00,
      "change_24h": 5.2,
      "chain": "ethereum"
    }
  ],
  "timestamp": "2025-10-15T10:35:00Z",
  "risk_score": 0.35
}
```

### ↖️ Registration Response

Immediate feedback via `MessageResponse`:

```json
{
  "message": "✅ Portfolio registered: 1 wallet(s), 3 chain(s). Scanning starts next cycle."
}
```

**Error Examples:**
```json
{
  "message": "Invalid wallet(s): 0xinvalid: Invalid EVM address format"
}
```
```json
{
  "message": "Unsupported chain(s): solana. Supported: ethereum, bsc, polygon..."
}
```

---

## 🔄 Agent Workflow

```
1. User Registers Portfolio
         ↓
2. Validation (Wallets + Chains)
         ↓
3. Storage in ctx.storage
         ↓
4. Wait for Next Scan Cycle (10 min)
         ↓
5. Scan 1 Portfolio (Round-Robin)
         ↓
6. Check First Wallet on Max 3 Chains
         ↓
7. Fetch Native Token Balances (Web3)
         ↓
8. Get Prices from CoinGecko (Cached)
         ↓
9. Filter Assets (min $0.01 value)
         ↓
10. Calculate Risk Score
         ↓
11. Create & Store Snapshot (Last 5)
         ↓
12. Send to Risk Agent (if value > $1)
         ↓
13. Repeat for Next Portfolio
```

---

## 🧮 Risk Scoring Algorithm

The agent calculates a composite risk score (0-1) based on three factors:

### **1. Concentration Risk (35% weight)**
- Uses Herfindahl-Hirschman Index (HHI)
- Formula: `Σ(asset_value/total_value)²`
- Higher concentration = Higher risk

### **2. Volatility Risk (45% weight)**
- Based on average 24-hour price changes
- Normalized: `min(avg_volatility / 20, 1)`
- Caps at 20% volatility for scaling

### **3. Chain Diversity Risk (20% weight)**
- Penalizes single-chain portfolios
- Formula: `1.0 if 1 chain else max(0, 1 - unique_chains/5)`

**Final Formula:**
```python
risk_score = (
    concentration * 0.35 +
    volatility_score * 0.45 +
    chain_diversity_score * 0.20
)
```

**Example:**
- 100% ETH on 1 chain = 0.55 risk
- Equal split across 3 chains = 0.28 risk

---

## 🔗 Agent Communication

### ➡️ Sends Messages To:
- **Risk Analysis Agent** (`agent1q2stpgsyl2h5dlpq7sfk47hfnjqsw84kf6m40defdfph65ftje4e56l5a0f`)
  - Portfolio snapshots with `total_value_usd > $1.00`
  - Sends `PortfolioSnapshot` model

### ⬅️ Receives Messages From:
- **End Users / Client Agents**
  - Portfolio registration via `Portfolio` model
  - Returns `MessageResponse` for confirmation/errors

---

## ⚙️ Configuration

### API Integration
- **CoinGecko API**: Free tier with 60-second price caching
- **Rate Limiting**: 0.5 seconds between chain scans
- **Timeout**: 5 seconds per Web3 call
- **RPC Providers**: Public endpoints (LlamaRPC, Binance, etc.)

### Monitoring Interval
- **Default**: 600 seconds (10 minutes per cycle)
- **Portfolios per Cycle**: 1 (round-robin rotation)
- **Chains per Scan**: Max 3 (first 3 from registered list)
- **Minimum Asset Value**: $0.01 USD

### Storage Limits
- **Snapshots per User**: Last 5 historical records
- **Storage Type**: `ctx.storage` (Agentverse persistent storage)
- **Keys Tracked**: `portfolio_{user_id}`, `snapshots_{user_id}`, `portfolio_keys`, `scan_index`

---

## 📦 Data Storage

**Storage Type**: Agentverse `ctx.storage` (persistent)

### Stored Data Structure:

**Portfolio Record:**
```python
{
  "wallets": ["0xChecksum..."],  # Validated checksums
  "chains": ["ethereum", "polygon"],
  "registered_at": "2025-10-15T...",
  "owner": "sender_address",
  "last_scan": "2025-10-15T..."  # ISO timestamp
}
```

**Snapshot Record:**
```python
{
  "user_id": "user_id",
  "total_value_usd": 50000.0,
  "assets": [...],  # List of asset dicts
  "timestamp": "2025-10-15T...",
  "risk_score": 0.35
}
```

**Global Keys:**
- `portfolio_keys`: List of all registered portfolio IDs
- `scan_index`: Current position in round-robin scan

---

## 🚀 Usage Example

### Register a Portfolio

```python
from uagents import Agent, Context, Model
from datetime import datetime, timezone

# Create client agent
client = Agent(name="portfolio_client", mailbox=True)

# Define models
class Portfolio(Model):
    user_id: str
    wallets: list[str]
    chains: list[str]
    timestamp: str

class MessageResponse(Model):
    message: str

PORTFOLIO_AGENT = "agent1qvyvw79t54ysq7rdp5xfc9qtqkycrnvtqlwjncrqfj3v8ne3dhzfvkjmdrn"

@client.on_event("startup")
async def register_portfolio(ctx: Context):
    portfolio = Portfolio(
        user_id="my_crypto_portfolio",
        wallets=["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"],
        chains=["ethereum", "polygon", "arbitrum"],  # Max 5
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    await ctx.send(PORTFOLIO_AGENT, portfolio)
    ctx.logger.info("✅ Portfolio registration sent!")

@client.on_message(model=MessageResponse)
async def handle_response(ctx: Context, sender: str, msg: MessageResponse):
    ctx.logger.info(f"Response: {msg.message}")

if __name__ == "__main__":
    client.run()
```

---

## 🔍 Monitoring & Logs

### Key Log Messages
- `📝 Registering portfolio for: {user_id}` - New portfolio validation
- `🔍 Scanning {wallet}... on {n} chain(s)` - Active scan
- `📊 ${value}, Risk: {score}%` - Snapshot created
- `🔄 Scanning portfolio {i}/{total}: {user_id}` - Cycle progress
- `Next scan in 10 minutes (portfolio {next}/{total})` - Queue status

### Error Handling
- Invalid wallets: Immediate rejection with error details
- RPC failures: Logged and skipped (doesn't crash agent)
- CoinGecko errors: Returns $0 price (logs warning)
- No assets found: Logs info but doesn't send to Risk Agent

---

## 🛠️ Technical Stack

- **Framework**: Fetch.ai uAgents `v0.12.0+`
- **Language**: Python 3.10+
- **Networking**: aiohttp (async HTTP)
- **Blockchain**: Web3.py `v7.13`
- **APIs**: CoinGecko API v3 (Free Tier)
- **Async**: asyncio for concurrent chain scans
- **Deployment**: Agentverse Cloud Platform
- **Storage**: Agentverse Context Storage

---

## 🔐 Security Features

- ✅ **No Private Keys** - Only monitors public addresses
- ✅ **Read-Only Operations** - Cannot execute transactions
- ✅ **Checksum Validation** - ERC-55 address verification
- ✅ **Zero Address Protection** - Rejects `0x0000...0000`
- ✅ **Rate Limited API** - Respects CoinGecko free tier
- ✅ **Error Isolation** - Wallet/chain failures don't cascade
- ✅ **Input Validation** - Regex + Web3 validation on all addresses

---

## 📈 Performance Metrics

- **Scan Time**: 2-5 seconds per portfolio (3 chains)
- **Concurrent Portfolios**: Unlimited registration, 1 scan per cycle
- **Cache Hit Rate**: ~90% (60-second price cache)
- **RPC Timeout**: 5 seconds per chain
- **Uptime**: 99.9% on Agentverse
- **API Calls**: 3-4 per scan (with caching)

### Agentverse Optimizations
- **Single Wallet Scanning**: Only first wallet per cycle
- **Chain Limit**: Max 3 chains per scan (from first 3 registered)
- **Minimum Threshold**: Skips assets < $0.01
- **Round-Robin**: Distributes load across portfolios
- **Snapshot Limit**: Stores only last 5 per user

---

## 🤝 Integration with DeFiGuard Ecosystem

This agent is part of the **DeFiGuard Multi-Agent System**:

> 1. **Portfolio Monitor** ← Current Agent (Data Collection)
2. **Risk Analysis** - Receives snapshots via `PortfolioSnapshot` messages
3. **Alert Agent** - Notified by Risk Agent on high-risk detection
4. **Market Data** - Provides price feeds
5. **Fraud Detection** - Validates token safety

---

## 🐛 Known Limitations

1. **Token Support**: Native tokens only (no ERC-20 tracking in current version)
2. **Wallet Limitation**: Scans only first wallet per portfolio
3. **Chain Limitation**: Max 3 chains per scan cycle
4. **Historical Data**: Only last 5 snapshots stored
5. **API Dependency**: Relies on CoinGecko free tier (rate limits apply)
6. **No Transaction History**: Balance-only monitoring

---

## 📞 Support & Contact

- **GitHub**: [DeFiGuard Repository](https://github.com/DhanteyUD/DeFiGuard)
- **Issues**: Report bugs via GitHub Issues

---

## 📄 License

MIT License - Open Source

---

**Powered by ASI Alliance** | **Built with Fetch.ai uAgents** | **Deployed on Agentverse**

*Last Updated: October 2025*