# 🛡️ DeFiGuard: Multi-Agent Risk Management System

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

**DeFiGuard** is an autonomous, decentralized portfolio risk management system powered by the ASI Alliance. It monitors crypto portfolios across multiple chains, analyzes risks using AI reasoning, detects fraud, and provides real-time alerts through ASI:One interface.

## 🎥 Demo Video

[Watch Demo Video (3-5 minutes)](YOUR_YOUTUBE_LINK_HERE)

## 🏗️ Architecture

```
┌────────────────────────────────────────────────┐
│                 USER INTERFACE                 │
│                 (ASI:One Chat)                 │
└──────────────────────┬─────────────────────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │       Alert Agent      │ ◄────── Real-time Notifications
          │     (Chat Protocol)    │
          └────────┬───────────────┘
                   │
       ┌───────────┼───────────┬──────────┐
       ▼           ▼           ▼          ▼
┌──────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐
│Portfolio │ │   Risk   │ │ Market  │ │  Fraud   │
│ Monitor  │ │ Analysis │ │  Data   │ │Detection │
│  Agent   │ │  Agent   │ │  Agent  │ │  Agent   │
└────┬─────┘ └────┬─────┘ └────┬────┘ └────┬─────┘
     │            │            │           │
     └────────────┴────────────┴───────────┘
                       │
                       ▼
               ┌──────────────┐
               │    MeTTa     │
               │  Knowledge   │
               │    Graph     │
               └──────────────┘
```

## 🤖 Agent Addresses

All agents are deployed on **Agentverse** with Chat Protocol enabled:

| Agent                 | Address         | Port | Function                               |
|-----------------------|-----------------|------|----------------------------------------|
| **Portfolio Monitor** | `agent1qf8x...` | 8000 | Tracks wallet balances across chains   |
| **Risk Analysis**     | `agent1qz3y...` | 8001 | AI-powered risk assessment with MeTTa  |
| **Alert System**      | `agent1qa2b...` | 8002 | ASI:One chat interface & notifications |
| **Market Data**       | `agent1qm5n...` | 8003 | Real-time price & volume data          |
| **Fraud Detection**   | `agent1qp7k...` | 8004 | Scam & honeypot detection              |

> **Note**: Replace with your actual agent addresses after deployment

## ✨ Features

### 🔍 Real-Time Portfolio Monitoring
- Multi-chain support (Ethereum, Polygon, BSC, Arbitrum)
- Automatic balance tracking every 5 minutes
- Historical snapshot comparison

### 🧠 AI-Powered Risk Analysis
- MeTTa Knowledge Graph for pattern recognition
- Multi-factor risk scoring:
  - Concentration risk (Herfindahl Index)
  - Volatility analysis (24h/7d/30d changes)
  - Asset-specific risks
  - Liquidity assessment
- Dynamic recommendations

### 🚨 Intelligent Alerts
- Risk-based alert levels (Low → Critical)
- ASI:One chat integration
- Customizable alert thresholds
- Alert history tracking

### 📊 Market Intelligence
- CoinGecko API integration
- Price change detection
- Volume spike identification
- Multi-token batch requests

### 🕵️ Fraud Detection
- Honeypot detection
- High tax identification
- Ownership analysis
- Liquidity risk assessment
- Holder concentration analysis

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Git
git --version
```

### Installation

```bash
# Clone repository
git clone https://github.com/DhanteyUD/DeFiGuard.git
cd DeFiGuard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy environment template:**
```bash
cp .env.example .env
```

2. **Edit `.env` with your settings:**
```env
# Agent Seeds (MUST CHANGE THESE!)
PORTFOLIO_AGENT_SEED=your_unique_seed_here
RISK_AGENT_SEED=your_unique_seed_here
ALERT_AGENT_SEED=your_unique_seed_here
MARKET_AGENT_SEED=your_unique_seed_here
FRAUD_AGENT_SEED=your_unique_seed_here

# API Keys (Optional but recommended)
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
COINGECKO_API_KEY=your_coingecko_key
ETHERSCAN_API_KEY=your_etherscan_key

# Configuration
NETWORK=testnet
LOG_LEVEL=INFO
RISK_THRESHOLD=
ALERT_COOLDOWN=
MONITOR_INTERVAL=
```

### Running DeFiGuard

```bash
# Start all agents
python main.py
```

You should see:
```
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                  DEFIGUARD SYSTEM v1.0                    ║
    ║                                                           ║
    ║           Multi-Agent Risk Management System              ║
    ║                Powered by ASI Alliance                    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    📊 Agent Status:
    
    ✓ Portfolio Monitor   : agent1qf8x...
    ✓ Risk Analyzer       : agent1qz3y...
    ✓ Alert System        : agent1qa2b...
    ✓ Market Data         : agent1qm5n...
    ✓ Fraud Detection     : agent1qp7k...
    
    🚀 All agents initialized successfully!
    🌐 ASI:One Chat Protocol enabled
```

## 📱 Using DeFiGuard

### 1. Register Your Portfolio

Send a message to the Portfolio Monitor Agent:

```python
from agents.portfolio_monitor import Portfolio
from datetime import datetime, UTC

portfolio = Portfolio(
    user_id="your_user_id",
    wallets=[
        "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "0xYourSecondWallet..."
    ],
    chains=["ethereum", "polygon", "bsc"],
    timestamp=datetime.now(UTC).isoformat()
)
```

### 2. Interact via ASI:One

1. Go to [ASI:One Interface](https://asione.fetch.ai)
2. Search for "DeFiGuard Alert System"
3. Start chatting!

**Available Commands:**
- `status` - Check current portfolio risk
- `history` - View recent alerts
- `help` - Show available commands

### 3. Automated Monitoring

Once registered, DeFiGuard automatically:
- Monitors your portfolio every 5 minutes
- Analyzes risk using MeTTa knowledge graphs
- Sends alerts when risk thresholds are exceeded
- Detects suspicious market activities

## 🧪 Testing

Run the test suite:

```bash
# Make sure main.py is running in another terminal
python tests/test_system.py
```

This will test:
- ✅ Portfolio registration
- ✅ Risk analysis
- ✅ Market data fetching
- ✅ Fraud detection

## 🛠️ Technologies Used

### ASI Alliance Stack
- **Fetch.ai uAgents Framework** - Agent development & communication
- **Agentverse** - Agent deployment & registry
- **ASI:One Chat Protocol** - User interface integration
- **SingularityNET MeTTa** - Knowledge graph reasoning

### Supporting Technologies
- **Python 3.8+** - Core language
- **CoinGecko API** - Market data
- **Web3.py** - Blockchain interaction
- **aiohttp** - Async HTTP requests
- **Hyperon** - MeTTa runtime

## 📊 Risk Scoring Methodology

DeFiGuard uses a weighted multi-factor risk score:

```
Risk Score = (Concentration × 0.3) + (Volatility × 0.4) + (Asset Risk × 0.3)
```

### Risk Levels
- 🟢 **Low** (0-30%): Portfolio is healthy
- 🟡 **Medium** (30-50%): Monitor closely
- 🟠 **High** (50-70%): Action recommended within 24h
- 🔴 **Critical** (70-100%): Immediate action required

### Concentration Risk
Measured using Herfindahl-Hirschman Index (HHI):
- Single asset >50% of portfolio = High risk
- Single asset >70% = Critical risk

### Volatility Risk
Based on 24h price changes:
- >20% change = High volatility
- >50% change = Extreme volatility

## 🔐 Security & Privacy

- **No Private Keys**: DeFiGuard only monitors public wallet addresses
- **Decentralized**: No central database - data stays with agents
- **Open Source**: All code is auditable
- **Privacy First**: User data never leaves the agent network

## 🎯 Use Cases

1. **Portfolio Risk Management**
   - Track diversification across chains
   - Get alerts before major draw-downs

2. **Fraud Prevention**
   - Analyze tokens before investing
   - Detect honeypots and scams

3. **Market Intelligence**
   - Track price movements
   - Identify unusual volume patterns

4. **Automated Rebalancing**
   - Get recommendations when portfolio drifts
   - Maintain target allocations

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ASI Alliance** for the hackathon opportunity
- **Fetch.ai** for uAgents framework
- **SingularityNET** for MeTTa knowledge graphs
- **CoinGecko** for market data API

## 📞 Contact

- **Project Link**: [https://github.com/DhanteyUD/DeFiGuard](https://github.com/DhanteyUD/DeFiGuard)
- **Demo Video**: [YouTube Link](YOUR_LINK)
- **ASI:One Agent**: Search "DeFiGuard" in ASI:One

---

**Built with ❤️ for ASI Alliance Hackathon**

*Securing DeFi, one portfolio at a time* 🛡️