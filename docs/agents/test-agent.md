# DeFiGuard Risk Test Agent

A testing agent for the DeFiGuard risk analysis system that simulates portfolio data and validates the complete risk analysis pipeline on Agentverse.

## Overview

The Test Agent automatically generates and sends simulated portfolio scenarios to your Risk Analysis Agent, allowing you to validate:

- Risk scoring calculations
- MeTTa knowledge graph integration
- Alert triggering logic
- Asset classification accuracy
- Concentration and volatility analysis

## Quick Start

### 1. Get Your Agent Addresses

Deploy your agents to Agentverse and note their addresses:
- Risk Analysis Agent address
- Alert Agent address (optional, for receiving critical alerts)

### 2. Update Configuration

In `test_agent_av.py`, replace the placeholder addresses:

```python
RISK_AGENT_ADDRESS = "agent1qwwc3jwx0x6z0sk07029n9ngztsrapcc0ngdwy8swzq50tt7t0nf726tmkm"
ALERT_AGENT_ADDRESS = "agent1qftjr2fh4uuk0se60sp6e6yevamtlmh5tlsjxx9ny2kgenggf089unxed9f"
```

### 3. Deploy to Agentverse

Upload `test_agent.py` to Agentverse and run it.

## Test Scenarios

The test agent cycles through 6 different portfolio scenarios every 10 seconds:

### 1. Low Risk Portfolio
**Expected Risk Level:** Low (0-30%)

- Diversified across Bitcoin, Ethereum, and USDC
- Minimal volatility (0-2.5% 24h change)
- No concentration risk
- All stable/blue-chip assets

**MeTTa Evaluation:** All assets classified as "low" risk

```
Total Value: $50,000
- Bitcoin: $22,500 (45%)
- Ethereum: $25,000 (50%)
- USDC: $2,500 (5%)
```

### 2. Medium Risk Portfolio
**Expected Risk Level:** Medium (30-50%)

- Concentrated in Ethereum with some altcoins
- Moderate volatility (3-5% 24h change)
- Diversification present but unbalanced

**MeTTa Evaluation:** Mixed asset quality, elevated volatility

```
Total Value: $50,000
- Ethereum: $37,500 (75%)
- DAI: $5,000 (10%)
- Cardano: $12,500 (25%)
```

### 3. High Risk Portfolio
**Expected Risk Level:** High (50-70%)

- Concentrated in suspicious meme coins
- Extreme volatility (-8.5% to +12.3%)
- Contains keywords that trigger fraud detection

**MeTTa Evaluation:** "SafeMoon" and "baby" keywords detected as high-risk patterns

```
Total Value: $50,000
- SafeMoon: $25,000 (50%)
- baby_ethereum: $25,000 (50%)
```

### 4. Critical Risk Portfolio
**Expected Risk Level:** Critical (70-100%)

- 100% allocated to a single suspicious token
- Extreme volatility (+45.2% 24h)
- Matches multiple fraud indicators

**MeTTa Evaluation:** "elon_inu_moon" triggers critical keywords ("elon", "inu", "moon")

```
Total Value: $50,000
- elon_inu_moon: $50,000 (100%)
```

### 5. High Volatility Portfolio
**Expected Risk Level:** Medium-High (40-60%)

- Diverse assets but with extreme price swings
- Bitcoin down 15.8%, Ethereum up 28.5%
- Tests volatility scoring independent of concentration

**MeTTa Evaluation:** High volatility threshold triggers, but diversity reduces overall risk

```
Total Value: $50,000
- Bitcoin: $22,500 (45%) - 24h: -15.8%
- Ethereum: $25,000 (50%) - 24h: +28.5%
- USDC: $2,500 (5%) - 24h: +0.1%
```

### 6. High Concentration Portfolio
**Expected Risk Level:** Medium-High (50-70%)

- 100% in single stable asset (Ethereum)
- Minimal volatility but maximum concentration risk
- Tests concentration scoring independently

**MeTTa Evaluation:** Concentration threshold exceeded, single point of failure

```
Total Value: $50,000
- Ethereum: $50,000 (100%)
```

## Monitoring Results

### View Logs on Agentverse

1. Navigate to your Risk Analysis Agent's detail page
2. Open the logs section
3. Watch for analysis results

### Expected Log Output

**For Low Risk Portfolio:**
```
🧠 Analyzing risk with MeTTa for user: test_user_low_risk
✅ MeTTa risk analysis complete: low (score: 0.15)
Recommendations:
  - ✅ MeTTa Analysis: Portfolio risk is acceptable - continue monitoring
  - 🧠 MeTTa Analysis: Always conduct your own research (DYOR)
```

**For Critical Risk Portfolio:**
```
🧠 Analyzing risk with MeTTa for user: test_user_critical_risk
🧠 MeTTa: elon_inu_moon risk = critical
✅ MeTTa risk analysis complete: critical (score: 0.92)
Recommendations:
  - ⚠️ URGENT: MeTTa knowledge graph detected critical risk - review immediately
  - ⚠️ DO NOT INVEST - Critical fraud indicators detected
```

## What Gets Tested

### Risk Scoring
- Concentration index calculation
- Volatility percentage conversion
- Asset quality weighting
- Combined risk score (0-1 range)

### MeTTa Knowledge Graph
- Asset keyword detection (bitcoin, ethereum, safemoon, etc.)
- Risk pattern matching (leverage, fork, clone, etc.)
- Suspicious token name analysis
- Risk threshold evaluation

### Alert Generation
- Risk level assignment (low → medium → high → critical)
- Alert triggering on risk_score > 0.7
- Critical risk detection and notification

### Recommendation Generation
- Dynamic recommendations based on risk level
- Specific concerns addressed
- Action items prioritized by urgency

## Integration Points

### Risk Analysis Agent
Receives: `RiskAnalysisRequest` with simulated portfolio data
Returns: `RiskReport` with analysis results

### Alert Agent (Optional)
Receives alerts when:
- Risk level is "high" or "critical"
- Risk score exceeds 0.7 threshold
- MeTTa detects fraud indicators

## Configuration Options

### Adjust Test Frequency

Change the interval period in milliseconds:
```python
@test_agent.on_interval(period=10.0)  # Currently 10 seconds
```

Increase to 30 or 60 seconds for less frequent testing.

### Modify Test Scenarios

Edit portfolio creation functions to test custom scenarios:

```python
def create_custom_portfolio() -> RiskAnalysisRequest:
    return RiskAnalysisRequest(
        user_id="test_custom",
        total_value_usd=100000,
        assets=[
            {"token": "your_token", "balance": 100, "price": 1000, 
             "value_usd": 100000, "chain": "ethereum", "change_24h": 5.0},
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=0.5
    )
```

### Disable Specific Tests

Comment out scenarios in `send_test_portfolios()`:
```python
test_portfolios = [
    create_low_risk_portfolio(),
    # create_medium_risk_portfolio(),  # Disabled
    create_high_risk_portfolio(),
]
```

## Troubleshooting

### Agent Not Receiving Data

1. Verify Risk Agent address is correct
2. Ensure Risk Agent is running on Agentverse
3. Check agent logs for connection errors
4. Confirm both agents are on the same network

### Risk Scores Not Matching Expected Values

1. Verify asset data matches portfolio definitions
2. Check MeTTa knowledge base is loaded
3. Review risk calculation weights in Risk Agent
4. Validate timestamp format is ISO 8601

### No Alerts Generated

1. Check alert_agent_address is correctly set
2. Verify risk score exceeds 0.7 threshold
3. Confirm Alert Agent is deployed and running
4. Review Alert Agent logs for received messages

## Best Practices

1. **Run tests periodically** - Test after any changes to risk calculation logic
2. **Monitor all agents** - Keep logs open for all three agents during testing
3. **Validate incrementally** - Test each scenario individually before running full suite
4. **Document results** - Note risk scores for each scenario for regression testing
5. **Scale gradually** - Start with one scenario, then run full test suite

## Performance Considerations

- Test agent sends data every 10 seconds
- Each scenario completes in 1-3 seconds on Agentverse
- Total cycle time: approximately 1 minute for all 6 scenarios
- Adjust interval if your Risk Agent needs more processing time

## Next Steps

After validating with the test agent:

1. Connect real wallet data via Portfolio Monitor Agent
2. Integrate with actual market data feeds
3. Set up user alerts via chat protocol
4. Deploy to production with real portfolios

## Support

For issues or questions:
1. Check agent logs on Agentverse
2. Review Risk Analysis Agent MeTTa output
3. Verify all agent addresses are correctly configured
4. Ensure agents have proper mailbox settings enabled