from uagents import Agent, Context, Model
# from uagents.setup import fund_agent_if_low
from typing import List, Dict
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

try:
    from hyperon import MeTTa

    METTA_AVAILABLE = True
    print("✅ MeTTa (SingularityNET) integration active")
except ImportError:
    METTA_AVAILABLE = False
    print("⚠️  MeTTa not available, using fallback knowledge system")

    # Define a fallback MeTTa class so name always exists
    class MeTTa:
        def __init__(self):
            print("⚠️  Using dummy MeTTa fallback (no real reasoning engine).")

        @staticmethod
        def run():
            print("⚠️  MeTTa fallback: run() called but hyperon not installed.")

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
    # mailbox=False  # type: ignore[arg-type]
)

# fund_agent_if_low(str(risk_agent.wallet.address()))

print(f"Risk Analysis Agent Address: {risk_agent.address}")

# Initialize MeTTa
metta = None
if METTA_AVAILABLE:
    try:
        metta = MeTTa()

        # Load MeTTa knowledge base from file
        knowledge_file = os.path.join("metta", "risk_knowledge.metta")
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r') as f:
                knowledge_content = f.read()
                metta.run(knowledge_content)
            print("✅ MeTTa knowledge base loaded from file")
        else:
            # Inline knowledge base if file not found
            print("⚠️  MeTTa file not found, loading inline knowledge")
            metta_knowledge = """
            ; DeFiGuard Risk Knowledge Graph
            ; Powered by SingularityNET MeTTa

            ; Define types
            (: Asset Type)
            (: RiskLevel Type)
            (: Token Type)

            ; Asset risk classifications
            (has-risk bitcoin low)
            (has-risk ethereum low)
            (has-risk bnb low)
            (has-risk usdc low)
            (has-risk usdt low)
            (has-risk dai low)
            (has-risk busd low)

            ; High-risk asset patterns
            (has-risk-pattern leverage high)
            (has-risk-pattern 3x critical)
            (has-risk-pattern 2x high)
            (has-risk-pattern short high)
            (has-risk-pattern bear high)
            (has-risk-pattern bull high)
            (has-risk-pattern safemoon critical)
            (has-risk-pattern baby high)
            (has-risk-pattern elon high)
            (has-risk-pattern moon high)

            ; Concentration risk rules
            (concentration-threshold critical 0.70)
            (concentration-threshold high 0.50)
            (concentration-threshold medium 0.30)

            ; Volatility risk rules
            (volatility-threshold extreme 50)
            (volatility-threshold high 20)
            (volatility-threshold medium 10)

            ; Risk scoring weights
            (weight concentration 0.3)
            (weight volatility 0.4)
            (weight asset-quality 0.3)
            """
            metta.run(metta_knowledge)
            print("✅ MeTTa inline knowledge base loaded")

    except Exception as e:
        print(f"❌ Error initializing MeTTa: {e}")
        METTA_AVAILABLE = False
        metta = None

# Risk thresholds
RISK_THRESHOLDS = {
    "low": 0.3,
    "medium": 0.5,
    "high": 0.7,
    "critical": 0.85
}

FALLBACK_KNOWLEDGE = {
    "asset_risks": {
        "bitcoin": "low", "btc": "low",
        "ethereum": "low", "eth": "low",
        "bnb": "low",
        "usdc": "low", "usdt": "low", "dai": "low",
    },
    "high_risk_patterns": ["leverage", "3x", "2x", "short", "bear", "bull", "safemoon", "baby", "elon", "moon"]
}


def query_asset_risk_metta(token: str) -> str:
    """Query MeTTa for asset risk level"""
    if not METTA_AVAILABLE or not metta:
        # Fallback to Python knowledge
        return FALLBACK_KNOWLEDGE["asset_risks"].get(token.lower(), "medium")

    try:
        # Query MeTTa: (has-risk TOKEN LEVEL)
        query = f"!(match &self (has-risk {token.lower()} $level) $level)"
        result = metta.run(query)

        if result and len(result) > 0:
            # Extract risk level from result
            risk_level = str(result[0]).strip()
            print(f"🧠 MeTTa: {token} risk = {risk_level}")
            return risk_level

        # Check for risk patterns
        pattern_query = f"!(match &self (has-risk-pattern $pattern $level) (if (== $pattern {token.lower()}) $level))"
        pattern_result = metta.run(pattern_query)

        if pattern_result and len(pattern_result) > 0:
            risk_level = str(pattern_result[0]).strip()
            print(f"🧠 MeTTa pattern: {token} risk = {risk_level}")
            return risk_level

    except Exception as err:
        print(f"⚠️  MeTTa query error: {err}")

    return "medium"  # Default


def query_concentration_threshold_metta(percentage: float) -> str:
    """Query MeTTa for concentration risk level"""
    if not METTA_AVAILABLE or not metta:
        # Fallback logic
        if percentage >= 0.70:
            return "critical"
        elif percentage >= 0.50:
            return "high"
        elif percentage >= 0.30:
            return "medium"
        return "low"

    try:
        # Query MeTTa for concentration thresholds
        query = "!(match &self (concentration-threshold $level $threshold) ($level $threshold))"
        result = metta.run(query)

        if result:
            # Find appropriate risk level based on percentage
            for item in result:
                level = str(item[0]).strip()
                threshold = float(str(item[1]).strip())
                if percentage >= threshold:
                    print(f"🧠 MeTTa concentration: {percentage:.2f} = {level}")
                    return level
    except Exception as err:
        print(f"⚠️  MeTTa concentration query error: {err}")

    return "low"


def query_volatility_threshold_metta(change: float) -> str:
    """Query MeTTa for volatility risk level"""
    if not METTA_AVAILABLE or not metta:
        # Fallback logic
        if change >= 50:
            return "extreme"
        elif change >= 20:
            return "high"
        elif change >= 10:
            return "medium"
        return "low"

    try:
        # Query MeTTa for volatility thresholds
        query = "!(match &self (volatility-threshold $level $threshold) ($level $threshold))"
        result = metta.run(query)

        if result:
            for item in result:
                level = str(item[0]).strip()
                threshold = float(str(item[1]).strip())
                if change >= threshold:
                    print(f"🧠 MeTTa volatility: {change:.1f}% = {level}")
                    return level
    except Exception as err:
        print(f"⚠️  MeTTa volatility query error: {err}")

    return "low"


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
    """Analyze portfolio concentration using MeTTa"""
    concerns = []

    if not assets or total_value == 0:
        return {"concerns": [], "score": 0}

    # Calculate Herfindahl index
    hhi = sum((asset["value_usd"] / total_value) ** 2 for asset in assets)

    # Check individual asset concentration
    for asset in assets:
        percentage = (asset["value_usd"] / total_value)

        concentration_risk = query_concentration_threshold_metta(percentage)

        if concentration_risk == "critical":
            concerns.append(
                f"{asset['token']} represents {percentage * 100:.1f}% - CRITICAL concentration (MeTTa)"
            )
        elif concentration_risk == "high":
            concerns.append(
                f"{asset['token']} represents {percentage * 100:.1f}% - high concentration (MeTTa)"
            )
        elif concentration_risk == "medium" and percentage > 0.30:
            concerns.append(
                f"{asset['token']} represents {percentage * 100:.1f}% - moderate concentration (MeTTa)"
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

    for asset in assets:
        change = abs(asset.get("change_24h", 0))

        volatility_risk = query_volatility_threshold_metta(change)

        if volatility_risk == "extreme":
            concerns.append(
                f"{asset['token']} EXTREME volatility: {change:.1f}% in 24h (MeTTa)"
            )
        elif volatility_risk == "high":
            concerns.append(
                f"{asset['token']} high volatility: {change:.1f}% in 24h (MeTTa)"
            )

    # Calculate average volatility
    avg_volatility = sum(abs(a.get("change_24h", 0)) for a in assets) / len(assets) if assets else 0
    volatility_score = min(avg_volatility / 30, 1.0)

    return {
        "concerns": concerns,
        "score": volatility_score,
        "avg_volatility": avg_volatility
    }


def analyze_asset_risk(assets: List[Dict]) -> Dict:
    """Analyze individual asset risks using MeTTa"""
    concerns = []
    total_risk_score = 0

    for asset in assets:
        token = asset["token"].lower()

        # Query MeTTa for asset-specific risk
        asset_risk = query_asset_risk_metta(token)

        if asset_risk == "critical":
            concerns.append(
                f"{asset['token']} classified as CRITICAL risk by MeTTa knowledge graph"
            )
            total_risk_score += 1.0
        elif asset_risk == "high":
            concerns.append(
                f"{asset['token']} classified as HIGH risk by MeTTa knowledge graph"
            )
            total_risk_score += 0.7
        elif asset_risk == "medium":
            # Only add concern if it's a significant portion
            if asset.get("value_usd", 0) / sum(a.get("value_usd", 0) for a in assets) > 0.1:
                concerns.append(
                    f"{asset['token']} has medium risk classification (MeTTa)"
                )
                total_risk_score += 0.3

    risk_score = min(total_risk_score / max(len(assets), 1), 1.0)

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
            "🧠 MeTTa Analysis: Diversify portfolio - reduce concentration in top holdings"
        )

    # Volatility recommendations
    if volatility_analysis["score"] > 0.6:
        recommendations.append(
            "🧠 MeTTa Analysis: Increase stablecoin allocation to reduce volatility"
        )
        recommendations.append(
            "Set stop-loss orders for highly volatile assets"
        )

        # Risk level recommendations
        if risk_level == "critical":
            recommendations.append(
                "⚠️ URGENT: MeTTa knowledge graph detected critical risk - review immediately"
            )
        elif risk_level == "high":
            recommendations.append(
                "🧠 MeTTa Analysis: High risk detected - rebalance within 24 hours"
            )
        elif risk_level == "medium":
            recommendations.append(
                "🧠 MeTTa Analysis: Moderate risk - monitor portfolio daily"
            )
        else:
            recommendations.append(
                "✅ MeTTa Analysis: Portfolio risk is acceptable - continue monitoring"
            )

    # Asset-specific recommendations
    if asset_analysis["concerns"]:
        recommendations.append(
            "🧠 MeTTa Knowledge Graph: Review flagged high-risk assets"
        )

    return recommendations


@risk_agent.on_message(model=RiskAnalysisRequest)
async def analyze_risk(ctx: Context, sender: str, msg: RiskAnalysisRequest):
    """Perform comprehensive risk analysis using SingularityNET MeTTa"""
    ctx.logger.info(f"🧠 Analyzing risk with MeTTa for user: {msg.user_id}")

    try:
        # Perform analyses using MeTTa knowledge graph
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
            f"✅ MeTTa risk analysis complete: {risk_level} "
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
        ctx.logger.error(f"❌ Error in MeTTa risk analysis: {err}")
        await ctx.send(sender, ErrorResponse(message=f"Risk analysis failed: {str(err)}"))


@risk_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info("🧠 Risk Analysis Agent started!")
    ctx.logger.info(f"📍 Agent address: {risk_agent.address}")
    if METTA_AVAILABLE:
        ctx.logger.info("✅ SingularityNET MeTTa integration: ACTIVE")
    else:
        ctx.logger.info("⚠️  SingularityNET MeTTa: Using fallback (install hyperon)")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    risk_agent.run()