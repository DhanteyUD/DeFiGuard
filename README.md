# 🛡️ DeFiGuard: Multi-Agent Risk Management System

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1) ![Python](https://img.shields.io/badge/python-3.12-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg) ![GitHub repo size](https://img.shields.io/github/repo-size/DhanteyUD/DeFiGuard) ![GitHub last commit](https://img.shields.io/github/last-commit/DhanteyUD/DeFiGuard)

**AI-powered, multi-chain DeFi portfolio risk monitoring with autonomous agents**

Monitor crypto portfolios across 12 chains, analyze risks using SingularityNET MeTTa AI, detect fraud, and receive real-time alerts via ASI:One chat.

---

## 📋 Table of Contents

- [Demo Video](#-demo-video)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Agents Overview](#-agents-overview)
- [Agent Addresses](#-agent-addresses)
- [Quick Start](#-quick-start)
- [Using DeFiGuard](#-using-defiguard)
- [Risk Scoring Methodology](#-risk-scoring-methodology)
- [Technologies Used](#-technologies-used)
- [Documentation](#-documentation)
- [Testing](#-testing)
- [Security](#-security)
- [Contributing](#-contributing)
- [Acknowledgments](#-acknowledgments)
- [Contact](#-contact)
- [License](#-license)


---

## 🎥 Demo Video

[▶️ Watch Demo (3-5 minutes)](YOUR_YOUTUBE_LINK_HERE)

---

## ✨ Key Features

**🔍 Multi-Chain Monitoring** - Track portfolios across 12 EVM chains (Ethereum, BSC, Polygon, Arbitrum, Optimism, Avalanche, Base, Fantom, Gnosis, Moonbeam, Celo, Cronos)

**🧠 AI Risk Analysis** - SingularityNET MeTTa knowledge graphs with 50+ assets, 25+ risk rules, explainable decisions

**💬 Natural Chat Interface** - ASI:One integration with ASI-1 AI for conversational portfolio management

**🚨 Real-Time Alerts** - Instant notifications on risk escalation (Low → Critical)

**🕵️ Fraud Detection** - Honeypot detection, high tax identification, scam pattern matching via GoPlus Security API

**📊 Market Intelligence** - CoinGecko API integration with price change detection, volume spike identification

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

## 🤖 Agents Overview

### 1. Alert Agent (Chat Interface)
**Address**: `agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l`

**Capabilities:**
- ASI:One chat interface with ASI-1 AI
- Portfolio registration forwarding
- Real-time alert delivery
- Natural language Q&A
- Commands: `register`, `status`, `history`, `portfolio`, `chains`, `help`

**Tech**: ASI:One Chat Protocol, ASI-1 mini model, React state (no localStorage)

📄 [Doc](docs/agents/alert-agent.md)

### 2. Portfolio Monitor Agent
**Address**: `agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f`

**Capabilities:**
- 12-chain multi-wallet tracking
- Native token balance monitoring
- 10-minute scan cycles (round-robin)
- ERC-55 checksum validation
- CoinGecko price integration (60s cache)

**Limitations**: 1 wallet/cycle, max 3 chains/scan, native tokens only

📄 [Doc](docs/agents/portfolio-monitor.md)

### 3. Risk Analysis Agent (MeTTa-Powered)
**Address**: `agent1qtrn82fz9tnspwudzrjr7mm9ncwvavjse5xcv7j9t06gajmdxq0yg38dyx5`

**Capabilities:**
- SingularityNET MeTTa knowledge graph reasoning
- Multi-factor risk scoring (concentration 35%, volatility 45%, chain diversity 20%)
- Pattern matching for complex risk scenarios
- Explainable AI decisions (traceable to knowledge base)
- 5-level classification (Safe → Critical)

**Tech**: MeTTa v0.1.0, 50+ asset classifications, 25+ risk rules

📄 [Doc](docs/agents/risk-analysis.md) | [MeTTa Integration](docs/METTA_INTEGRATION.md)

### 4. Market Data Agent
**Address**: `agent1qgwdvuucfhpvucqdru0gnrwc2zqf0ak5u24rvxua9flcazctmdvdsyrr8qq`

**Capabilities:**
- CoinGecko API integration (10,000+ tokens)
- 5-minute price caching
- Volume spike detection
- Market cap tracking
- Anomaly alerts (>10% price change, >50% volume)

**Tech**: CoinGecko API v3, 5-min TTL cache, aiohttp

📄 [Doc](docs/agents/market-data.md)

### 5. Fraud Detection Agent
**Address**: `agent1q0x3wcul6azlcu4wy5khce9hklav28ea9f8kjqcq649rs4jat5kc7zxarn6`

**Capabilities:**
- GoPlus Security API integration
- Honeypot detection (cannot sell)
- High tax identification (>10%)
- Ownership analysis (renounced check)
- 20+ security checks with weighted scoring
- Risk classification (Safe → Critical)

**Tech**: GoPlus API, Honeypot.is API, 12 blockchain explorers

📄 [Doc](docs/agents/fraud-detection.md)

---

## 🔗 Agent Addresses

### Deployment Architecture

#### **🐳 Docker Container (Railway Hosting)** 
> All 5 agents run together in a single Docker container using Fetch.ai's Bureau framework, enabling efficient inter-agent communication and resource management.

**☁️ Agentverse Registration**
> Only the Alert Agent is registered on Agentverse to serve as the public-facing interface for ASI:One chat interactions.

| Agent             | Address/Status                                                      | Deployment             |
|-------------------|---------------------------------------------------------------------|------------------------|
| Alert Agent       | `agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l` | ✅ Agentverse + Railway |
| Portfolio Monitor | Internal (Bureau)                                                   | 🐳 Railway Container   |
| Risk Analysis     | Internal (Bureau)                                                   | 🐳 Railway Container   |
| Market Data       | Internal (Bureau)                                                   | 🐳 Railway Container   |
| Fraud Detection   | Internal (Bureau)                                                   | 🐳 Railway Container   |

**💡 Architecture Benefits:**
- **Unified Deployment**: Single container simplifies DevOps and reduces hosting costs
- **Low Latency**: Internal Bureau messaging eliminates network overhead between agents
- **Single Entry Point**: Alert Agent handles all external communication via Agentverse
- **Scalability**: Railway auto-scaling manages all agents together

**🔌 How to Connect:**
Users interact only with the Alert Agent address through ASI:One or Agentverse Chat. The Alert Agent coordinates with all internal agents automatically.

#### Agentverse Cloud
> Each agent hosted independently on Agentverse and communicate via the Fetch.ai network.

| Agent             | Address                                                             | Status          |
|-------------------|---------------------------------------------------------------------|-----------------|
| Portfolio Monitor | `agent1qvyvw79t54ysq7rdp5xfc9qtqkycrnvtqlwjncrqfj3v8ne3dhzfvkjmdrn` | ✅ Active        |
| Risk Analysis     | `agent1q2stpgsyl2h5dlpq7sfk47hfnjqsw84kf6m40defdfph65ftje4e56l5a0f` | ✅ Active        |
| Alert Agent       | `agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun` | ✅ Active + Chat |
| Market Data       | `agent1qv7r47p6r8as5kw083fr36rjw4yjn3z59pe77x2hqeu7kgfh8leas7wxux8` | ✅ Active        |
| Fraud Detection   | `agent1qvyvsyr93jp4detyrt7zy3hnvtrpu4jthy90nwv8uqpeunhywvdpgtglguc` | ✅ Active        |

**💡 Independent Deployment Benefits:**
- **Distributed Architecture**: Each agent runs in isolated Agentverse environments
- **Network Communication**: Agents discover and message each other via Fetch.ai Almanac
- **Individual Scaling**: Each agent can be updated/restarted independently
- **No Single Point of Failure**: Redundancy through distributed hosting

---

**🔌 How to Connect:**
Regardless of deployment mode, users interact only with the Alert Agent address (`agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l`) through ASI:One or Agentverse Chat. The Alert Agent coordinates with all other agents automatically.

---

## 🚀 Quick Start

### Prerequisites
```bash
python --version  # 3.10+
git --version
```

### Installation
```bash
# Clone & setup
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

# Configure (copy & edit .env)
cp .env.example .env

# Add your AGENT_SEEDS and optional API keys

# Verify MeTTa
python verify_metta.py

# Run all agents
python main.py
```

---

## 📱 Using DeFiGuard

### Via ASI:One Chat (Recommended)

1. Open [ASI:One](https://asi1.ai) or [Agentverse Chat](https://chat.agentverse.ai/)
2. **Search for Agent**: `DeFiGuard Alert Agent` or address `agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l`
3. **Start Chatting**:

```
User: register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon

Agent: ✅ Portfolio Registered!
       Wallet: 0x742d35Cc...5f0bEb
       Monitoring 2 chain(s): Ethereum, Polygon
       💬 Ask me: "What's my current risk?"

User: What's my current risk?

Agent: I'm analyzing your portfolio with MeTTa AI...
       
       Current Risk: 🟡 MEDIUM (45%)
       
       Your portfolio shows moderate concentration risk...

User: status

Agent: 📊 Portfolio Status
       🟡 Risk Level: MEDIUM
       Risk Score: 45%
       Updated: Oct 16, 2025 10:35 AM
```

**Commands**: `register`, `status`, `history`, `portfolio`, `chains`, `help`

### Programmatic Usage

```python
from uagents import Agent, Context, Model
from datetime import datetime, timezone

class Portfolio(Model):
    user_id: str
    wallets: list[str]
    chains: list[str]
    timestamp: str

client = Agent(name="my_client", mailbox=True)

@client.on_event("startup")
async def register_portfolio(ctx: Context):
    portfolio = Portfolio(
        user_id="my_portfolio",
        wallets=["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"],
        chains=["ethereum", "polygon"],
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    await ctx.send(
        "agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f",
        portfolio
    )

if __name__ == "__main__":
    client.run()
```

---

## 📊 Risk Scoring Methodology

### Formula
```
Risk Score = (Concentration × 0.35) + (Volatility × 0.45) + (Chain Diversity × 0.20)
```

### Risk Levels

| Level    | Score   | Emoji | Action               |
|----------|---------|-------|----------------------|
| Low      | 0-30%   | 🟢    | Monitor              |
| Medium   | 30-50%  | 🟡    | Review weekly        |
| High     | 50-70%  | 🟠    | Rebalance within 24h |
| Critical | 70-100% | 🔴    | Review immediately   |

### MeTTa Knowledge Base

All thresholds defined declaratively:

```metta
; Asset classifications
(has-risk bitcoin low)
(has-risk ethereum low)
(has-risk-pattern leverage critical)

; Thresholds
(concentration-threshold critical 0.70)
(volatility-threshold extreme 50)
```

**Benefits**: Explainable, extensible, maintainable by domain experts

---

## 🛠️ Technologies Used

| Component           | Technology                     |
|---------------------|--------------------------------|
| **Agent Framework** | Fetch.ai uAgents `v0.22.10`    |
| **AI Reasoning**    | SingularityNET MeTTa           |
| **Chat Interface**  | ASI:One Chat Protocol, ASI-1   |
| **Deployment**      | Agentverse Cloud               |
| **Blockchain**      | Web3.py `v7.13`                |
| **APIs**            | CoinGecko, GoPlus, Honeypot.is |
| **Language**        | Python `3.12`                  |

---

## 📚 Documentation

- **[README.md](README.md)** - Project overview
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Agentverse deployment
- **[docs/METTA_INTEGRATION.md](docs/METTA_INTEGRATION.md)** - MeTTa AI details

**Agent Docs:**
- [Alert Agent](docs/agents/alert-agent.md)
- [Portfolio Monitor](docs/agents/portfolio-monitor.md)
- [Risk Analysis](docs/agents/risk-analysis.md)
- [Market Data](docs/agents/market-data.md)
- [Fraud Detection](docs/agents/fraud-detection.md)

**Knowledge Base:**
- [metta/risk_knowledge.metta](metta/risk_knowledge.metta)

---

## 🧪 Testing

```bash
# Terminal 1: Start agents
python local.py

# Terminal 2: Run tests
python tests/test_system.py

# Verify MeTTa
python verify_metta.py
```

---

## 🔐 Security

- ✅ No private keys (read-only monitoring)
- ✅ ERC-55 checksum validation
- ✅ Zero/burn address protection
- ✅ Secure agent messaging (Fetch.ai)
- ✅ Open source & auditable

---

## 🤝 Contributing

1. Fork repo
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Open Pull Request

**Areas**: Blockchain integrations, MeTTa rules, risk metrics, UI/UX, docs, bug fixes

---

## 🙏 Acknowledgments

- **ASI Alliance** - Hackathon & infrastructure
- **Fetch.ai** - uAgents & Agentverse
- **SingularityNET** - MeTTa AI technology
- **CoinGecko** - Market data API
- **GoPlus Security** - Fraud detection API

---

## 📞 Contact

- **GitHub**: https://github.com/DhanteyUD/DeFiGuard
- **Demo Video**: [YouTube Link](YOUR_LINK)
- **ASI:One**: Search **`DeFiGuard Alert Agent`**
- **Issues**: [GitHub Issues](https://github.com/DhanteyUD/DeFiGuard/issues)

---

## 📄 License

MIT License - Open Source

---

**Built with ❤️ by [DhanteyUD](https://github.com/DhanteyUD)**

*Securing DeFi, one portfolio at a time* 🛡️

**⭐ Star this repo if you find it useful!**

---

**Powered by ASI Alliance** | **Fetch.ai uAgents** | **SingularityNET MeTTa** | **ASI:One**