from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from typing import List, Dict
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from hyperon import MeTTa

load_dotenv()


# Data Models
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


# Create Risk Analysis Agent
risk_agent = Agent(
    name="risk_analysis",
    seed=os.getenv("RISK_AGENT_SEED", "risk_demo_seed"),
    port=8001,
    endpoint=["http://localhost:8001/submit"],
    # mailbox=True
)

fund_agent_if_low(str(risk_agent.wallet.address()))

print(f"Risk Analysis Agent Address: {risk_agent.address}")

# Initialize MeTTa
metta = MeTTa()

# Load knowledge base
try:
    knowledge_file = os.path.join("metta", "risk_knowledge.metta")
    if os.path.exists(knowledge_file):
        with open(knowledge_file, 'r') as f:
            knowledge_content = f.read()
            metta.run(knowledge_content)
        print("MeTTa knowledge base loaded successfully")
    else:
        print("Warning: MeTTa knowledge file not found")
except Exception as e:
    print(f"Error loading MeTTa knowledge: {e}")

# Risk thresholds
RISK_THRESHOLDS = {
    "low": 0.3,
    "medium": 0.5,
    "high": 0.7,
    "critical": 0.85
}


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
    """Analyze portfolio concentration"""
    concerns = []

    if not assets or total_value == 0:
        return {"concerns": [], "score": 0}

    # Calculate Herfindahl index
    hhi = sum((asset["value_usd"] / total_value) ** 2 for asset in assets)

    # Check individual asset concentration
    for asset in assets:
        percentage = (asset["value_usd"] / total_value) * 100
        if percentage > 70:
            concerns.append(
                f"{asset['token']} represents {percentage:.1f}% of portfolio - extreme concentration"
            )
        elif percentage > 50:
            concerns.append(
                f"{asset['token']} represents {percentage:.1f}% of portfolio - over-concentrated"
            )

    # Overall concentration score
    concentration_score: float = min(hhi * 2.0, 1.0)

    return {
        "concerns": concerns,
        "score": concentration_score,
        "hhi": hhi
    }


def analyze_volatility(assets: List[Dict]) -> Dict:
    """Analyze portfolio volatility"""
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
                f"{token} showing extreme volatility ({change:.1f}% in 24h)"
            )

    if high_volatility_assets:
        for token, change in high_volatility_assets:
            concerns.append(
                f"{token} showing high volatility ({change:.1f}% in 24h)"
            )

    # Calculate average volatility
    avg_volatility = sum(abs(a.get("change_24h", 0)) for a in assets) / len(assets)
    volatility_score = min(avg_volatility / 30, 1.0)

    return {
        "concerns": concerns,
        "score": volatility_score,
        "avg_volatility": avg_volatility
    }


def analyze_asset_risk(assets: List[Dict]) -> Dict:
    """Analyze individual asset risks using MeTTa"""
    concerns = []

    # Known high-risk tokens (in production, query from MeTTa)
    high_risk_indicators = ["leverage", "3x", "short", "bear", "bull"]

    for asset in assets:
        token_lower = asset["token"].lower()

        # Check for high-risk indicators
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

    # Concentration recommendations
    if concentration_analysis["score"] > 0.7:
        recommendations.append(
            "Diversify portfolio - reduce concentration in top holdings"
        )

    # Volatility recommendations
    if volatility_analysis["score"] > 0.6:
        recommendations.append(
            "Consider increasing stablecoin allocation to reduce volatility"
        )
        recommendations.append(
            "Set stop-loss orders for highly volatile assets"
        )

    # Risk level recommendations
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

    # Asset-specific recommendations
    if asset_analysis["concerns"]:
        recommendations.append(
            "Review high-risk assets - consider reducing exposure"
        )

    return recommendations


@risk_agent.on_message(model=RiskAnalysisRequest)
async def analyze_risk(ctx: Context, sender: str, msg: RiskAnalysisRequest):
    """Perform comprehensive risk analysis"""
    ctx.logger.info(f"Analyzing risk for user: {msg.user_id}")

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

        # Get risk level
        risk_level = get_risk_level(weighted_score)

        # Collect all concerns
        all_concerns = (
                concentration["concerns"] +
                volatility["concerns"] +
                asset_risk["concerns"]
        )

        # Generate recommendations
        recommendations = generate_recommendations(
            risk_level,
            concentration,
            volatility,
            asset_risk
        )

        # Determine if alert is needed
        should_alert = risk_level in ["high", "critical"] or weighted_score > 0.7

        # Create report
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
            f"Risk analysis complete: {risk_level} "
            f"(score: {weighted_score:.2f})"
        )

        # Send report back to sender
        await ctx.send(sender, report)

        # If alert needed, send to Alert Agent
        if should_alert:
            alert_agent_address = os.getenv("ALERT_AGENT_ADDRESS", "")
            if alert_agent_address:
                await ctx.send(alert_agent_address, report)

    except Exception as err:
        ctx.logger.error(f"Error in risk analysis: {err}")
        await ctx.send(sender, ErrorResponse(message=f"Risk analysis failed: {str(err)}"))


@risk_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Risk Analysis Agent started!")
    ctx.logger.info(f"Agent address: {risk_agent.address}")


if __name__ == "__main__":
    risk_agent.run()
