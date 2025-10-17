# 🚀 DeFiGuard Deployment Guide

Complete guide to deploying your agents to Agentverse and enabling ASI:One integration.

## 📋 Pre-Deployment Checklist

- [ ] All agents tested locally
- [ ] API keys obtained (CoinGecko, RPC providers)
- [ ] Agentverse account created
- [ ] Code pushed to GitHub

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
   ```

5. **Paste Agent Code**
   - Copy entire content from `agentverse/portfolio_monitor_av.py`
   - Paste into agentverse code editor (it automatically saves)

6. **Add Environment Variables**
   ```
   COINGECKO_API_KEY=your_key
   ETHEREUM_RPC_URL=your_rpc
   ```

7. **Deploy Agent**
   - Click "Start Agent"
   - Wait for your code to run
   - Copy the agent address

8. **Repeat for All Agents**
   - Risk Analysis Agent
   - Alert Agent (with Chat Protocol)
   - Market Data Agent
   - Fraud Detection Agent

## Step 3: Integrate with ASI:One

### Verify Agent Discovery

1. **Open [ASI:One](https://asi1.ai)**
2. **Search for your agent**
   - Search: "DeFiGuard"
   - Or use agent address

3. **Verify Chat Interface**
   - Should show you `DeFiGuard Alert Agent`
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

...
```

## Step 4: Update GitHub Repository

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


## 🌐 Deployed Agents

All DeFiGuard agents are live on Agentverse:

- **Portfolio Monitor Agent**: `agent1qvyv...` [View](https://agentverse.ai/agents/agent1qvyvw79t54ysq7rdp5xfc9qtqkycrnvtqlwjncrqfj3v8ne3dhzfvkjmdrn)
- **Risk Analysis Agent**: `agent1q2st...` [View](https://agentverse.ai/agents/agent1q2stpgsyl2h5dlpq7sfk47hfnjqsw84kf6m40defdfph65ftje4e56l5a0f)
- **Alert Agent**: `agent1qwzs...` [View](https://agentverse.ai/agents/agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun)
- **Market Data**: `agent1qv7r...` [View](https://agentverse.ai/agents/agent1qv7r47p6r8as5kw083fr36rjw4yjn3z59pe77x2hqeu7kgfh8leas7wxux8)
- **Fraud Detection Agent**: `agent1qvyv...` [View](https://agentverse.ai/agents/agent1qvyvsyr93jp4detyrt7zy3hnvtrpu4jthy90nwv8uqpeunhywvdpgtglguc)

### Try it now on ASI:One!
Search for "DeFiGuard" in [ASI:One](https://asi1.ai/) to start monitoring your portfolio.

### Commit and Push

```bash
git add .
git commit -m "Deploy DeFiGuard to Agentverse - ASI Alliance Hackathon"
git push origin main
```

## Step 5: Final Verification

### Deployment Checklist

- [ ] All 5 agents deployed to Agentverse
- [ ] Agent addresses updated in README.md
- [ ] Chat Protocol enabled on Alert Agent
- [ ] ASI:One integration working
- [ ] Test messages sent successfully
- [ ] GitHub repository updated
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

---

**Ready to deploy? Let's go! 🚀**