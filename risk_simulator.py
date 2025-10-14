"""
DeFiGuard Risk Analysis Simulator
Test different risk scenarios without needing real wallet data
"""

from datetime import datetime, timezone
from typing import List, Dict
import asyncio
import json


class RiskAnalysisSimulator:
    """Simulate different portfolio risk scenarios"""

    @staticmethod
    def generate_low_risk_portfolio() -> Dict:
        """Generate a safe, diversified portfolio"""
        return {
            "user_id": "test_user_low_risk",
            "total_value_usd": 50000,
            "assets": [
                {
                    "token": "bitcoin",
                    "balance": 0.5,
                    "price": 45000,
                    "value_usd": 22500,
                    "chain": "ethereum",
                    "change_24h": 2.5
                },
                {
                    "token": "ethereum",
                    "balance": 10,
                    "price": 2500,
                    "value_usd": 25000,
                    "chain": "ethereum",
                    "change_24h": 1.8
                },
                {
                    "token": "usdc",
                    "balance": 2500,
                    "price": 1.0,
                    "value_usd": 2500,
                    "chain": "ethereum",
                    "change_24h": 0.1
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_score": 0.15
        }

    @staticmethod
    def generate_medium_risk_portfolio() -> Dict:
        """Generate a moderately risky portfolio"""
        return {
            "user_id": "test_user_medium_risk",
            "total_value_usd": 50000,
            "assets": [
                {
                    "token": "ethereum",
                    "balance": 15,
                    "price": 2500,
                    "value_usd": 37500,
                    "chain": "ethereum",
                    "change_24h": 5.2
                },
                {
                    "token": "dai",
                    "balance": 5000,
                    "price": 1.0,
                    "value_usd": 5000,
                    "chain": "ethereum",
                    "change_24h": 0.05
                },
                {
                    "token": "cardano",
                    "balance": 5000,
                    "price": 2.5,
                    "value_usd": 12500,
                    "chain": "ethereum",
                    "change_24h": -3.8
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_score": 0.45
        }

    @staticmethod
    def generate_high_risk_portfolio() -> Dict:
        """Generate a high-risk portfolio with concentration"""
        return {
            "user_id": "test_user_high_risk",
            "total_value_usd": 50000,
            "assets": [
                {
                    "token": "SafeMoon",
                    "balance": 100000000,
                    "price": 0.00025,
                    "value_usd": 25000,
                    "chain": "bsc",
                    "change_24h": -8.5
                },
                {
                    "token": "baby_ethereum",
                    "balance": 50000000,
                    "price": 0.0005,
                    "value_usd": 25000,
                    "chain": "bsc",
                    "change_24h": 12.3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_score": 0.72
        }

    @staticmethod
    def generate_critical_risk_portfolio() -> Dict:
        """Generate a critical-risk portfolio"""
        return {
            "user_id": "test_user_critical_risk",
            "total_value_usd": 50000,
            "assets": [
                {
                    "token": "elon_inu_moon",
                    "balance": 1000000000,
                    "price": 0.00005,
                    "value_usd": 50000,
                    "chain": "bsc",
                    "change_24h": 45.2
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_score": 0.92
        }

    @staticmethod
    def generate_high_volatility_portfolio() -> Dict:
        """Generate portfolio with extreme volatility"""
        return {
            "user_id": "test_user_volatility",
            "total_value_usd": 50000,
            "assets": [
                {
                    "token": "bitcoin",
                    "balance": 0.5,
                    "price": 45000,
                    "value_usd": 22500,
                    "chain": "ethereum",
                    "change_24h": -15.8
                },
                {
                    "token": "ethereum",
                    "balance": 10,
                    "price": 2500,
                    "value_usd": 25000,
                    "chain": "ethereum",
                    "change_24h": 28.5
                },
                {
                    "token": "usdc",
                    "balance": 2500,
                    "price": 1.0,
                    "value_usd": 2500,
                    "chain": "ethereum",
                    "change_24h": 0.1
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_score": 0.58
        }

    @staticmethod
    def generate_high_concentration_portfolio() -> Dict:
        """Generate portfolio with extreme concentration risk"""
        return {
            "user_id": "test_user_concentration",
            "total_value_usd": 50000,
            "assets": [
                {
                    "token": "ethereum",
                    "balance": 20,
                    "price": 2500,
                    "value_usd": 50000,
                    "chain": "ethereum",
                    "change_24h": 3.2
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_score": 0.65
        }


def print_portfolio_summary(portfolio: Dict):
    """Print a readable portfolio summary"""
    print("\n" + "="*60)
    print(f"Portfolio: {portfolio['user_id']}")
    print(f"Total Value: ${portfolio['total_value_usd']:,.2f}")
    print(f"Expected Risk Score: {portfolio['risk_score']:.2%}")
    print("="*60)
    print("\nAssets:")
    for asset in portfolio['assets']:
        pct = (asset['value_usd'] / portfolio['total_value_usd']) * 100
        print(f"  {asset['token'].upper():<20} ${asset['value_usd']:>10,.2f} ({pct:>5.1f}%) | 24h: {asset['change_24h']:>7.2f}%")
    print()


def save_test_portfolio_json(portfolio: Dict, filename: str = None) -> None:
    """Save portfolio as JSON for manual testing"""
    if filename is None:
        filename = f"test_portfolio_{portfolio['user_id']}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, indent=2)  # type: ignore[arg-type]
    print(f"✅ Saved to {filename}")


async def run_tests():
    """Run all test scenarios"""
    simulator = RiskAnalysisSimulator()

    test_scenarios = [
        ("LOW RISK", simulator.generate_low_risk_portfolio()),
        ("MEDIUM RISK", simulator.generate_medium_risk_portfolio()),
        ("HIGH RISK", simulator.generate_high_risk_portfolio()),
        ("CRITICAL RISK", simulator.generate_critical_risk_portfolio()),
        ("HIGH VOLATILITY", simulator.generate_high_volatility_portfolio()),
        ("HIGH CONCENTRATION", simulator.generate_high_concentration_portfolio()),
    ]

    print("\n" + "🧪 DeFiGuard Risk Analysis Test Scenarios" + "\n")

    for scenario_name, portfolio in test_scenarios:
        print_portfolio_summary(portfolio)
        save_test_portfolio_json(portfolio)

    # Print instructions
    print("\n" + "="*60)
    print("📋 TESTING INSTRUCTIONS")
    print("="*60)
    print("""
1. Start your Risk Analysis Agent:
   python risk_agent.py

2. Start your Alert Agent:
   python alert_agent.py

3. Use an async Python script to send test data:

   from uagents import Context
   from risk_agent import RiskAnalysisRequest
   import json

   # Load one of the test portfolios
   with open('test_portfolio_test_user_critical_risk.json') as f:
       portfolio = json.load(f)

   # Create request and send to Risk Agent
   request = RiskAnalysisRequest(
       user_id=portfolio['user_id'],
       total_value_usd=portfolio['total_value_usd'],
       assets=portfolio['assets'],
       timestamp=portfolio['timestamp'],
       risk_score=portfolio['risk_score']
   )

   # Send to your risk agent
   await ctx.send(RISK_AGENT_ADDRESS, request)

4. Monitor the logs to see:
   - MeTTa analysis results
   - Risk score calculations
   - Alerts sent to Alert Agent
   - Chat notifications to users

Test each scenario and verify:
   ✓ Correct risk levels are assigned
   ✓ Appropriate concerns are identified
   ✓ Relevant recommendations are generated
   ✓ Alerts trigger for high/critical risks
   ✓ Chat messages format correctly with emojis
""")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(run_tests())