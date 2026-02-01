# 🚨 DeFiGuard 2.0

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3) ![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1) ![tag:solana](https://img.shields.io/badge/solana-9945FF)

---

## 📊 Overview

AI-powered chat interface for DeFi portfolio risk monitoring. Users register portfolios, receive real-time alerts, and interact with ASI-1 AI for risk insights via natural language conversation.

**Now with full Solana blockchain support!** ◎

---

## 🎯 Agent Details

- **Agent Name**: `alert_agent`
- **Agent Address:** `agent1q2zusjcsgluu9pkkf9g2fn5lyqnaf9jqlhm3smlhvqcd6nct46ezy2qvm2l`  
- **Network:** Fetch.ai Mainnet (Agentverse)  
- **Interface:** ASI:One Chat
- **Version:** 2.0.0-solana

---

## 🎯 Core Features

✅ **Portfolio Registration** - Register EVM or Solana wallets via chat  
✅ **ASI-1 AI Integration** - Natural language Q&A about portfolio risks  
✅ **Real-Time Alerts** - Push notifications when risk escalates  
✅ **13 Chains Supported** - Solana + 12 EVM chains  
✅ **Solana Fraud Detection** - Mint authority, freeze authority, rug pull checks  
✅ **Token Analysis** - Analyze any token for fraud indicators  
✅ **Interactive Commands** - Status checks, history, portfolio view

---

## 💬 Quick Start

### Register EVM Portfolio
```
register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon,arbitrum
```

### Register Solana Portfolio ◎
```
register 9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY solana
```

### Analyze a Token (NEW)
```
analyze So11111111111111111111111111111111111111112
analyze 0xdac17f958d2ee523a2206206994597c13d831ec7
```

### Ask AI Questions
```
💬 "What's my current risk?"
💬 "How can I reduce my risk?"
💬 "What is mint authority on Solana?"
💬 "Is my Solana wallet at risk?"
```

### Use Commands
- `status` - Check current risk level
- `history` - View recent alerts (last 5)
- `portfolio` - View registered wallet(s)
- `chains` - List 13 supported chains
- `analyze <token>` - Analyze token for fraud
- `help` - Show all commands

---

## 🔗 Supported Chains (13)

### ◎ Solana (NEW)
- Full SPL token support
- Mint authority detection
- Freeze authority warnings
- Holder concentration analysis
- RugCheck API integration

### ⟠ EVM Chains (12)
ethereum, bsc, polygon, arbitrum, optimism, avalanche, base, fantom, gnosis, moonbeam, celo, cronos

---

## 🤖 ASI-1 AI Capabilities

The agent uses **ASI-1 mini** model to answer:
- Portfolio risk explanations
- DeFi risk concepts (smart contract, liquidity, volatility)
- **Solana-specific risks** (mint authority, freeze authority, rug pulls)
- Risk mitigation strategies
- Chain recommendations
- Alert interpretations
- Token analysis explanations

**Context-Aware:** AI has access to user's portfolio data, risk history, current alerts, and chain information.

---

## 📡 Message Protocol

### ➡️ Input: Alert Notification (from Risk Agent)
```json
{
  "user_id": "user_address",
  "overall_risk": "high",
  "risk_score": 0.75,
  "concerns": [
    "ETH 70% concentration",
    "◎ Solana: Mint authority active on BONK"
  ],
  "recommendations": [
    "Diversify immediately",
    "◎ Avoid tokens with active mint authority"
  ],
  "timestamp": "2025-10-16T10:35:10Z"
}
```

### ⬅️ Output: Portfolio (to Monitor Agent)
```json
{
  "user_id": "sender",
  "wallets": ["0x742d35Cc...", "9WzDXwBbmPd..."],
  "chains": ["ethereum", "polygon", "solana"],
  "wallet_type": "mixed",
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
2. ◎ Solana: Mint authority active on BONK

💡 Recommendations:
1. Diversify immediately
2. ◎ Avoid tokens with active mint authority
```

---

## 🔄 Workflow

### Registration Flow
```
User → register command
     ↓
Alert Agent detects wallet type (EVM/Solana)
     ↓
Validates address format
     ↓
Validates chain compatibility
     ↓
Saves locally + forwards to Portfolio Monitor
     ↓
Sends confirmation to user
     ↓
Portfolio Monitor starts scanning
```

### Token Analysis Flow (NEW)
```
User → analyze <token_address>
     ↓
Alert Agent detects token type (EVM/Solana)
     ↓
Forwards to Fraud Detection Agent
     ↓
Fraud Agent queries APIs:
  - Solana: RugCheck, Jupiter, Metaplex
  - EVM: GoPlus, Honeypot.is
     ↓
Returns formatted analysis to user
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
Alert Agent builds context:
  - Portfolio data
  - Chain types (Solana/EVM)
  - Recent alerts
  - Solana-specific context
     ↓
Queries ASI-1 model with enhanced system prompt
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

### EVM Wallet:
- Format: `0x` + 40 hex chars
- ERC-55 checksum validation
- Rejects zero/burn addresses

### Solana Wallet (NEW):
- Format: Base58 encoded, 32-44 chars
- Validates Base58 alphabet (no 0, O, I, l)
- Validates against known patterns

### Chain Compatibility (NEW):
- EVM wallets → EVM chains only
- Solana wallets → Solana chain only
- Automatic detection + helpful error messages

### Chains:
- Comma or space-separated
- Case-insensitive
- Max 10 chains
- Fuzzy matching for suggestions

---

## ◎ Solana-Specific Features

### Mint Authority Detection
```
⚠️ Solana: Mint authority is ACTIVE
   Risk: Token supply can be increased infinitely
   Action: Consider avoiding or limiting exposure
```

### Freeze Authority Detection
```
🔴 Solana: Freeze authority is ACTIVE
   Risk: Your tokens can be frozen by the authority
   Action: EXIT immediately - critical risk
```

### Holder Concentration Analysis
```
⚠️ Solana: Top holder owns 45% of supply
   Risk: Whale dump could crash price
   Action: Set tight stop-losses
```

### RugCheck Integration
- Real-time token safety scores
- Known scam detection
- Liquidity analysis
- Metadata verification

---

## 🔗 Agent Communication

**Receives From:**
1. Risk Analysis Agent - `AlertNotification` messages (Solana-enhanced)
2. Fraud Detection Agent - `FraudReport` messages (Solana + EVM)
3. Users via ASI:One - `ChatMessage` (text, session events)

**Sends To:**
1. Portfolio Monitor - `Portfolio` registration (with wallet_type)
2. Fraud Detection Agent - `TokenAnalysisRequest`
3. Users via ASI:One - `ChatMessage` responses
4. Risk Agent - `Acknowledgement`

**Connected Agents:**

| Agent             | Address                                                             | Purpose          |
|-------------------|---------------------------------------------------------------------|------------------|
| Portfolio Monitor | `agent1qv3pywlds6n86hr55p7lpvncwtd22d25yfe82zjg5tgx325cg9dnqylzy6f` | Wallet scanning  |
| Risk Analysis     | `agent1qtrn82fz9tnspwudzrjr7mm9ncwvavjse5xcv7j9t06gajmdxq0yg38dyx5` | Risk calculation |
| Fraud Detection   | `agent1q0x3wcul6azlcu4wy5khce9hklav28ea9f8kjqcq649rs4jat5kc7zxarn6` | Token analysis   |
| Market Data       | `agent1qgwdvuucfhpvucqdru0gnrwc2zqf0ak5u24rvxua9flcazctmdvdsyrr8qq` | Price feeds      |

---

## 🎭 Example Conversations

### New User - Solana Registration
```
User: [Opens Chat]

Agent: 👋 Welcome to DeFiGuard AI!
       
       🔗 Now supporting 13 chains:
       ◎ Solana + ⟠ 12 EVM chains
       
       Register your wallet:
       • EVM: `register 0x... ethereum,polygon`
       • Solana: `register <solana_address> solana`

User: register 9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY solana

Agent: ✅ Solana Portfolio Registered!
       
       📍 Wallet: 9WzDXwBb...NFZY
       🔗 Chain: Solana
       
       ◎ Solana-specific monitoring:
       • Mint authority detection
       • Freeze authority warnings
       • Holder concentration analysis
       • Meme coin volatility alerts
       
       💬 Ask me: "What Solana risks should I know about?"
```

### Token Analysis
```
User: analyze DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263

Agent: 🔍 Analyzing Solana Token...

       ◎ **BONK Token Analysis**
       
       ✅ Safety Score: 72/100 (MEDIUM RISK)
       
       📊 Risk Factors:
       • Mint Authority: ❌ REVOKED (Good)
       • Freeze Authority: ❌ REVOKED (Good)
       • Top 10 Holders: 35% (Medium concentration)
       • Liquidity: $45M (Healthy)
       
       ⚠️ Concerns:
       • Meme coin - high volatility expected
       • 35% holder concentration
       
       💡 Recommendation:
       Position size appropriately for high-risk asset.
```

### Solana Risk Alert
```
[Risk Agent detects Solana-specific risk]

Agent: 🔴 DeFiGuard Alert 🔴
       
       Risk Level: CRITICAL (85%)
       
       ⚠️ Concerns:
       1. ◎ Solana: Freeze authority ACTIVE on SLERF
       2. ◎ Top holder owns 52% of SLERF
       3. ◎ SLERF 65% volatility in 24h
       
       💡 Recommendations:
       1. ◎ EXIT tokens with freeze authority immediately
       2. ◎ High holder concentration = whale dump risk
       3. Consider stop-loss orders

User: What does freeze authority mean?

Agent: **Freeze Authority on Solana** ◎
       
       Freeze authority allows the token creator to "freeze" 
       any wallet holding the token. When frozen:
       
       ❌ You cannot transfer the tokens
       ❌ You cannot sell the tokens
       ❌ Your funds are effectively locked
       
       This is a CRITICAL risk because:
       • Scammers can freeze wallets after you buy
       • You have no control over your assets
       • Common in rug pull schemes
       
       **Action:** Avoid tokens with active freeze authority.
       
       Your SLERF position has this risk active. Consider exiting.
```

### Cross-Chain Portfolio
```
User: register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon

Agent: ✅ EVM Portfolio Registered!
       
       📍 Wallet: 0x742d35...f0bEb
       🔗 Chains: Ethereum, Polygon

User: Can I add my Solana wallet too?

Agent: Yes! You can register multiple wallets.
       
       Just send another register command:
       `register <your_solana_address> solana`
       
       I'll monitor both wallets and give you 
       a combined risk assessment across all chains.

User: register 9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY solana

Agent: ✅ Solana Wallet Added!
       
       📊 Your Portfolio:
       • ⟠ EVM: 0x742d35...f0bEb (ETH, Polygon)
       • ◎ Solana: 9WzDXwBb...NFZY
       
       🔗 Total Chains: 3
       ✅ Good chain diversification!
```

---

## 🛠️ Technical Stack

- **Framework:** uAgents `v0.22.10`
- **AI Model:** ASI-1 mini (via OpenAI SDK)
- **Protocol:** ASI:One Chat Protocol (chat_protocol_spec)
- **EVM Validation:** Web3.py (ERC-55 checksum)
- **Solana Validation:** Base58 pattern matching
- **Solana APIs:** RugCheck, Jupiter, Metaplex
- **EVM APIs:** GoPlus Security, Honeypot.is
- **Storage:** Agentverse ctx.storage
- **Response:** Instant (< 100ms)

---

## 🚀 Access

1. Open [ASI:One](https://asi1.ai) or [Agentverse Chat](https://chat.agentverse.ai/)
2. Search **`DeFiGuard-2.0`**
3. Start chatting!

---

## 📈 Performance

| Metric                 | Value   |
|------------------------|---------|
| Portfolio Registration | < 1s    |
| AI Response            | 2-5s    |
| Command Response       | < 100ms |
| Alert Delivery         | < 1s    |
| Token Analysis         | 2-4s    |
| Solana API Queries     | < 2s    |
| Uptime                 | 99.9%   |

---

## 🔐 Security

✅ ERC-55 checksum validation (EVM)  
✅ Base58 format validation (Solana)  
✅ Zero/burn address protection  
✅ Read-only (no transactions)  
✅ Session isolation  
✅ No private keys  
✅ Chain-wallet compatibility checks

---

## 📋 Command Reference

| Command     | Description        | Example                   |
|-------------|--------------------|---------------------------|
| `help`      | Show all commands  | `help`                    |
| `register`  | Register wallet    | `register 0x... ethereum` |
| `status`    | Current risk level | `status`                  |
| `portfolio` | View wallets       | `portfolio`               |
| `history`   | Recent alerts      | `history`                 |
| `chains`    | List chains        | `chains`                  |
| `analyze`   | Analyze token      | `analyze <token_address>` |

---

## 🆕 What's New in v2.0.0-solana

- ◎ **Solana wallet support** - Register Solana addresses
- ◎ **Mint authority detection** - Warns about unlimited supply risk
- ◎ **Freeze authority warnings** - Critical risk indicator
- ◎ **Holder concentration** - Whale dump risk analysis
- ◎ **RugCheck integration** - Real-time scam detection
- ◎ **Token analysis command** - Analyze any token
- ◎ **Solana meme coin alerts** - High volatility warnings
- 🔗 **13 chains total** - Solana + 12 EVM
- 🤖 **Enhanced AI context** - Solana-aware responses
- 📝 **Natural language parsing** - Flexible command input

---

**Powered by ASI Alliance** | **Built with ASI-1 AI** | **Real-Time Multi-Chain DeFi Monitoring**

*Updated: February 2026 | Version 2.0.0-solana*