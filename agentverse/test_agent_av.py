from uagents import Agent, Context, Model
from datetime import datetime, timezone
from typing import List, Dict


class RiskAnalysisRequest(Model):
    user_id: str
    total_value_usd: float
    assets: List[Dict]
    timestamp: str
    risk_score: float


class RiskReport(Model):
    user_id: str
    overall_risk: str
    risk_score: float
    concerns: List[str]
    recommendations: List[str]
    timestamp: str
    should_alert: bool


test_agent = Agent(
    name="risk_test_agent",
    mailbox=True,
    seed="risk_test_agent_seed_12345"
)

print(f"Test Agent Address: {test_agent.address}")

RISK_AGENT_ADDRESS = "agent1q2stpgsyl2h5dlpq7sfk47hfnjqsw84kf6m40defdfph65ftje4e56l5a0f"
ALERT_AGENT_ADDRESS = "agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun"


def create_low_risk_portfolio() -> RiskAnalysisRequest:
    """Create a safe, diversified portfolio"""

    return RiskAnalysisRequest(
        user_id="test_user_low_risk",
        total_value_usd=50000,
        assets=[
            {"token": "bitcoin", "balance": 0.5, "price": 45000, "value_usd": 22500, "chain": "ethereum",
             "change_24h": 2.5},
            {"token": "ethereum", "balance": 10, "price": 2500, "value_usd": 25000, "chain": "ethereum",
             "change_24h": 1.8},
            {"token": "usdc", "balance": 2500, "price": 1.0, "value_usd": 2500, "chain": "ethereum", "change_24h": 0.1},
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=0.15
    )


def create_medium_risk_portfolio() -> RiskAnalysisRequest:
    """Create a moderately risky portfolio"""

    return RiskAnalysisRequest(
        user_id="test_user_medium_risk",
        total_value_usd=50000,
        assets=[
            {"token": "ethereum", "balance": 15, "price": 2500, "value_usd": 37500, "chain": "ethereum",
             "change_24h": 5.2},
            {"token": "dai", "balance": 5000, "price": 1.0, "value_usd": 5000, "chain": "ethereum", "change_24h": 0.05},
            {"token": "cardano", "balance": 5000, "price": 2.5, "value_usd": 12500, "chain": "ethereum",
             "change_24h": -3.8},
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=0.45
    )


def create_high_risk_portfolio() -> RiskAnalysisRequest:
    """Create a high-risk portfolio with concentration"""

    return RiskAnalysisRequest(
        user_id="test_user_high_risk",
        total_value_usd=50000,
        assets=[
            {"token": "SafeMoon", "balance": 100000000, "price": 0.00025, "value_usd": 25000, "chain": "bsc",
             "change_24h": -8.5},
            {"token": "baby_ethereum", "balance": 50000000, "price": 0.0005, "value_usd": 25000, "chain": "bsc",
             "change_24h": 12.3},
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=0.72
    )


def create_critical_risk_portfolio() -> RiskAnalysisRequest:
    """Create a critical-risk portfolio"""

    return RiskAnalysisRequest(
        user_id="test_user_critical_risk",
        total_value_usd=50000,
        assets=[
            {"token": "elon_inu_moon", "balance": 1000000000, "price": 0.00005, "value_usd": 50000, "chain": "bsc",
             "change_24h": 45.2},
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=0.92
    )


def create_high_volatility_portfolio() -> RiskAnalysisRequest:
    """Create portfolio with extreme volatility"""

    return RiskAnalysisRequest(
        user_id="test_user_volatility",
        total_value_usd=50000,
        assets=[
            {"token": "bitcoin", "balance": 0.5, "price": 45000, "value_usd": 22500, "chain": "ethereum",
             "change_24h": -15.8},
            {"token": "ethereum", "balance": 10, "price": 2500, "value_usd": 25000, "chain": "ethereum",
             "change_24h": 28.5},
            {"token": "usdc", "balance": 2500, "price": 1.0, "value_usd": 2500, "chain": "ethereum", "change_24h": 0.1},
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=0.58
    )


def create_high_concentration_portfolio() -> RiskAnalysisRequest:
    """Create portfolio with extreme concentration risk"""

    return RiskAnalysisRequest(
        user_id="test_user_concentration",
        total_value_usd=50000,
        assets=[
            {"token": "ethereum", "balance": 20, "price": 2500, "value_usd": 50000, "chain": "ethereum",
             "change_24h": 3.2},
        ],
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=0.65
    )


@test_agent.on_message(model=RiskReport)
async def handle_risk_report(ctx: Context, sender: str, msg: RiskReport):
    print(f"sender: {sender}")

    ctx.logger.info(f"✅ Received risk report for {msg.user_id}")
    ctx.logger.info(f"   Risk Level: {msg.overall_risk.upper()}")
    ctx.logger.info(f"   Risk Score: {msg.risk_score:.2%}")
    ctx.logger.info(f"   Should Alert: {msg.should_alert}")

    if msg.concerns:
        ctx.logger.info("   Concerns:")
        for concern in msg.concerns:
            ctx.logger.info(f"     - {concern}")


@test_agent.on_interval(period=10.0)
async def send_test_portfolios(ctx: Context):
    test_portfolios = [
        create_low_risk_portfolio(),
        create_medium_risk_portfolio(),
        create_high_risk_portfolio(),
        create_critical_risk_portfolio(),
        create_high_volatility_portfolio(),
        create_high_concentration_portfolio(),
    ]

    for portfolio in test_portfolios:
        ctx.logger.info(f"📊 Sending {portfolio.user_id} to Risk Agent...")
        await ctx.send(RISK_AGENT_ADDRESS, portfolio)

        import asyncio
        await asyncio.sleep(2)


@test_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info("🧪 DeFiGuard Risk Test Agent Started!")
    ctx.logger.info(f"📍 Test Agent Address: {test_agent.address}")
    ctx.logger.info(f"🎯 Sending to Risk Agent: {RISK_AGENT_ADDRESS}")
    ctx.logger.info("=" * 60)
    ctx.logger.info("Simulating 6 test portfolios:")
    ctx.logger.info("  1. Low Risk (diversified)")
    ctx.logger.info("  2. Medium Risk (concentrated)")
    ctx.logger.info("  3. High Risk (meme coins)")
    ctx.logger.info("  4. Critical Risk (single token)")
    ctx.logger.info("  5. High Volatility (extreme swings)")
    ctx.logger.info("  6. High Concentration (100% single asset)")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    test_agent.run()
