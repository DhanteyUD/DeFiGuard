# 🚀 DeFiGuard Deployment Guide

Complete guide to deploying DeFiGuard agents to Agentverse and enabling ASI:One integration.

## 📋 Pre-Deployment Checklist

- [ ] All agents tested locally
- [ ] Agent seeds configured in `.env`
- [ ] API keys obtained (CoinGecko, RPC providers)
- [ ] Agentverse account created
- [ ] Code pushed to GitHub
- [ ] Demo video recorded

## Step 1: Prepare Agents for Agentverse

### Update Agent Configuration

Each agent needs `mailbox=True` for Agentverse deployment:

```python
agent = Agent(
    name="portfolio_monitor",
    seed=os.getenv("PORTFOLIO_AGENT_SEED"),
    mailbox=True  # Enable for Agentverse
    # Remove port and endpoint for Agentverse deployment
)
```

### Create Agentverse-Ready Files

For each agent, create a standalone file in `agentverse/` folder:

**File: `agentverse/portfolio_monitor_av.py`**

```python
# Combine all imports and code from agents/portfolio_monitor.py
# Make sure all dependencies are included
# Remove local-only features (like port binding)
```

## Step 2: Deploy to Agentverse

### Method 1: Agentverse Web UI (Recommended)

1. **Go to [Agentverse](https://agentverse.ai/)**

2. **Sign In/Sign Up**
   - Use email or Web3 wallet

3. **Create New Agent**
   - Click "Create Agent" button
   - Choose "Custom Agent"

4. **Configure Agent**
   ```
   Name: DeFiGuard Portfolio Monitor
   Description: Monitors DeFi portfolios across multiple chains
   Category: Finance
   ```

5. **Paste Agent Code**
   - Copy entire content from `agentverse/portfolio_monitor_av.py`
   - Paste into code editor
   - Click "Save"

6. **Add Environment Variables**
   ```
   PORTFOLIO_AGENT_SEED=your_seed
   COINGECKO_API_KEY=your_key
   ETHEREUM_RPC_URL=your_rpc
   ```

7. **Deploy Agent**
   - Click "Deploy"
   - Wait for deployment confirmation
   - Copy the agent address

8. **Repeat for All Agents**
   - Risk Analysis Agent
   - Alert Agent (with Chat Protocol)
   - Market Data Agent
   - Fraud Detection Agent

### Method 2: Agentverse CLI

```bash
# Install CLI
pip install agentverse-cli

# Login
agentverse login

# Deploy agent
agentverse deploy agentverse/portfolio_monitor_av.py \
  --name "DeFiGuard Portfolio Monitor" \
  --description "Monitors portfolios" \
  --env-file .env

# Deploy all agents
for agent in agentverse/*.py; do
  agentverse deploy $agent
done
```

## Step 3: Enable Chat Protocol (Alert Agent Only)

### In Agentverse UI

1. **Navigate to Alert Agent**
2. **Go to "Protocols" Tab**
3. **Enable "Chat Protocol"**
   - Toggle switch to ON
   - Confirm configuration

4. **Verify Manifest**
   ```json
   {
     "protocols": ["chat"],
     "endpoints": ["asi:one"]
   }
   ```

5. **Save Changes**

### Verify Chat Protocol

```python
# In your agent code, ensure this is included:
from uagents_core.contrib.protocols.chat import chat_protocol_spec

chat_proto = Protocol(spec=chat_protocol_spec)
agent.include(chat_proto, publish_manifest=True)
```

## Step 4: Configure Agent Network

### Update Agent Addresses

Once all agents are deployed, update `.env` with their addresses:

```.env
# Agent Addresses on Agentverse
PORTFOLIO_AGENT_ADDRESS=agent1qf8x...
RISK_AGENT_ADDRESS=agent1qz3y...
ALERT_AGENT_ADDRESS=agent1qa2b...
MARKET_AGENT_ADDRESS=agent1qm5n...
FRAUD_AGENT_ADDRESS=agent1qp7k...
```

### Update Agent Communication

Each agent needs to know other agent addresses. Update code:

```python
# In portfolio_monitor.py
risk_agent_address = os.getenv("RISK_AGENT_ADDRESS")
if risk_agent_address:
    await ctx.send(risk_agent_address, snapshot)
```

### Redeploy with Updated Addresses

After updating addresses, redeploy all agents with new configuration.

## Step 5: Test Agentverse Deployment

### Create Test Script

**File: `test_agentverse.py`**

```python
from uagents import Agent, Context
from agents.portfolio_monitor import Portfolio
from datetime import datetime
import os

test_agent = Agent(
    name="agentverse_tester",
    mailbox=True
)

PORTFOLIO_AGENT = os.getenv("PORTFOLIO_AGENT_ADDRESS")

@test_agent.on_interval(period=10.0)
async def test_portfolio(ctx: Context):
    if PORTFOLIO_AGENT:
        portfolio = Portfolio(
            user_id="test_user",
            wallets=["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"],
            chains=["ethereum"],
            timestamp=datetime.utcnow().isoformat()
        )
        await ctx.send(PORTFOLIO_AGENT, portfolio)
        ctx.logger.info("Test message sent!")

if __name__ == "__main__":
    test_agent.run()
```

Run test:
```bash
python test_agentverse.py
```

## Step 6: Integrate with ASI:One

### Verify Agent Discovery

1. **Open [ASI:One](https://asione.fetch.ai)**
2. **Search for your agent**
   - Search: "DeFiGuard"
   - Or use agent address

3. **Verify Chat Interface**
   - Should show your Alert Agent
   - Chat interface should be available

### Test Chat Commands

In ASI:One chat:
```
User: help
Agent: 🆘 DeFiGuard Help...

User: status
Agent: 📊 Current Portfolio Status...

User: history
Agent: 📜 Recent Alerts...
```

## Step 7: Update GitHub Repository

### Final Repository Structure

```
defiguard/
├── agents/
│   ├── portfolio_monitor.py
│   ├── risk_analysis.py
│   ├── alert_agent.py
│   ├── market_data.py
│   └── fraud_detection.py
├── agentverse/
│   ├── portfolio_monitor_av.py
│   ├── risk_analysis_av.py
│   ├── alert_agent_av.py
│   ├── market_data_av.py
│   └── fraud_detection_av.py
├── metta/
│   └── risk_knowledge.metta
├── tests/
│   ├── test_system.py
│   └── test_agentverse.py
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
├── main.py
└── LICENSE
```

### Update README.md

Add Agentverse deployment information:

```markdown
## 🌐 Deployed Agents

All DeFiGuard agents are live on Agentverse:

- **Portfolio Monitor**: `agent1qf8x...` [View](https://agentverse.ai/agents/agent1qf8x...)
- **Risk Analyzer**: `agent1qz3y...` [View](https://agentverse.ai/agents/agent1qz3y...)
- **Alert System**: `agent1qa2b...` [View](https://agentverse.ai/agents/agent1qa2b...)
- **Market Data**: `agent1qm5n...` [View](https://agentverse.ai/agents/agent1qm5n...)
- **Fraud Detector**: `agent1qp7k...` [View](https://agentverse.ai/agents/agent1qp7k...)

### Try it now on ASI:One!
Search for "DeFiGuard" in [ASI:One](https://asione.fetch.ai) to start monitoring your portfolio.
```

### Commit and Push

```bash
git add .
git commit -m "Deploy DeFiGuard to Agentverse - ASI Alliance Hackathon"
git push origin main
```

## Step 8: Create Demo Video

### Video Script (3-5 minutes)

**0:00-0:30 - Introduction**
- "Hi, I'm presenting DeFiGuard"
- "Multi-agent risk management system for DeFi"
- Show logo/banner

**0:30-1:30 - Problem & Solution**
- Problem: DeFi users lose money to scams and poor risk management
- Solution: Autonomous agents that monitor 24/7
- Show architecture diagram

**1:30-3:00 - Live Demo**
- Open ASI:One interface
- Chat with Alert Agent
- Show: `status`, `history`, `help` commands
- Demonstrate risk alert
- Show agent communication in Agentverse logs

**3:00-4:00 - Technical Highlights**
- uAgents Framework usage
- MeTTa Knowledge Graph integration
- Multi-agent collaboration
- Cross-chain support

**4:00-4:30 - Impact & Future**
- Real-world impact: Prevent losses
- Future features: More chains, ML improvements
- Call to action: Try on ASI:One

**4:30-5:00 - Closing**
- GitHub repository
- Thank ASI Alliance
- Contact information

### Recording Tools

- **OBS Studio** (Free, professional)
- **Loom** (Easy, browser-based)
- **Screen Recording** (Mac/Windows built-in)

### Upload Video

1. Upload to YouTube/Vimeo
2. Add to README.md
3. Include in hackathon submission

## Step 9: Final Verification

### Deployment Checklist

- [ ] All 5 agents deployed to Agentverse
- [ ] Agent addresses updated in README.md
- [ ] Chat Protocol enabled on Alert Agent
- [ ] ASI:One integration working
- [ ] Test messages sent successfully
- [ ] GitHub repository updated
- [ ] Innovation Lab badge added
- [ ] Demo video recorded and uploaded
- [ ] All documentation complete

### Test End-to-End Flow

1. **Send portfolio registration** → Portfolio Monitor
2. **Verify risk analysis** → Risk Agent processes
3. **Check alert generation** → Alert Agent notifies
4. **Test ASI:One chat** → Commands work
5. **Verify fraud detection** → Scam detection works

## 🎉 Deployment Complete!

Your DeFiGuard system is now live on Agentverse and accessible via ASI:One!

### Next Steps

1. **Monitor Logs**: Check Agentverse for any errors
2. **Gather Feedback**: Share with community
3. **Iterate**: Improve based on usage
4. **Submit**: Complete hackathon submission form

## 🆘 Troubleshooting

### Agent Not Responding

- Check Agentverse logs for errors
- Verify environment variables
- Ensure agent addresses are correct
- Check API rate limits

### Chat Protocol Not Working

- Verify `publish_manifest=True`
- Check chat protocol inclusion
- Redeploy agent
- Clear ASI:One cache

### Message Not Received

- Verify recipient address
- Check network connectivity
- Review Agentverse message logs
- Ensure both agents are running

## 📞 Support

- **Agentverse Docs**: https://docs.fetch.ai/
- **Discord**: Fetch.ai Community
- **GitHub Issues**: Your repository

---

**Ready to deploy? Let's go! 🚀**