# 🚨 DeFiGuard Alert Agent

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

---

## 📊 Overview

AI-powered chat interface for DeFi portfolio risk monitoring. Users register portfolios, receive real-time alerts, and interact with ASI-1 AI for risk insights via natural language conversation.

---

## 🎯 Agent Details

- **Agent Name**: `alert_agent`
- **Agent Address:** `agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l`  
- **Network:** Fetch.ai Testnet (Agentverse)  
- **Interface:** ASI:One Chat

---

## 🎯 Core Features

✅ **Portfolio Registration** - Register wallets via chat, forwarded to Portfolio Monitor  
✅ **ASI-1 AI Integration** - Natural language Q&A about portfolio risks  
✅ **Real-Time Alerts** - Push notifications when risk escalates  
✅ **12 EVM Chains** - Multi-chain monitoring support  
✅ **Interactive Commands** - Status checks, history, portfolio view

---

## 💬 Quick Start

### Register Portfolio
```
register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon,arbitrum
```

### Ask AI Questions
```
💬 "What's my current risk?"
💬 "How can I reduce my risk?"
💬 "Explain smart contract risk"
```

### Use Commands
- `status` - Check current risk
- `history` - View recent alerts (last 5)
- `portfolio` - View registered wallet(s)
- `chains` - List 12 supported chains
- `help` - Show commands

---

## 🔗 Supported Chains (12)

ethereum, bsc, polygon, arbitrum, optimism, avalanche, base, fantom, gnosis, moonbeam, celo, cronos

---

## 🤖 ASI-1 AI Capabilities

The agent uses **ASI-1 mini** model to answer:
- Portfolio risk explanations
- DeFi risk concepts (smart contract, liquidity, volatility)
- Risk mitigation strategies
- Chain recommendations
- Alert interpretations

**Context-Aware:** AI has access to user's portfolio data, risk history, and current alerts.

---

## 📡 Message Protocol

### ➡️ Input: Alert Notification (from Risk Agent)
```json
{
  "user_id": "user_address",
  "overall_risk": "high",
  "risk_score": 0.75,
  "concerns": ["ETH 70% concentration"],
  "recommendations": ["Diversify immediately"],
  "timestamp": "2025-10-16T10:35:10Z"
}
```

### ⬅️ Output: Portfolio (to Monitor Agent)
```json
{
  "user_id": "sender",
  "wallets": ["0x742d35Cc..."],
  "chains": ["ethereum", "polygon"],
  "timestamp": "2025-10-16T10:35:10Z"
}
```

### ↖️ Output: ChatMessage (to User)
```
🟠 DeFiGuard Alert 🟠

Risk Level: HIGH
Risk Score: 75%
Time: Oct 16, 2025 10:35

⚠️ Concerns:
1. ETH 70% concentration

💡 Recommendations:
1. Diversify immediately
```

---

## 🔄 Workflow

### Registration Flow
```
User → register command
     ↓
Alert Agent validates (ERC-55 checksum)
     ↓
Saves locally + forwards to Portfolio Monitor
     ↓
Sends confirmation to user
     ↓
Portfolio Monitor starts scanning
```

### Alert Flow
```
Risk Agent → AlertNotification
          ↓
Alert Agent stores + formats
          ↓
Checks active session
          ↓
Sends via chat if active (or stores)
```

### AI Chat Flow
```
User → Natural language question
     ↓
Alert Agent builds context (portfolio + alerts)
     ↓
Queries ASI-1 model with system prompt
     ↓
Returns AI-generated response
```

---

## 🎨 Risk Levels

| Level    | Emoji | Range   | Action        |
|----------|-------|---------|---------------|
| LOW      | 🟢    | 0-30%   | Monitor       |
| MEDIUM   | 🟡    | 30-50%  | Review weekly |
| HIGH     | 🟠    | 50-70%  | Rebalance 24h |
| CRITICAL | 🔴    | 70-100% | Urgent        |

---

## ✅ Validation Rules

**Wallet:**
- Format: `0x` + 40 hex chars
- ERC-55 checksum validation
- Rejects zero/burn addresses

**Chains:**
- Comma or space-separated
- Case-insensitive
- Max 10 chains
- Fuzzy matching for suggestions

---

## 🔗 Agent Communication

**Receives From:**
1. Risk Analysis Agent - `AlertNotification` messages
2. Users via ASI:One - `ChatMessage` (text, session events)

**Sends To:**
1. Portfolio Monitor - `Portfolio` registration
2. Users via ASI:One - `ChatMessage` responses
3. Risk Agent - `Acknowledgement`

**Portfolio Monitor Address:**  
`agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f`

---

## 🎭 Example Conversations

### New User + AI
```
User: [Opens Chat]

Agent: 👋 Welcome to DeFiGuard AI!
       Ask me anything or register:
       `register <wallet> ethereum,polygon`

User: register 0x742d35Cc...5f0bEb ethereum,polygon

Agent: ✅ Portfolio Registered!
       💬 Ask me: "What should I know about my risk?"

User: What risks do you monitor?

Agent: I monitor three main risk categories:
       1. Concentration Risk (35%) - Asset diversification
       2. Volatility Risk (45%) - Price fluctuations
       3. Chain Diversity (20%) - Multi-chain exposure
       
       Your portfolio is analyzed every 10 minutes...
```

### High Risk Alert
```
[Risk Agent detects high risk]

Agent: 🟠 DeFiGuard Alert 🟠
       Risk Level: HIGH (75%)
       
       ⚠️ ETH 70% concentration
       💡 Diversify immediately

User: Why is concentration bad?

Agent: High concentration means most of your value is in one asset.
       If ETH drops 20%, your portfolio drops ~14% (70% × 20%).
       
       Diversifying across 3-5 assets reduces single-asset risk...
```

---

## 🛠️ Technical Stack

- **Framework:** uAgents v0.22.10
- **AI Model:** ASI-1 mini (via OpenAI SDK)
- **Protocol:** ASI:One Chat Protocol
- **Validation:** Web3.py (ERC-55 checksum)
- **Storage:** Agentverse ctx.storage
- **Response:** Instant (< 100ms)

---

## 🚀 Access

1. Open [ASI:One](https://asi1.ai) or [Agentverse Chat](https://chat.agentverse.ai/)
2. Search **`DeFiGuard Alert Agent`**
3. Start chatting!

---

## 📈 Performance

- Portfolio Registration: < 1s
- AI Response: 2-5s
- Command Response: < 100ms
- Alert Delivery: < 1s
- Uptime: 99.9%

---

## 🔐 Security

✅ ERC-55 checksum validation  
✅ Zero/burn address protection  
✅ Read-only (no transactions)  
✅ Session isolation  
✅ No private keys

---

**Powered by ASI Alliance** | **Built with ASI-1 AI** | **Real-Time DeFi Monitoring**

*Updated: October 2025*