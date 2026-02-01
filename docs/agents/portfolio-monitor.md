# 🛡️ DeFiGuard Portfolio Monitor

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
![tag:solana](https://img.shields.io/badge/solana-9945FF)

## 📊 Overview

The **Portfolio Monitor Agent** is the core data collection component of the DeFiGuard multi-agent risk management
system. It continuously monitors DeFi portfolios across multiple blockchain networks, tracking wallet balances, native
token prices, and portfolio composition with optimized performance for Agentverse deployment.

**Now with full Solana blockchain support!** ◎

---

## 🎯 Agent Details

- **Agent Name**: `portfolio_monitor`
- **Agent Address**: `agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f`
- **Network**: Fetch.ai Mainnet (Agentverse)
- **Version**: 2.0.0-solana
- **Status**: ✅ Active
- **Scan Interval**: 600 seconds (10 minutes)
- **Optimization**: 1 portfolio per cycle, max 3 chains per scan

---

## 🔧 Capabilities

### Core Functions

- ✅ **Multi-chain Portfolio Tracking** - Monitors wallets on 13 chains (Solana + 12 EVM)
- ✅ **Solana SPL Token Support** - Full SPL token balance tracking ◎
- ✅ **Automated Price Fetching** - CoinGecko + Jupiter API with caching
- ✅ **Risk Score Calculation** - Concentration, volatility, and chain diversity metrics
- ✅ **Portfolio Snapshots** - Stores last 5 historical records per portfolio
- ✅ **Wallet Validation** - ERC-55 (EVM) + Base58 (Solana) validation
- ✅ **Lightweight Scanning** - Optimized for Agentverse limits

### Solana-Specific Features (NEW) ◎

- ✅ **SPL Token Balances** - Track all Solana token holdings
- ✅ **Mint Address Resolution** - Map mints to token symbols
- ✅ **Jupiter Price Integration** - Real-time Solana DEX prices
- ✅ **Meme Coin Detection** - Flag high-volatility meme tokens
- ✅ **LST Tracking** - mSOL, jitoSOL, bSOL liquid staking tokens

### Supported Chains (13 Total)

**◎ Solana Ecosystem (NEW)**

- Solana Mainnet

**⟠ EVM Chains (12)**

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

**EVM Portfolio:**

```json
{
  "user_id": "user_wallet_address_or_id",
  "wallets": [
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
  ],
  "chains": [
    "ethereum",
    "polygon",
    "bsc"
  ],
  "wallet_type": "evm",
  "timestamp": "2025-10-15T10:30:00Z"
}
```

**Solana Portfolio (NEW):** ◎

```json
{
  "user_id": "user_solana_portfolio",
  "wallets": [
    "9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY"
  ],
  "chains": [
    "solana"
  ],
  "wallet_type": "solana",
  "timestamp": "2025-10-15T10:30:00Z"
}
```

**Mixed Portfolio (NEW):**

```json
{
  "user_id": "user_multi_chain",
  "wallets": [
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY"
  ],
  "chains": [
    "ethereum",
    "polygon",
    "solana"
  ],
  "wallet_type": "mixed",
  "timestamp": "2025-10-15T10:30:00Z"
}
```

**Important Notes:**

- Maximum **5 chains** per portfolio (Agentverse limit)
- Only **first wallet** of each type scanned per cycle
- EVM wallets validated with ERC-55 checksum
- Solana wallets validated with Base58 format
- Invalid chains/wallets return error via `MessageResponse`

### ⬅️ Output: Portfolio Snapshot

Automatically sends snapshots to Risk Analysis Agent (only if `total_value_usd > $1.00`):

**EVM Snapshot:**

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
      "chain": "ethereum",
      "chain_type": "evm"
    }
  ],
  "timestamp": "2025-10-15T10:35:00Z",
  "risk_score": 0.35,
  "chains_scanned": [
    "ethereum",
    "polygon"
  ],
  "wallet_types": [
    "evm"
  ]
}
```

**Solana Snapshot (NEW):** ◎

```json
{
  "user_id": "user_solana_portfolio",
  "total_value_usd": 25000.00,
  "assets": [
    {
      "token": "SOL",
      "balance": 100.0,
      "value_usd": 14500.00,
      "price": 145.00,
      "change_24h": 5.2,
      "chain": "solana",
      "chain_type": "solana"
    },
    {
      "token": "BONK",
      "balance": 50000000,
      "value_usd": 1175.00,
      "price": 0.0000235,
      "change_24h": 25.5,
      "chain": "solana",
      "chain_type": "solana",
      "is_meme_coin": true,
      "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
    },
    {
      "token": "jitoSOL",
      "balance": 50.0,
      "value_usd": 7800.00,
      "price": 156.00,
      "change_24h": 5.5,
      "chain": "solana",
      "chain_type": "solana",
      "is_lst": true
    }
  ],
  "timestamp": "2025-10-15T10:35:00Z",
  "risk_score": 0.45,
  "chains_scanned": [
    "solana"
  ],
  "wallet_types": [
    "solana"
  ],
  "solana_specific": {
    "spl_tokens_found": 15,
    "meme_coins_detected": 3,
    "lst_tokens": 2
  }
}
```

### ↖️ Registration Response

Immediate feedback via `MessageResponse`:

**Success:**

```json
{
  "message": "✅ Portfolio registered: 1 wallet(s), 3 chain(s). Scanning starts next cycle."
}
```

**Solana Success (NEW):**

```json
{
  "message": "✅ Solana portfolio registered: 1 wallet(s). ◎ SPL token scanning enabled."
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
  "message": "❌ Wallet/Chain Mismatch: Solana wallet cannot monitor EVM chains."
}
```

```json
{
  "message": "Invalid Solana address format"
}
```

---

## 🔄 Agent Workflow

```
1. User Registers Portfolio
         ↓
2. Detect Wallet Type (EVM/Solana/Mixed)
         ↓
3. Validation (Wallets + Chains + Compatibility)
         ↓
4. Storage in ctx.storage
         ↓
5. Wait for Next Scan Cycle (10 min)
         ↓
6. Scan 1 Portfolio (Round-Robin)
         ↓
7. Route by Chain Type:
   ├── EVM: Check wallet on max 3 chains
   └── Solana: Fetch SPL token accounts ◎
         ↓
8. Fetch Balances:
   ├── EVM: Web3 native token balances
   └── Solana: getTokenAccountsByOwner RPC ◎
         ↓
9. Get Prices:
   ├── EVM: CoinGecko API (Cached)
   └── Solana: Jupiter + CoinGecko ◎
         ↓
10. Filter Assets (min $0.01 value)
         ↓
11. Detect Special Tokens:
    └── Solana: Meme coins, LSTs ◎
         ↓
12. Calculate Risk Score
         ↓
13. Create & Store Snapshot (Last 5)
         ↓
14. Send to Risk Agent (if value > $1)
         ↓
15. Repeat for Next Portfolio
```

---

## 🧮 Risk Scoring Algorithm

The agent calculates a composite risk score (0-1) based on multiple factors:

### **1. Concentration Risk (35% weight)**

- Uses Herfindahl-Hirschman Index (HHI)
- Formula: `Σ(asset_value/total_value)²`
- Higher concentration = Higher risk

### **2. Volatility Risk (45% weight)**

- Based on average 24-hour price changes
- Normalized: `min(avg_volatility / 20, 1)`
- Caps at 20% volatility for scaling
- **Solana meme coins weighted higher** ◎

### **3. Chain Diversity Risk (20% weight)**

- Penalizes single-chain portfolios
- Formula: `1.0 if 1 chain else max(0, 1 - unique_chains/5)`
- **Cross-chain bonus for Solana + EVM** ◎

### **Solana-Specific Adjustments (NEW)** ◎

- Meme coin holdings add +0.1 to volatility score
- High LST concentration may reduce risk slightly
- Single-chain Solana portfolios flagged for diversity

**Final Formula:**

```python
risk_score = (
        concentration * 0.35 +
        volatility_score * 0.45 +
        chain_diversity_score * 0.20
)

# Solana adjustments
if has_meme_coins:
    risk_score = min(risk_score + 0.05, 1.0)
```

**Examples:**

| Portfolio                       | Risk Score |
|---------------------------------|------------|
| 100% ETH on 1 chain             | 0.55       |
| Equal split across 3 EVM chains | 0.28       |
| 100% SOL on Solana              | 0.55       |
| SOL + BONK on Solana            | 0.62       |
| ETH + SOL across 2 chains       | 0.25       |

---

## 🔗 Agent Communication

### ➡️ Sends Messages To:

- **Risk Analysis Agent** (`agent1qtrn82fz9tnspwudzrjr7mm9ncwvavjse5xcv7j9t06gajmdxq0yg38dyx5`)
    - Portfolio snapshots with `total_value_usd > $1.00`
    - Sends `PortfolioSnapshot` model with chain type info

### ⬅️ Receives Messages From:

- **Alert Agent** (`agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l`)
    - Portfolio registration via `Portfolio` model
    - Returns `MessageResponse` for confirmation/errors

### Connected Agents:

| Agent           | Address                                                             | Purpose            |
|-----------------|---------------------------------------------------------------------|--------------------|
| Risk Analysis   | `agent1qtrn82fz9tnspwudzrjr7mm9ncwvavjse5xcv7j9t06gajmdxq0yg38dyx5` | Receives snapshots |
| Alert Agent     | `agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l` | User registration  |
| Market Data     | `agent1qgwdvuucfhpvucqdru0gnrwc2zqf0ak5u24rvxua9flcazctmdvdsyrr8qq` | Price feeds        |
| Fraud Detection | `agent1q0x3wcul6azlcu4wy5khce9hklav28ea9f8kjqcq649rs4jat5kc7zxarn6` | Token safety       |

---

## ⚙️ Configuration

### API Integration

| API           | Purpose             | Cache TTL  |
|---------------|---------------------|------------|
| CoinGecko API | EVM token prices    | 60 seconds |
| Jupiter API   | Solana token prices | 30 seconds |
| Solana RPC    | SPL token balances  | Real-time  |
| EVM RPCs      | Native balances     | Real-time  |

### RPC Endpoints

**Solana (NEW):** ◎

- Primary: `https://api.mainnet-beta.solana.com`
- Backup: `https://solana-api.projectserum.com`

**EVM Chains:**

- Ethereum: LlamaRPC, Infura
- BSC: Binance public RPC
- Polygon: Polygon RPC
- Others: Public endpoints

### Monitoring Interval

- **Default**: 600 seconds (10 minutes per cycle)
- **Portfolios per Cycle**: 1 (round-robin rotation)
- **Chains per Scan**: Max 3 (first 3 from registered list)
- **Minimum Asset Value**: $0.01 USD
- **Solana SPL Limit**: Max 50 tokens per scan ◎

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
    "wallets": ["0xChecksum...", "9WzDXwBb..."],  # Validated addresses
    "chains": ["ethereum", "polygon", "solana"],
    "wallet_type": "mixed",  # "evm", "solana", or "mixed"
    "registered_at": "2025-10-15T...",
    "owner": "sender_address",
    "last_scan": "2025-10-15T..."
}
```

**Snapshot Record:**

```python
{
    "user_id": "user_id",
    "total_value_usd": 75000.0,
    "assets": [...],  # List of asset dicts
    "timestamp": "2025-10-15T...",
    "risk_score": 0.35,
    "wallet_types": ["evm", "solana"],
    "chains_scanned": ["ethereum", "solana"]
}
```

**Global Keys:**

- `portfolio_keys`: List of all registered portfolio IDs
- `scan_index`: Current position in round-robin scan

---

## 🚀 Usage Example

### Register an EVM Portfolio

```python
from uagents import Agent, Context, Model
from datetime import datetime, timezone

client = Agent(name="portfolio_client", mailbox=True)


class Portfolio(Model):
    user_id: str
    wallets: list[str]
    chains: list[str]
    wallet_type: str = "evm"
    timestamp: str


class MessageResponse(Model):
    message: str


PORTFOLIO_AGENT = "agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f"


@client.on_event("startup")
async def register_portfolio(ctx: Context):
    portfolio = Portfolio(
        user_id="my_evm_portfolio",
        wallets=["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"],
        chains=["ethereum", "polygon", "arbitrum"],
        wallet_type="evm",
        timestamp=datetime.now(timezone.utc).isoformat()
    )

    await ctx.send(PORTFOLIO_AGENT, portfolio)
    ctx.logger.info("✅ EVM portfolio registration sent!")


if __name__ == "__main__":
    client.run()
```

### Register a Solana Portfolio (NEW) ◎

```python
@client.on_event("startup")
async def register_solana_portfolio(ctx: Context):
    portfolio = Portfolio(
        user_id="my_solana_portfolio",
        wallets=["9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY"],
        chains=["solana"],
        wallet_type="solana",
        timestamp=datetime.now(timezone.utc).isoformat()
    )

    await ctx.send(PORTFOLIO_AGENT, portfolio)
    ctx.logger.info("◎ Solana portfolio registration sent!")
```

### Register a Mixed Portfolio (NEW)

```python
@client.on_event("startup")
async def register_mixed_portfolio(ctx: Context):
    portfolio = Portfolio(
        user_id="my_multi_chain_portfolio",
        wallets=[
            "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",  # EVM
            "9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY"  # Solana
        ],
        chains=["ethereum", "polygon", "solana"],
        wallet_type="mixed",
        timestamp=datetime.now(timezone.utc).isoformat()
    )

    await ctx.send(PORTFOLIO_AGENT, portfolio)
    ctx.logger.info("🔗 Multi-chain portfolio registration sent!")
```

---

## 🔍 Monitoring & Logs

### Key Log Messages

- `📝 Registering portfolio for: {user_id}` - New portfolio validation
- `◎ Solana wallet detected` - Solana routing ◎
- `🔍 Scanning {wallet}... on {n} chain(s)` - Active scan
- `◎ Found {n} SPL tokens in Solana wallet` - SPL token discovery ◎
- `◎ Meme coin detected: {token}` - Meme coin flag ◎
- `📊 ${value}, Risk: {score}%` - Snapshot created
- `🔄 Scanning portfolio {i}/{total}: {user_id}` - Cycle progress
- `Next scan in 10 minutes (portfolio {next}/{total})` - Queue status

### Error Handling

- Invalid wallets: Immediate rejection with error details
- Wallet/chain mismatch: Clear error message
- RPC failures: Logged and skipped (doesn't crash agent)
- CoinGecko/Jupiter errors: Returns $0 price (logs warning)
- No assets found: Logs info but doesn't send to Risk Agent
- Solana RPC timeout: Retries with backup endpoint

---

## 🛠️ Technical Stack

- **Framework**: Fetch.ai uAgents `v0.22.10`
- **Language**: Python 3.10+
- **Networking**: aiohttp (async HTTP)
- **EVM Blockchain**: Web3.py `v7.13`
- **Solana Blockchain**: solana-py, solders ◎
- **APIs**:
    - CoinGecko API v3 (Free Tier)
    - Jupiter Price API ◎
- **Async**: asyncio for concurrent chain scans
- **Deployment**: Agentverse Cloud Platform
- **Storage**: Agentverse Context Storage

---

## 🔐 Security Features

- ✅ **No Private Keys** - Only monitors public addresses
- ✅ **Read-Only Operations** - Cannot execute transactions
- ✅ **EVM Checksum Validation** - ERC-55 address verification
- ✅ **Solana Base58 Validation** - Format verification ◎
- ✅ **Zero Address Protection** - Rejects null addresses
- ✅ **Chain Compatibility Check** - Prevents mismatched wallets
- ✅ **Rate Limited API** - Respects free tier limits
- ✅ **Error Isolation** - Wallet/chain failures don't cascade
- ✅ **Input Validation** - Regex + library validation on all addresses

---

## 📈 Performance Metrics

| Metric          | EVM         | Solana       |
|-----------------|-------------|--------------|
| Scan Time       | 2-5 sec     | 3-6 sec      |
| Tokens per Scan | Native only | Up to 50 SPL |
| Cache Hit Rate  | ~90%        | ~85%         |
| RPC Timeout     | 5 sec       | 10 sec       |
| API Calls       | 3-4         | 5-8          |

### Agentverse Optimizations

- **Single Wallet Scanning**: Only first wallet per type per cycle
- **Chain Limit**: Max 3 chains per scan (from first 3 registered)
- **SPL Token Limit**: Max 50 tokens per Solana scan ◎
- **Minimum Threshold**: Skips assets < $0.01
- **Round-Robin**: Distributes load across portfolios
- **Snapshot Limit**: Stores only last 5 per user

---

## 🤝 Integration with DeFiGuard Ecosystem

This agent is part of the **DeFiGuard Multi-Agent System**:

> 1. **Portfolio Monitor** ← Current Agent (Data Collection)

2. **Risk Analysis** - Receives snapshots via `PortfolioSnapshot` messages
3. **Alert Agent** - Notified by Risk Agent on high-risk detection
4. **Market Data** - Provides price feeds (EVM + Solana)
5. **Fraud Detection** - Validates token safety (RugCheck for Solana)

**Chains Supported:** 13 total (◎ Solana + ⟠ 12 EVM)

---

## 🐛 Known Limitations

1. **Token Support**: Native tokens (EVM) + SPL tokens (Solana)
2. **ERC-20 Tracking**: Not yet implemented for EVM chains
3. **Wallet Limitation**: Scans only first wallet per type per portfolio
4. **Chain Limitation**: Max 3 chains per scan cycle
5. **SPL Token Limit**: Max 50 tokens per Solana scan ◎
6. **Historical Data**: Only last 5 snapshots stored
7. **API Dependency**: Relies on CoinGecko/Jupiter free tiers
8. **No Transaction History**: Balance-only monitoring

---

## 🆕 What's New in v2.0.0-solana

- ◎ **Solana wallet support** - Base58 address validation
- ◎ **SPL token scanning** - All Solana token holdings
- ◎ **Jupiter price integration** - Real-time Solana prices
- ◎ **Meme coin detection** - Flags BONK, WIF, POPCAT, etc.
- ◎ **LST tracking** - mSOL, jitoSOL, bSOL support
- ◎ **Mint address resolution** - Map mints to symbols
- 🔗 **Mixed portfolios** - EVM + Solana in one registration
- 🔗 **Wallet type tracking** - evm, solana, or mixed
- 🔗 **Chain compatibility validation** - Prevents mismatches
- 📊 **Enhanced snapshots** - Chain type and Solana metadata

---

## 📞 Support & Contact

- **GitHub**: [DeFiGuard Repository](https://github.com/DhanteyUD/DeFiGuard)
- **Issues**: Report bugs via GitHub Issues

---

## 📄 License

MIT License - Open Source

---

**Powered by ASI Alliance** | **Built with Fetch.ai uAgents** | **Deployed on Agentverse**

*Updated: February 2026 | Version 2.0.0-solana*