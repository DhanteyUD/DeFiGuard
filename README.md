# 🛡️ DeFiGuard-2.0: Multi-Agent Risk Management System

![Solana](https://img.shields.io/badge/Solana-Ready-14F195?logo=solana) ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1) ![Python](https://img.shields.io/badge/python-3.12-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg)

**AI-powered, multi-chain DeFi portfolio risk monitoring with autonomous agents**

Monitor crypto portfolios across **Solana + 12 EVM chains**, analyze risks using SingularityNET MeTTa AI, detect fraud,
and receive real-time alerts via ASI:One chat.

---

## 📋 Table of Contents

- [Solana Integration](#-solana-integration)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Solana Usage](#-solana-usage)
- [Risk Scoring](#-risk-scoring-methodology)
- [Supported Chains](#-supported-chains)
- [Documentation](#-documentation)
- [Technologies](#-technologies)
- [Recognition](#-recognition)
- [Security](#-security)
- [Contact](#-contact)
- [License](#-license)

---

## 🆕 Solana Integration

DeFiGuard now features **comprehensive Solana blockchain support**:

###  Solana Features

| Feature                    | Description                                          |
|----------------------------|------------------------------------------------------|
| **Wallet Monitoring**      | Track SOL + all SPL token balances                   |
| **Fraud Detection**        | Solana-specific scam analysis                        |
| **Mint Authority Check**   | Detects tokens with active mint authority (rug risk) |
| **Freeze Authority Check** | Warns when tokens can be frozen                      |
| **RugCheck Integration**   | Community-verified scam database                     |
| **Jupiter Verification**   | Confirms tokens on trusted lists                     |
| **Holder Analysis**        | Concentration risk for Solana tokens                 |

### Supported Solana Assets

- **Native:** SOL
- **Stablecoins:** USDC, USDT
- **DeFi:** RAY, ORCA, JUP, MNDE, Jito
- **Liquid Staking:** mSOL, jitoSOL
- **Meme Coins:** BONK, WIF (flagged as high-risk)

---

## ✨ Key Features

| Feature                      | Chains          | Technology                |
|------------------------------|-----------------|---------------------------|
| **⌕ Multi-Chain Monitoring** | Solana + 12 EVM | Native RPC integration    |
| **🧠 AI Risk Analysis**      | All chains      | SingularityNET MeTTa      |
| **💬 Chat Interface**        | N/A             | ASI:One + ASI-1 model     |
| **🚨 Real-Time Alerts**      | All chains      | Instant notifications     |
| **🕵️ Fraud Detection**      | Solana + EVM    | GoPlus, RugCheck, Jupiter |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│                  USER INTERFACE                    │
│                  (ASI:One Chat)                    │
└──────────────────────┬─────────────────────────────┘
                       │
                       ▼
              ┌────────────────────────┐
              │      Alert Agent       │ ◄── Real-time Notifications
              │    (Chat Protocol)     │
              └────────┬───────────────┘
                       │
           ┌───────────┼───────────┬──────────┐
           ▼           ▼           ▼          ▼
    ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐
    │Portfolio │ │   Risk   │ │ Market  │ │  Fraud   │
    │ Monitor  │ │ Analysis │ │  Data   │ │ Detection│
    │  Agent   │ │  Agent   │ │  Agent  │ │  Agent   │
    └────┬─────┘ └────┬─────┘ └────┬────┘ └────┬─────┘
         │            │            │           │
         └────────────┴────────────┴───────────┘
                             │
              ┌──────────────┴──────────────┐
              │      Blockchain APIs        │
              │  ◎ Solana RPC               │
              │  ⟠ EVM RPCs (12 chains)     │
              │  ₿ CoinGecko                │
              │  ⌕ GoPlus / RugCheck        │
              └─────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
python --version  # 3.10+
```

### Installation

```bash
# Clone repository
git clone https://github.com/DhanteyUD/DeFiGuard.git
cd DeFiGuard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your AGENT_SEEDS

# Run tests
python tests/test_integration.py

# Start all agents
python main.py
```

---

## ◎ Solana Usage

### Register a Solana Wallet

Via ASI:One Chat:

```
register 9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY solana
```

### Analyze a Solana Token

```python
from uagents import Agent, Context, Model


class TokenAnalysisRequest(Model):
    token_address: str
    chain: str


# Request fraud analysis for a Solana token
request = TokenAnalysisRequest(
    token_address="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",  # BONK
    chain="solana"
)

await ctx.send(FRAUD_AGENT_ADDRESS, request)
```

### Solana-Specific Risk Factors

| Risk Factor             | Weight | Description                 |
|-------------------------|--------|-----------------------------|
| Mint Authority Active   | 25%    | Can create unlimited tokens |
| Freeze Authority Active | 30%    | Can freeze your tokens      |
| Holder Concentration    | 25%    | Top holder owns >30%        |
| Low Liquidity           | 20%    | Hard to exit position       |

---

## 📊 Risk Scoring Methodology

### Formula

```
Risk Score = (Concentration × 0.30) + (Volatility × 0.35) + 
             (Asset Quality × 0.20) + (Chain Diversity × 0.15)
```

### Solana Token Risk Levels

| Risk Level | Score  | Indicators                  |
|------------|--------|-----------------------------|
| 🟢 Safe    | 0-19   | Verified, authority revoked |
| 🟡 Low     | 20-39  | Minor concerns              |
| 🟠 Medium  | 40-59  | Multiple warnings           |
| 🔴 High    | 60-79  | Significant red flags       |
| ⚫ Critical | 80-100 | Likely scam/rug pull        |

---

## 🔗 Supported Chains

### Solana Ecosystem

- ◎ **Solana Mainnet** - Full SPL token support

### EVM Chains (12)

- Ethereum, BSC, Polygon, Arbitrum, Optimism
- Avalanche, Base, Fantom, Gnosis
- Moonbeam, Celo, Cronos

---

## 📚 Documentation

| Document                                              | Description                |
|-------------------------------------------------------|----------------------------|
| [MeTTa Integration](docs/METTA_INTEGRATION.md)        | AI knowledge graph         |
| [Agent Docs](docs/agents)                             | Individual agent specs     |

---

## 🛠️ Technologies

| Component       | Technology                  |
|-----------------|-----------------------------|
| Agent Framework | Fetch.ai uAgents `v0.22.10` |
| AI Reasoning    | SingularityNET MeTTa        |
| Solana          | solana-py, RugCheck API     |
| EVM             | Web3.py, GoPlus API         |
| Chat            | ASI:One Protocol            |
| Language        | Python `3.12`               |

---

## 🏆 Recognition

- 🥇 **Colosseum Cypherpunk Hackathon Winner**
- 🎯 ASI Alliance Hackathon Participant

---

## 🔐 Security

- ✅ Read-only monitoring (no private keys)
- ✅ ERC-55 + Base58 address validation
- ✅ Rate limiting on all APIs
- ✅ Error isolation across agents

---

## 📞 Contact

- **GitHub:** [DhanteyUD/DeFiGuard](https://github.com/DhanteyUD/DeFiGuard)
- **Demo v1:** [YouTube](https://www.youtube.com/watch?v=xyt-SBwxnIo)
- **ASI:One:** Search `DeFiGuard-2.0`

---

## 📄 License

MIT License - Open Source

---

**Built with ❤️ by [DhanteyUD](https://github.com/DhanteyUD)**

*Protecting DeFi portfolios across Solana and beyond* 🛡️◎

---

**Powered by ASI Alliance** | **Fetch.ai uAgents** | **SingularityNET MeTTa** | **Solana**
