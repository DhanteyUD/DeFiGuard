# 🛡️ DeFiGuard: Multi-Agent Risk Management System

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**DeFiGuard** is an autonomous, decentralized portfolio risk management system powered by the ASI Alliance. It monitors crypto portfolios across multiple chains, analyzes risks using AI reasoning with SingularityNET's MeTTa, detects fraud, and provides real-time alerts through ASI:One chat interface.

---

## 📋 Table of Contents

- [Demo Video](#-demo-video)
- [Architecture](#-architecture)
- [ASI Alliance Technologies](#-asi-alliance-technologies)
- [Features](#-features)
- [Agent Addresses](#-agent-addresses)
- [Quick Start](#-quick-start)
- [Using DeFiGuard](#-using-defiguard)
- [Risk Scoring Methodology](#-risk-scoring-methodology)
- [Technologies Used](#-technologies-used)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎥 Demo Video

[▶️ Watch Demo Video (3-5 minutes)](YOUR_YOUTUBE_LINK_HERE)

---

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
    │ Monitor  │ │ Analysis │ │  Data   │ │ Detection│
    │  Agent   │ │  Agent   │ │  Agent  │ │  Agent   │
    └────┬─────┘ └────┬─────┘ └────┬────┘ └────┬─────┘
         │            │            │           │
         └────────────┴────────────┴───────────┘
                             │
                             ▼
    ┌────────────────────────────────────────────────┐
    │              MeTTa Knowledge Graph             │
    │           (50+ assets, 25+ risk rules)         │
    └────────────────────────────────────────────────┘   
                   
```

---

## 🤖 ASI Alliance Technologies

DeFiGuard leverages the **full ASI Alliance technology stack** to deliver intelligent, autonomous risk management.

### ✅ Fetch.ai Integration

| Component                 | Usage in DeFiGuard              | Benefits                           |
|---------------------------|---------------------------------|------------------------------------|
| **uAgents Framework**     | All 5 agents built with uAgents | Autonomous agent development       |
| **Agentverse**            | Cloud deployment platform       | Scalable, always-on infrastructure |
| **ASI:One Chat Protocol** | Alert agent user interface      | Natural language interaction       |
| **Agent Communication**   | Inter-agent messaging           | Decentralized coordination         |
| **Bureau System**         | Multi-agent orchestration       | Centralized management             |

**Implementation:**
- 5 specialized agents communicating autonomously
- Real-time message passing between agents
- Deployed to Agentverse for 24/7 operation
- Chat interface for user interaction

### ✅ SingularityNET Integration

| Component                  | Usage in DeFiGuard                   | Benefits              |
|----------------------------|--------------------------------------|-----------------------|
| **MeTTa Knowledge Graphs** | Risk analysis reasoning engine       | Declarative AI logic  |
| **Knowledge Base**         | 50+ asset classifications, 25+ rules | Explainable decisions |
| **Pattern Matching**       | Fraud and risk detection             | Intelligent reasoning |
| **Logical Inference**      | Portfolio risk assessment            | Composable rules      |

**Implementation:**
- MeTTa knowledge graph with comprehensive risk ontology
- Query-based risk classification system
- Explainable AI - every decision traceable to knowledge base
- Extensible rule system for domain experts

**📚 Detailed Integration:** See [docs/METTA_INTEGRATION.md](docs/METTA_INTEGRATION.md)

### 🔗 Why Both Technologies?

| Aspect           | Fetch.ai                          | SingularityNET              |
|------------------|-----------------------------------|-----------------------------|
| **Purpose**      | Agent infrastructure              | AI reasoning                |
| **Role**         | Communication & orchestration     | Knowledge & intelligence    |
| **In DeFiGuard** | Agents talk to each other         | Agents make smart decisions |
| **Analogy**      | Nervous system                    | Brain                       |
| **Example**      | Portfolio Monitor → Risk Analyzer | Risk rules in MeTTa graph   |

**Together**: Fetch.ai provides the **communication layer**, SingularityNET provides the **intelligence layer**. This combination creates truly autonomous, intelligent agents.

---

## ✨ Features

### 🔍 Real-Time Portfolio Monitoring
- ✅ **Multi-chain support**: Ethereum, Polygon, BSC
- ✅ **Automatic balance tracking**: Every 5 minutes
- ✅ **Historical snapshots**: Track portfolio changes over time
- ✅ **Asset valuation**: Real-time USD pricing via CoinGecko
- ✅ **Cross-chain aggregation**: Unified view of all holdings

### 🧠 AI-Powered Risk Analysis (MeTTa)
- ✅ **MeTTa Knowledge Graph**: SingularityNET reasoning engine
- ✅ **Multi-factor risk scoring**:
  - Concentration risk (Herfindahl-Hirschman Index)
  - Volatility analysis (24h/7d/30d price changes)
  - Asset quality assessment
  - Liquidity risk evaluation
- ✅ **Explainable AI**: Every decision traceable to knowledge base
- ✅ **Dynamic recommendations**: Context-aware advice
- ✅ **Pattern recognition**: Identifies complex risk scenarios

### 🚨 Intelligent Alerts (ASI:One)
- ✅ **Risk-based levels**: Low → Medium → High → Critical
- ✅ **ASI:One chat integration**: Natural language interface
- ✅ **Interactive commands**: `status`, `history`, `portfolio`, `register  <wallet> <chains>`, `help`
- ✅ **Customizable thresholds**: Personalized risk tolerance
- ✅ **Alert history**: Track past notifications
- ✅ **Real-time delivery**: Instant notifications

### 📊 Market Intelligence
- ✅ **CoinGecko API integration**: 10,000+ token coverage
- ✅ **Price change detection**: Alerts on significant moves (>10%)
- ✅ **Volume spike identification**: Unusual trading activity
- ✅ **Multi-token batch requests**: Efficient data retrieval
- ✅ **Market cap tracking**: Total and circulating supply
- ✅ **5-minute cache**: Optimized API usage

### 🕵️ Fraud Detection
- ✅ **Honeypot detection**: Identifies tokens that can't be sold
- ✅ **High tax identification**: Flags excessive buy/sell taxes (>10%)
- ✅ **Ownership analysis**: Checks if ownership is renounced
- ✅ **Liquidity risk assessment**: Evaluates exit difficulty
- ✅ **Holder concentration**: Tracks whale dominance
- ✅ **Scam pattern matching**: Known fraud indicators

---

## 🤖 Agent Addresses

Local agents (community/open source version): See [agents](agents)

| Agent                 | Address                                                             | Port | 
|-----------------------|---------------------------------------------------------------------|------|
| **Portfolio Monitor** | `agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f` | 8000 | 
| **Risk Analysis**     | `agent1qtrn82fz9tnspwudzrjr7mm9ncwvavjse5xcv7j9t06gajmdxq0yg38dyx5` | 8001 | 
| **Alert Agent**       | `agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l` | 8002 | 
| **Market Data**       | `agent1qgwdvuucfhpvucqdru0gnrwc2zqf0ak5u24rvxua9flcazctmdvdsyrr8qq` | 8003 | 
| **Fraud Detection**   | `agent1q0x3wcul6azlcu4wy5khce9hklav28ea9f8kjqcq649rs4jat5kc7zxarn6` | 8004 |


All agents deployed on **[Agentverse](https://agentverse.ai/agents)** (Fetch.ai Testnet): See [agentverse](agentverse)


| Agent                 | Agentverse Address                                                  | Status                   |
|-----------------------|---------------------------------------------------------------------|--------------------------|
| **Portfolio Monitor** | `agent1qt2fhu92p6uq3yq692drxrnx74yh7jqs0vjm65st3tz6wej6rxf7qehenpc` | ✅ Active                 |
| **Risk Analysis**     | `agent1qwwc3jwx0x6z0sk07029n9ngztsrapcc0ngdwy8swzq50tt7t0nf726tmkm` | ✅ Active                 |
| **Alert Agent**       | `agent1qftjr2fh4uuk0se60sp6e6yevamtlmh5tlsjxx9ny2kgenggf089unxed9f` | ✅ Active + Chat Protocol |
| **Market Data**       | `agent1qt70kl5x938q9dlryd9tnfr3yk5z3pmaq85jrl5vkwsguhwxazdyjr29aw3` | ✅ Active                 |
| **Fraud Detection**   | `agent1q220sdmkgn3dj2pxz38cmeer2kt335ev6vqhta3f4a0cuz4h9zcwyp5qzm5` | ✅ Active                 |

**📖 Individual Agent Documentation:** See [docs/agents](docs/agents) for detailed README for each agent.


<img width="1101" height="739" alt="Screenshot 2025-10-15 at 3 15 19 AM" src="https://github.com/user-attachments/assets/e49b921d-3735-4bab-a5ce-643ddfd3bed6" />


---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python --version  # Should be 3.8 or higher

# Git (for cloning)
git --version
```

### Installation

```bash
# 1. Clone repository
git clone https://github.com/DhanteyUD/DeFiGuard.git
cd DeFiGuard

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Configuration

#### 1. Create Environment File
```bash
cp .env.example .env
```

#### 2. Update `.env` with Your Settings

**Minimum Required (Generate Random Strings):**
```env
# Agent Seeds - Change these to unique random strings!
PORTFOLIO_AGENT_SEED=your_random_portfolio_seed_12345678901234
RISK_AGENT_SEED=your_random_risk_seed_23456789012345678
ALERT_AGENT_SEED=your_random_alert_seed_34567890123456789
MARKET_AGENT_SEED=your_random_market_seed_45678901234567890
FRAUD_AGENT_SEED=your_random_fraud_seed_56789012345678901
```

**Optional (For Better Functionality):**
```env
# API Keys (Free tiers available)
COINGECKO_API_KEY=your_coingecko_api_key
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
BSC_RPC_URL=https://bsc-dataseed.binance.org/
ETHERSCAN_API_KEY=YOUR_KEY

# Configuration
NETWORK=testnet
RISK_THRESHOLD=0.7
ALERT_COOLDOWN=300
MONITOR_INTERVAL=300
LOG_LEVEL=INFO
MAX_RETRIES=3
API_TIMEOUT=30
```

**💡 Tip:** Generate secure seeds with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Verify MeTTa Integration (SingularityNET)

```bash
# Test MeTTa installation and knowledge base
python verify_metta.py
```

Expected output:
```
✅ MeTTa (SingularityNET) integration active
✅ Knowledge base loaded from metta/risk_knowledge.metta
✅ bitcoin: low
✅ Pattern 'leverage': critical
📊 VERIFICATION SUMMARY: ✅ OPERATIONAL
```

If MeTTa fails to install, DeFiGuard will use Python fallback mode.

### Run DeFiGuard

```bash
# Start all 5 agents
python main.py
```

**Success Output:**
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
    
  ✓ Portfolio Monitor   : agent1qv3pywlds6...
  ✓ Risk Analysis       : agent1qtrn82fz9t...
  ✓ Alert Agent         : agent1q2zusjcsgl...
  ✓ Market Data         : agent1qgwdvuucfh...
  ✓ Fraud Detection     : agent1q0x3wcul6a...

  🚀 All agents initialized successfully!
  🌐 ASI:One Chat Protocol enabled on Alert Agent
  🧠 SingularityNET MeTTa integration: ACTIVE

============================================================
```

---

## 📱 Using DeFiGuard

### Method 1: Via ASI:One Chat (Recommended)

1. **Open ASI:One**: https://asi1.ai
2. **Search for Agent**: Use agent name `DeFiGuard alert agent` or  address `agent1qftjr2fh4uuk0se60sp6e6yevamtlmh5tlsjxx9ny2kgenggf089unxed9f`
3. **Start Chatting**:

```
User: [Opens Chat]
Agent: 👋 Welcome to DeFiGuard Alert Agent!
       
       To get started, register your portfolio:
       
       Format: register <wallet_address> <chains>
       Example: register 0x742d35...0bEb ethereum,polygon
       
       Type 'help' for more commands.

User: register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon
Agent: ✅ Portfolio Registered Successfully!
       
       Wallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
       Chains: ethereum, polygon
       
       Your portfolio is now being monitored 24/7.
       Type 'status' to check your current risk level.

User: portfolio
Agent: 📋 Your Registered Portfolio
       
       Wallets:
       1. 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
       
       Chains: ethereum, polygon
       Registered: 2025-10-14T10:35
       
       To update: register <new_wallet> <chains>

User: status
Agent: 📊 Current Portfolio Status
       Risk Level: MEDIUM
       Risk Score: 45%
       Last Updated: 2025-10-14T10:30
       
       Type 'history' for more details.

User: history
Agent: 📜 Recent Alerts
       1. MEDIUM (45%) - 2025-10-14 10:30
       2. LOW (32%) - 2025-10-13 15:20
       3. LOW (28%) - 2025-10-12 09:15
```


**Available Commands:**
- `register <wallet> <chains>` - Register portfolio
- `status` - Check current portfolio risk level
- `history` - View recent alerts (last 5)
- `portfolio` - View registered portfolio
- `help` - Show command reference

### Method 2: Via Agentverse AI

1. **Open Agentverse AI**: https://chat.agentverse.ai/
2. **Search for Agent**: Use agent name `DeFiGuard alert agent` or  address `agent1qftjr2fh4uuk0se60sp6e6yevamtlmh5tlsjxx9ny2kgenggf089unxed9f`
3. **Start Chatting**:

### Method 3: Programmatic (Direct Agent Messaging)

```python
from uagents import Agent, Context, Model
from agents.portfolio_monitor import Portfolio
from datetime import datetime, timezone

# Create your client agent
client = Agent(name="my_client", mailbox=True)

@client.on_event("startup")
async def register_portfolio(ctx: Context):
    # Send portfolio registration
    portfolio = Portfolio(
        user_id="0xYourWalletAddress",
        wallets=[
            "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "0xYourSecondWallet..."
        ],
        chains=["ethereum", "polygon", "bsc"],
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    # Send to Portfolio Monitor Agent
    await ctx.send(
        "agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f",
        portfolio
    )
    ctx.logger.info("✅ Portfolio registered!")

if __name__ == "__main__":
    client.run()
```

### Automated Monitoring

Once registered, DeFiGuard automatically:

1. **Scans portfolio** every 5 minutes
2. **Queries MeTTa knowledge graph** for risk assessment
3. **Calculates risk score** using multi-factor analysis
4. **Sends alerts** when thresholds exceeded
5. **Detects market anomalies** (price spikes, volume changes)
6. **Checks for fraud** in new token holdings

---

## 📊 Risk Scoring Methodology

### Multi-Factor Risk Formula

```
Risk Score = (Concentration × 0.3) + (Volatility × 0.4) + (Asset Quality × 0.3)
```

### Risk Levels

| Level           | Score   | Indicator            | Action               |
|-----------------|---------|----------------------|----------------------|
| 🟢 **Low**      | 0-30%   | Portfolio is healthy | Continue monitoring  |
| 🟡 **Medium**   | 30-50%  | Monitor closely      | Review within week   |
| 🟠 **High**     | 50-70%  | Action recommended   | Rebalance within 24h |
| 🔴 **Critical** | 70-100% | Immediate action     | Review immediately   |

### Risk Components

#### 1. Concentration Risk (30% weight)
- **Method**: Herfindahl-Hirschman Index (HHI)
- **Formula**: `HHI = Σ(asset_percentage²)`
- **Thresholds** (via MeTTa):
  - Critical: Single asset >70%
  - High: Single asset >50%
  - Medium: Single asset >30%

#### 2. Volatility Risk (40% weight)
- **Method**: 24-hour price change analysis
- **Formula**: `volatility_score = avg_change / 20`
- **Thresholds** (via MeTTa):
  - Extreme: >50% change in 24h
  - High: >20% change in 24h
  - Medium: >10% change in 24h

#### 3. Asset Quality Risk (30% weight)
- **Method**: MeTTa knowledge graph classification
- **Factors**:
  - Token reputation (via MeTTa: `has-risk bitcoin low`)
  - Leverage indicators (via MeTTa: `has-risk-pattern leverage critical`)
  - Stablecoin ratio
  - Liquidity metrics

### MeTTa-Powered Reasoning

All risk thresholds and classifications are defined in the MeTTa knowledge graph:

```metta
; Example rules from metta/risk_knowledge.metta

; Asset classifications
(has-risk bitcoin low)
(has-risk ethereum low)
(has-risk-pattern leverage critical)

; Concentration thresholds
(concentration-threshold critical 0.70)
(concentration-threshold high 0.50)

; Volatility thresholds
(volatility-threshold extreme 50)
(volatility-threshold high 20)
```

**🧠 Benefits:**
- Explainable: Every decision traceable to knowledge base
- Extensible: Add new rules without code changes
- Maintainable: Domain experts can update rules
- Composable: Rules combine for complex reasoning

---

## 🧪 Testing

### Run Integration Tests

```bash
# Terminal 1: Start agents
python main.py

# Terminal 2: Run tests
python tests/test_system.py
```

**Tests cover:**
- ✅ Portfolio registration
- ✅ Risk analysis with MeTTa
- ✅ Market data fetching
- ✅ Fraud detection
- ✅ Alert generation

### Verify MeTTa Integration

```bash
python verify_metta.py
```

---

## 🛠️ Technologies Used

### Core Stack

| Technology               | Version  | Purpose             |
|--------------------------|----------|---------------------|
| **Python**               | ` 3.12`  | Core language       |
| **Fetch.ai uAgents**     | `0.12.0` | Agent framework     |
| **SingularityNET MeTTa** | Latest   | Knowledge reasoning |
| **Agentverse**           | Cloud    | Agent deployment    |
| **ASI:One**              | Latest   | Chat interface      |

### APIs & Libraries

| Library         | Purpose                |
|-----------------|------------------------|
| `aiohttp`       | Async HTTP requests    |
| `web3.py`       | Blockchain interaction |
| `hyperon`       | MeTTa runtime          |
| `pydantic`      | Data validation        |
| `python-dotenv` | Environment config     |
| `ccxt`          | Exchange data          |

### External APIs

- **CoinGecko API**: Token prices, market cap, volume
- **Alchemy/Infura**: Ethereum/Polygon RPC
- **Etherscan API**: Contract verification

---

## 📚 Documentation

### Project Documentation

> - **[README.md](README.md)** - Current file (project overview)
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Agentverse deployment guide
- **[docs/METTA_INTEGRATION.md](docs/METTA_INTEGRATION.md)** - SingularityNET MeTTa integration details
- **[LICENSE](LICENSE)** - MIT License

### Individual Agent Documentation

Each agent has detailed documentation:

- **[Portfolio Monitor](docs/agents/portfolio-monitor.md)** - Multi-chain portfolio tracking
- **[Risk Analysis Agent](docs/agents/risk-analysis.md)** - AI-powered risk assessment with MeTTa
- **[Alert System Agent](docs/agents/alert-agent.md)** - ASI:One chat interface & notifications
- **[Market Data Agent](docs/agents/market-data.md)** - Real-time price feeds & market intelligence
- **[Fraud Detection Agent](docs/agents/fraud-detection.md)** - Scam detection & honeypot identification

### MeTTa Knowledge Base

- **[metta/risk_knowledge.metta](metta/risk_knowledge.metta)** - 50+ assets, 25+ rules, comprehensive risk ontology

---

## 🔐 Security & Privacy

- ✅ **No Private Keys**: Only monitors public wallet addresses
- ✅ **Read-Only**: Cannot execute transactions
- ✅ **Decentralized**: No central database
- ✅ **Open Source**: All code auditable
- ✅ **Privacy First**: Data stays within agent network
- ✅ **Secure Communication**: Fetch.ai encrypted messaging

---

## 🎯 Use Cases

### 1. Portfolio Risk Management
- Track diversification across multiple chains
- Get alerts before major draw-downs
- Maintain healthy risk-reward ratio

### 2. Fraud Prevention
- Analyze tokens before investing
- Detect honeypots and scams early
- Identify high-risk token patterns

### 3. Market Intelligence
- Track price movements in real-time
- Identify unusual volume patterns
- Stay informed on market anomalies

### 4. Automated Rebalancing
- Get recommendations when portfolio drifts
- Maintain target allocations
- Optimize risk-adjusted returns

---

## 🤝 Contributing

Contributions are welcome! We'd love your help improving DeFiGuard.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Areas for Contribution

- 🔧 Additional blockchain integrations
- 🧠 Enhanced MeTTa knowledge rules
- 📊 New risk analysis metrics
- 🎨 UI/UX improvements
- 📚 Documentation improvements
- 🐛 Bug fixes

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **ASI Alliance** - For the hackathon opportunity and infrastructure
- **Fetch.ai** - For uAgents framework and Agentverse platform
- **SingularityNET** - For MeTTa knowledge graph technology
- **CoinGecko** - For comprehensive market data API
- **Open Source Community** - For inspiration and support

---

## 📞 Contact & Links

- **GitHub**: https://github.com/DhanteyUD/DeFiGuard
- **Demo Video**: [YouTube Link](YOUR_LINK)
- **ASI:One**: Search "DeFiGuard Alert Agent"
- **Agents Documentation**: [Full Docs](docs)
- **Issues**: [GitHub Issues](https://github.com/DhanteyUD/DeFiGuard/issues)

---

## 🏆 Built for ASI Alliance Hackathon

**DeFiGuard** showcases the power of combining:
- 🤖 **Fetch.ai's uAgents** - For autonomous agent infrastructure
- 🧠 **SingularityNET's MeTTa** - For intelligent reasoning
- 🌐 **ASI:One** - For seamless user interaction

Together, these technologies enable truly intelligent, autonomous, and explainable DeFi risk management.

---

**Built with ❤️ by [DhanteyUD](https://github.com/DhanteyUD)**

*Securing DeFi, one portfolio at a time* 🛡️

---

## 🚀 Quick Links

| Resource                | Link                                              |
|-------------------------|---------------------------------------------------|
| **Live Demo**           | [ASI:One Interface](https://asi1.ai)              |
| **Documentation**       | [docs](docs)                                      |
| **MeTTa Integration**   | [METTA_INTEGRATION.md](docs/METTA_INTEGRATION.md) |
| **Deployment Guide**    | [DEPLOYMENT.md](DEPLOYMENT.md)                    |
| **Agents README**       | [docs/agents](docs/agents)                        |
| **Fetch.ai Docs**       | https://docs.fetch.ai/                            |
| **SingularityNET Docs** | https://metta-lang.dev/                           |

---

**⭐ Star this repo if you find it useful!**
