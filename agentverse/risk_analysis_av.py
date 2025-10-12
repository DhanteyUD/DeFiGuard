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
    overall_risk: str  # low, medium, high, critical
    risk_score: float
    concerns: List[str]
    recommendations: List[str]
    timestamp: str
    should_alert: bool


class ErrorResponse(Model):
    message: str


risk_agent = Agent(
    name="risk_analysis",
    mailbox=True # type: ignore[arg-type]
)

print(f"Risk Analysis Agent Address: {risk_agent.address}")


RISK_KNOWLEDGE = {
    "asset_risks": {
        "bitcoin": "low",
        "ethereum": "low",
        "bnb": "low",
        "usdc": "low",
        "usdt": "low",
        "dai": "low",
        "busd": "low"
    },
    "concentration_thresholds": {
        "critical": 0.70,
        "high": 0.50,
        "medium": 0.30
    },
    "volatility_thresholds": {
        "extreme": 50,
        "high": 20,
        "medium": 10
    }
}


RISK_THRESHOLDS = {
    "low": 0.3,
    "medium": 0.5,
    "high": 0.7,
    "critical": 0.85
}


def query_knowledge_base(query_type: str, data: Dict) -> any:
    """Query knowledge base for risk assessment"""
    if query_type == "asset_risk":
        token = data.get("token", "").lower()
        return RISK_KNOWLEDGE["asset_risks"].get(token, "medium")

    elif query_type == "concentration_level":
        percentage = data.get("percentage", 0)
        if percentage >= RISK_KNOWLEDGE["concentration_thresholds"]["critical"]:
            return "critical"
        elif percentage >= RISK_KNOWLEDGE["concentration_thresholds"]["high"]:
            return "high"
        elif percentage >= RISK_KNOWLEDGE["concentration_thresholds"]["medium"]:
            return "medium"
        return "low"

    elif query_type == "volatility_level":
        change = abs(data.get("change", 0))
        if change >= RISK_KNOWLEDGE["volatility_thresholds"]["extreme"]:
            return "extreme"
        elif change >= RISK_KNOWLEDGE["volatility_thresholds"]["high"]:
            return "high"
        elif change >= RISK_KNOWLEDGE["volatility_thresholds"]["medium"]:
            return "medium"
        return "low"

    return None


def get_risk_level(score: float) -> str:
    """Convert risk score to risk level"""
    if score >= RISK_THRESHOLDS["critical"]:
        return "critical"
    elif score >= RISK_THRESHOLDS["high"]:
        return "high"
    elif score >= RISK_THRESHOLDS["medium"]:
        return "medium"
    else:
        return "low"


def analyze_concentration(assets: List[Dict], total_value: float) -> Dict:
    """Analyze portfolio concentration risk"""
    concerns = []

    if not assets or total_value == 0:
        return {"concerns": [], "score": 0}

    # Calculate Herfindahl-Hirschman Index
    hhi = sum((asset["value_usd"] / total_value) ** 2 for asset in assets)

    # Check individual asset concentration
    for asset in assets:
        percentage = (asset["value_usd"] / total_value) * 100
        if percentage > 70:
            concerns.append(
                f"{asset['token']} represents {percentage:.1f}% - extreme concentration"
            )
        elif percentage > 50:
            concerns.append(
                f"{asset['token']} represents {percentage:.1f}% - over-concentrated"
            )

    concentration_score: float = min(hhi * 2.0, 1.0)

    return {
        "concerns": concerns,
        "score": concentration_score,
        "hhi": hhi
    }


def analyze_volatility(assets: List[Dict]) -> Dict:
    """Analyze portfolio volatility risk"""
    concerns = []

    if not assets:
        return {"concerns": [], "score": 0}

    high_volatility_assets = []
    extreme_volatility_assets = []

    for asset in assets:
        change = abs(asset.get("change_24h", 0))
        if change > 50:
            extreme_volatility_assets.append((asset["token"], change))
        elif change > 20:
            high_volatility_assets.append((asset["token"], change))

    if extreme_volatility_assets:
        for token, change in extreme_volatility_assets:
            concerns.append(
                f"{token} extreme volatility ({change:.1f}% in 24h)"
            )

    if high_volatility_assets:
        for token, change in high_volatility_assets:
            concerns.append(
                f"{token} high volatility ({change:.1f}% in 24h)"
            )

    avg_volatility = sum(abs(a.get("change_24h", 0)) for a in assets) / len(assets)
    volatility_score = min(avg_volatility / 30, 1.0)

    return {
        "concerns": concerns,
        "score": volatility_score,
        "avg_volatility": avg_volatility
    }


def analyze_asset_risk(assets: List[Dict]) -> Dict:
    """Analyze individual asset risks"""
    concerns = []
    high_risk_indicators = ["leverage", "3x", "short", "bear", "bull", "2x"]

    for asset in assets:
        token_lower = asset["token"].lower()
        for indicator in high_risk_indicators:
            if indicator in token_lower:
                concerns.append(
                    f"{asset['token']} identified as high-risk asset type"
                )
                break

    risk_score = len(concerns) / max(len(assets), 1)

    return {
        "concerns": concerns,
        "score": risk_score
    }


def generate_recommendations(
        risk_level: str,
        concentration_analysis: Dict,
        volatility_analysis: Dict,
        asset_analysis: Dict
) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []

    if concentration_analysis["score"] > 0.7:
        recommendations.append(
            "Diversify portfolio - reduce concentration in top holdings"
        )

    if volatility_analysis["score"] > 0.6:
        recommendations.append(
            "Consider increasing stablecoin allocation to reduce volatility"
        )
        recommendations.append(
            "Set stop-loss orders for highly volatile assets"
        )

    if risk_level == "critical":
        recommendations.append(
            "URGENT: Review portfolio immediately - critical risk detected"
        )
    elif risk_level == "high":
        recommendations.append(
            "High risk detected - consider rebalancing within 24 hours"
        )
    elif risk_level == "medium":
        recommendations.append(
            "Moderate risk - monitor portfolio daily"
        )
    else:
        recommendations.append(
            "Portfolio risk is acceptable - continue monitoring"
        )

    if asset_analysis["concerns"]:
        recommendations.append(
            "Review high-risk assets - consider reducing exposure"
        )

    return recommendations


@risk_agent.on_message(model=RiskAnalysisRequest)
async def analyze_risk(ctx: Context, sender: str, msg: RiskAnalysisRequest):
    """Perform comprehensive risk analysis"""
    ctx.logger.info(f"🔍 Analyzing risk for user: {msg.user_id}")

    try:
        # Perform analyses
        concentration = analyze_concentration(msg.assets, msg.total_value_usd)
        volatility = analyze_volatility(msg.assets)
        asset_risk = analyze_asset_risk(msg.assets)

        # Calculate weighted risk score
        weights = {"concentration": 0.3, "volatility": 0.4, "asset": 0.3}

        weighted_score = (
                concentration["score"] * weights["concentration"] +
                volatility["score"] * weights["volatility"] +
                asset_risk["score"] * weights["asset"]
        )

        risk_level = get_risk_level(weighted_score)

        all_concerns = (
                concentration["concerns"] +
                volatility["concerns"] +
                asset_risk["concerns"]
        )

        recommendations = generate_recommendations(
            risk_level,
            concentration,
            volatility,
            asset_risk
        )

        should_alert = risk_level in ["high", "critical"] or weighted_score > 0.7

        report = RiskReport(
            user_id=msg.user_id,
            overall_risk=risk_level,
            risk_score=weighted_score,
            concerns=all_concerns,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc).isoformat(),
            should_alert=should_alert
        )

        ctx.logger.info(
            f"✅ Risk analysis complete: {risk_level} "
            f"(score: {weighted_score:.2f})"
        )

        await ctx.send(sender, report)


        alert_agent_address = "agent1qftjr2fh4uuk0se60sp6e6yevamtlmh5tlsjxx9ny2kgenggf089unxed9f"
        if should_alert and alert_agent_address:
            await ctx.send(alert_agent_address, report)

    except Exception as e:
        ctx.logger.error(f"❌ Error in risk analysis: {e}")
        await ctx.send(sender, ErrorResponse(message=f"Risk analysis failed: {str(e)}"))


@risk_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info("🧠 DeFiGuard Risk Analysis Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {risk_agent.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("📚 Knowledge base loaded: Python-based (MeTTa-ready)")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    risk_agent.run()