# 🛡️ DeFiGuard Portfolio Monitor

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

## 📊 Overview

The **Portfolio Monitor Agent** is the core data collection component of the DeFiGuard multi-agent risk management system. It continuously monitors DeFi portfolios across multiple blockchain networks, tracking wallet balances, token prices, and portfolio composition in real-time.

---

## 🎯 Agent Details

- **Agent Name**: `portfolio_monitor`
- **Agent Address**: `agent1qt2fhu92p6uq3yq692drxrnx74yh7jqs0vjm65st3tz6wej6rxf7qehenpc`
- **Network**: Fetch.ai Testnet (Agentverse) 
- **Status**: ✅ Active  

---

## 🔧 Capabilities

### Core Functions
- ✅ **Multi-chain Portfolio Tracking** - Monitors wallets on Ethereum, Polygon, and BSC
- ✅ **Real-time Balance Updates** - Scans portfolio every 5 minutes
- ✅ **Automated Price Fetching** - Integrates with CoinGecko API for live token prices
- ✅ **Risk Score Calculation** - Computes concentration and volatility metrics
- ✅ **Portfolio Snapshots** - Creates historical records of portfolio state

### Supported Chains
- Ethereum Mainnet
- Binance Smart Chain (BSC)
- Polygon PoS
- *(Coming Soon: Arbitrum & Optimism)*  

---

## 📡 Message Protocol

### ➡️ Input: Portfolio Registration

Send a `Portfolio` message to register a new portfolio for monitoring:

```json
{
  "user_id": "user_wallet_address_or_id",
  "wallets": [
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "0xYourSecondWallet..."
  ],
  "chains": ["ethereum", "polygon", "bsc"],
  "timestamp": "2025-10-12T10:30:00Z"
}
```

### ⬅️ Output: Portfolio Snapshot

Automatically sends snapshots to Risk Analysis Agent:

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
  "timestamp": "2025-10-12T10:35:00Z",
  "risk_score": 0.35
}
```

---

## 🔄 Agent Workflow

```
1. User Registers Portfolio
         ↓
2. Agent Scans Wallets
         ↓
3. Fetches Token Prices (CoinGecko)
         ↓
4. Calculates Portfolio Value
         ↓
5. Computes Risk Score
         ↓
6. Creates Snapshot
         ↓
7. Sends to Risk Analysis Agent
         ↓
8. Repeats Every 5 Minutes
```

---

## 🧮 Risk Scoring Algorithm

The agent calculates a basic risk score (0-1) based on:

**Concentration Risk (40% weight)**
- Uses `Herfindahl-Hirschman` Index (HHI)
- Higher concentration = Higher risk

**Volatility Risk (60% weight)**
- Based on 24-hour price changes
- Normalized to 0-1 scale

**Formula:**
```
risk_score = (HHI × 0.4) + (avg_volatility/20 × 0.6)
```

---

## 🔗 Agent Communication

### ➡️ Sends Messages To:
- **Risk Analysis Agent** (`agent1qwwc3jwx0x6z0sk07029n9ngztsrapcc0ngdwy8swzq50tt7t0nf726tmkm`) - Portfolio snapshots for risk assessment

### ⬅️ Receives Messages From:
- **End Users** - Portfolio registration requests
- **Other Agents** - Query requests for portfolio data

---

## ⚙️ Configuration

### API Integration
- **CoinGecko API**: Real-time token price data
- **Rate Limiting**: 1.5 seconds between requests
- **Timeout**: 10 seconds per API call

### Monitoring Interval
- **Default**: 300 seconds (5 minutes)
- **Adjustable**: Can be configured per deployment


---

## 📦 Data Storage

**Storage Type**: In-memory (demo)

**Stored Data:**
- Portfolio registrations
- Historical snapshots (last 100)
- User-agent mappings

**Production Note**: For production deployment, migrate to persistent storage (PostgreSQL, MongoDB, or Agentverse Storage API).

---

## 🚀 Usage Example

### Register a Portfolio

```python
from uagents import Agent, Context, Model
from datetime import datetime

# Create client agent
client = Agent(name="portfolio_client", mailbox=True)

# Define Portfolio model
class Portfolio(Model):
    user_id: str
    wallets: list[str]
    chains: list[str]
    timestamp: str

# Send registration
@client.on_event("startup")
async def register_portfolio(ctx: Context):
    portfolio = Portfolio(
        user_id="0xYourWalletAddress",
        wallets=["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"],
        chains=["ethereum", "polygon"],
        timestamp=datetime.utcnow().isoformat()
    )
    
    await ctx.send(
        "agent1qt2fhu92p6uq3yq692drxrnx74yh7jqs0vjm65st3tz6wej6rxf7qehenpc",
        portfolio
    )

if __name__ == "__main__":
    client.run()
```

---

## 🔍 Monitoring & Logs

### Key Log Messages
- `📝 Registering portfolio for user: {user_id}` - New portfolio added
- `📊 Portfolio snapshot created: ${value}, Risk: {score}%` - Snapshot generated
- `🔄 Monitoring {count} portfolio(s)...` - Periodic scan initiated

### Error Handling
- API failures gracefully handled with retries
- Invalid wallet addresses logged and skipped
- Network errors reported without stopping monitoring

---

## 🛠️ Technical Stack

- **Framework**: Fetch.ai uAgents `v0.12.0`
- **Language**: Python 3.12
- **Networking**: aiohttp (async I/O)
- **Blockchain**: Web3.py
- **APIs**: CoinGecko v3
- **Async**: aiohttp for concurrent requests
- **Deployment**: Agentverse Cloud Platform

---

## 🔐 Security Features

- ✅ **No Private Keys** - Only monitors public wallet addresses
- ✅ **Read-Only** - Cannot execute transactions
- ✅ **Rate Limited** - Respects API quotas
- ✅ **Error Isolation** - Individual failures don't crash system


---

## 📈 Performance Metrics

- **Response Time**: < 2 seconds per wallet scan
- **Throughput**: Monitors up to 100 portfolios concurrently
- **Uptime**: 99.9% on Agentverse infrastructure
- **API Calls**: ~20 per portfolio per scan

---

## 🤝 Integration with DeFiGuard Ecosystem

This agent is part of the **DeFiGuard Multi-Agent System**:

> 1. **Portfolio Monitor**  ← Current Agent
2. **Risk Analysis** - Receives snapshots
3. **Alert Agent** - Notified of high-risk portfolios
4. **Market Data** - Provides price feeds
5. **Fraud Detection** - Validates token safety

## 📞 Support & Contact

- **GitHub**: [DeFiGuard Repository](https://github.com/DhanteyUD/DeFiGuard)

## 📄 License

MIT License - Open Source

---

**Powered by ASI Alliance** | **Built with Fetch.ai uAgents** | **Deployed on Agentverse**