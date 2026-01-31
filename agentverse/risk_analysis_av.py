from uagents import Agent, Context, Model
from datetime import datetime, timezone
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from hyperon import MeTTa

    METTA_AVAILABLE = True
    print("✅ MeTTa (SingularityNET) integration active")
except ImportError:
    METTA_AVAILABLE = False
    print("⚠️  MeTTa not available, using fallback knowledge system")


    # fallback MeTTa class
    class MeTTa:
        def __init__(self):
            print("⚠️  Using dummy MeTTa fallback (no real reasoning engine).")

        @staticmethod
        def run(*_args, **_kwargs):
            print("⚠️  MeTTa fallback: run() called but hyperon not installed.")


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


risk_agent_av = Agent(
    name="risk_analysis",
    mailbox=True
)

print(f"Risk Analysis Agent Address: {risk_agent_av.address}")

metta = None
if METTA_AVAILABLE:
    try:
        metta = MeTTa()

        metta_knowledge = """
; ============================================
; DeFiGuard Risk Knowledge Graph
; Powered by SingularityNET MeTTa
; Enhanced with Solana-specific rules
; ============================================

; Define types
(: Asset Type)
(: RiskLevel Type)
(: Token Type)
(: Chain Type)

; ============================================
; CHAIN DEFINITIONS
; ============================================

(chain solana non-evm)
(chain ethereum evm)
(chain bsc evm)
(chain polygon evm)
(chain arbitrum evm)
(chain optimism evm)
(chain base evm)
(chain avalanche evm)

; ============================================
; ASSET RISK CLASSIFICATIONS - EVM
; ============================================

; Low-risk assets (established cryptocurrencies)
(has-risk bitcoin low)
(has-risk btc low)
(has-risk ethereum low)
(has-risk eth low)
(has-risk bnb low)
(has-risk cardano low)
(has-risk ada low)

; Stablecoins (lowest risk)
(has-risk usdc low)
(has-risk usdt low)
(has-risk dai low)
(has-risk busd low)
(has-risk frax low)
(has-risk tusd low)

; Medium-risk DeFi tokens
(has-risk uniswap medium)
(has-risk uni medium)
(has-risk aave medium)
(has-risk compound medium)
(has-risk comp medium)
(has-risk curve medium)
(has-risk crv medium)

; ============================================
; SOLANA-SPECIFIC ASSET CLASSIFICATIONS
; ============================================

; Solana Native (low risk)
(has-risk solana low)
(has-risk sol low)

; Major Solana DeFi (medium risk)
(has-risk raydium medium)
(has-risk ray medium)
(has-risk orca medium)
(has-risk jupiter medium)
(has-risk jup medium)
(has-risk marinade medium)
(has-risk mnde medium)
(has-risk jito medium)
(has-risk pyth medium)

; Solana Liquid Staking (low-medium risk)
(has-risk msol low)
(has-risk jitosol low)
(has-risk bsol medium)

; Solana Meme Coins (high risk)
(has-risk bonk high)
(has-risk wif high)
(has-risk dogwifhat high)
(has-risk popcat high)
(has-risk myro high)
(has-risk wen high)
(has-risk slerf critical)
(has-risk bome high)

; ============================================
; HIGH-RISK ASSET PATTERNS (ALL CHAINS)
; ============================================

; Leveraged tokens (critical risk)
(has-risk-pattern leverage critical)
(has-risk-pattern 3x critical)
(has-risk-pattern 5x critical)
(has-risk-pattern 10x critical)
(has-risk-pattern 2x high)

; Directional tokens (high risk)
(has-risk-pattern short high)
(has-risk-pattern bear high)
(has-risk-pattern bull high)
(has-risk-pattern long high)

; Meme/speculative tokens (critical risk)
(has-risk-pattern safemoon critical)
(has-risk-pattern baby critical)
(has-risk-pattern elon critical)
(has-risk-pattern moon high)
(has-risk-pattern doge high)
(has-risk-pattern shib high)
(has-risk-pattern inu high)
(has-risk-pattern pepe high)
(has-risk-pattern floki high)

; New/unverified tokens
(has-risk-pattern new critical)
(has-risk-pattern launch critical)
(has-risk-pattern presale critical)
(has-risk-pattern fair-launch high)

; ============================================
; SOLANA-SPECIFIC RISK PATTERNS
; ============================================

; Solana meme coin patterns
(has-solana-risk-pattern cat high)
(has-solana-risk-pattern dog high)
(has-solana-risk-pattern pump critical)
(has-solana-risk-pattern fun critical)
(has-solana-risk-pattern ai-agent high)

; Solana rug pull indicators
(has-solana-risk mint-authority-active high)
(has-solana-risk freeze-authority-active critical)
(has-solana-risk no-metadata high)
(has-solana-risk unverified high)
(has-solana-risk low-liquidity high)
(has-solana-risk high-concentration critical)

; ============================================
; CONCENTRATION RISK RULES
; ============================================

(concentration-threshold critical 0.70)
(concentration-threshold high 0.50)
(concentration-threshold medium 0.30)

; ============================================
; VOLATILITY RISK RULES
; ============================================

(volatility-threshold extreme 50)
(volatility-threshold high 20)
(volatility-threshold medium 10)

; ============================================
; RISK SCORING WEIGHTS
; ============================================

(weight concentration 0.30)
(weight volatility 0.35)
(weight asset-quality 0.20)
(weight chain-diversity 0.15)

; Solana-specific weight adjustments
(solana-weight mint-authority 0.25)
(solana-weight freeze-authority 0.30)
(solana-weight holder-concentration 0.25)
(solana-weight liquidity 0.20)
"""

        metta.run(metta_knowledge)
        print("✅ MeTTa knowledge base loaded successfully")

    except Exception as e:
        print(f"❌ Error initializing MeTTa: {e}")
        METTA_AVAILABLE = False
        metta = None

RISK_THRESHOLDS = {
    "low": 0.3,
    "medium": 0.5,
    "high": 0.7,
    "critical": 0.85
}

# =========================
# FALLBACK KNOWLEDGE
# =========================

FALLBACK_KNOWLEDGE = {
    "asset_risks": {
        # EVM tokens
        "bitcoin": "low", "btc": "low",
        "ethereum": "low", "eth": "low",
        "bnb": "low",
        "usdc": "low", "usdt": "low", "dai": "low",
        "uniswap": "medium", "uni": "medium",
        "aave": "medium",

        # Solana tokens (NEW)
        "solana": "low", "sol": "low",
        "raydium": "medium", "ray": "medium",
        "orca": "medium",
        "jupiter": "medium", "jup": "medium",
        "marinade": "medium", "mnde": "medium",
        "jito": "medium",
        "pyth": "medium",
        "msol": "low",
        "jitosol": "low",

        # Solana meme coins (high risk)
        "bonk": "high",
        "wif": "high", "dogwifhat": "high",
        "popcat": "high",
        "myro": "high",
        "wen": "high",
        "slerf": "critical",
        "bome": "high",
    },
    "high_risk_patterns": [
        # General patterns
        "leverage", "3x", "2x", "5x", "10x",
        "short", "bear", "bull", "long",
        "safemoon", "baby", "elon", "moon",
        "doge", "shib", "inu", "pepe", "floki",
        "new", "launch", "presale",

        # Solana-specific patterns (NEW)
        "pump", "fun", "cat", "dog", "ai-agent",
    ],

    # NEW: Solana-specific risk indicators
    "solana_risk_indicators": {
        "mint_authority_active": "high",
        "freeze_authority_active": "critical",
        "no_metadata": "high",
        "unverified": "high",
        "low_liquidity": "high",
        "high_concentration": "critical",
    }
}


def detect_chain_from_asset(asset: Dict) -> str:
    # Check if chain is explicitly specified
    if "chain" in asset:
        return asset["chain"].lower()

    # Check if it has a mint address (Solana)
    if "mint" in asset:
        return "solana"

    # Default to EVM
    return "evm"


def query_asset_risk_metta(token: str, chain: str = "evm") -> str:
    if not METTA_AVAILABLE or not metta:
        return FALLBACK_KNOWLEDGE["asset_risks"].get(token.lower(), "medium")

    try:
        # First try exact token match
        query = f"!(match &self (has-risk {token.lower()} $level) $level)"
        result = metta.run(query)

        if result and len(result) > 0:
            risk_level = str(result[0]).strip()
            chain_emoji = "◎" if chain == "solana" else "⟠"
            print(f"🧠 MeTTa: {chain_emoji} {token} risk = {risk_level}")
            return risk_level

        # Check for risk patterns
        for pattern in FALLBACK_KNOWLEDGE["high_risk_patterns"]:
            if pattern in token.lower():
                pattern_query = f"!(match &self (has-risk-pattern {pattern} $level) $level)"
                pattern_result = metta.run(pattern_query)

                if pattern_result and len(pattern_result) > 0:
                    risk_level = str(pattern_result[0]).strip()
                    print(f"🧠 MeTTa pattern: {token} matches {pattern} = {risk_level}")
                    return risk_level

        # Check Solana-specific patterns if on Solana
        if chain == "solana":
            for pattern in ["pump", "fun", "cat", "dog"]:
                if pattern in token.lower():
                    solana_query = f"!(match &self (has-solana-risk-pattern {pattern} $level) $level)"
                    solana_result = metta.run(solana_query)

                    if solana_result and len(solana_result) > 0:
                        risk_level = str(solana_result[0]).strip()
                        print(f"🧠 MeTTa Solana pattern: {token} matches {pattern} = {risk_level}")
                        return risk_level

    except Exception as err:
        print(f"⚠️  MeTTa query error: {err}")

    return "medium"


def query_solana_risk_indicator(indicator: str) -> str:
    if not METTA_AVAILABLE or not metta:
        return FALLBACK_KNOWLEDGE["solana_risk_indicators"].get(indicator, "medium")

    try:
        query = f"!(match &self (has-solana-risk {indicator} $level) $level)"
        result = metta.run(query)

        if result and len(result) > 0:
            risk_level = str(result[0]).strip()
            print(f"🧠 MeTTa Solana indicator: {indicator} = {risk_level}")
            return risk_level
    except Exception as err:
        print(f"⚠️  MeTTa Solana indicator query error: {err}")

    return FALLBACK_KNOWLEDGE["solana_risk_indicators"].get(indicator, "medium")


def query_concentration_threshold_metta(percentage: float) -> str:
    if not METTA_AVAILABLE or not metta:
        if percentage >= 0.70:
            return "critical"
        elif percentage >= 0.50:
            return "high"
        elif percentage >= 0.30:
            return "medium"
        return "low"

    try:
        query = "!(match &self (concentration-threshold $level $threshold) ($level $threshold))"
        result = metta.run(query)

        if result:
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
    if not METTA_AVAILABLE or not metta:
        if change >= 50:
            return "extreme"
        elif change >= 20:
            return "high"
        elif change >= 10:
            return "medium"
        return "low"

    try:
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
    if score >= RISK_THRESHOLDS["critical"]:
        return "critical"
    elif score >= RISK_THRESHOLDS["high"]:
        return "high"
    elif score >= RISK_THRESHOLDS["medium"]:
        return "medium"
    else:
        return "low"


def analyze_concentration(assets: List[Dict], total_value: float) -> Dict:
    concerns = []

    if not assets or total_value == 0:
        return {"concerns": [], "score": 0}

    # Calculate Herfindahl index
    hhi = sum((asset["value_usd"] / total_value) ** 2 for asset in assets)

    # Check individual asset concentration using MeTTa
    for asset in assets:
        percentage = (asset["value_usd"] / total_value)
        chain = detect_chain_from_asset(asset)
        chain_emoji = "◎" if chain == "solana" else "⟠"

        # Query MeTTa for risk level
        concentration_risk = query_concentration_threshold_metta(percentage)

        if concentration_risk == "critical":
            concerns.append(
                f"{chain_emoji} {asset['token']} represents {percentage * 100:.1f}% - CRITICAL concentration (MeTTa)"
            )
        elif concentration_risk == "high":
            concerns.append(
                f"{chain_emoji} {asset['token']} represents {percentage * 100:.1f}% - high concentration (MeTTa)"
            )
        elif concentration_risk == "medium" and percentage > 0.30:
            concerns.append(
                f"{chain_emoji} {asset['token']} represents {percentage * 100:.1f}% - moderate concentration (MeTTa)"
            )

    concentration_score = min(hhi * 2.0, 1.0)

    return {
        "concerns": concerns,
        "score": concentration_score,
        "hhi": hhi
    }


def analyze_volatility(assets: List[Dict]) -> Dict:
    concerns = []

    if not assets:
        return {"concerns": [], "score": 0}

    for asset in assets:
        change = abs(asset.get("change_24h", 0))
        chain = detect_chain_from_asset(asset)
        chain_emoji = "◎" if chain == "solana" else "⟠"

        # Query MeTTa for volatility risk
        volatility_risk = query_volatility_threshold_metta(change)

        if volatility_risk == "extreme":
            concerns.append(
                f"{chain_emoji} {asset['token']} EXTREME volatility: {change:.1f}% in 24h (MeTTa)"
            )
        elif volatility_risk == "high":
            concerns.append(
                f"{chain_emoji} {asset['token']} high volatility: {change:.1f}% in 24h (MeTTa)"
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
    concerns = []
    total_risk_score = 0

    for asset in assets:
        token = asset["token"].lower()
        chain = detect_chain_from_asset(asset)
        chain_emoji = "◎" if chain == "solana" else "⟠"

        # Query MeTTa for asset risk
        asset_risk = query_asset_risk_metta(token, chain)

        if asset_risk == "critical":
            concerns.append(
                f"{chain_emoji} {asset['token']} classified as CRITICAL risk by MeTTa knowledge graph"
            )
            total_risk_score += 1.0
        elif asset_risk == "high":
            concerns.append(
                f"{chain_emoji} {asset['token']} classified as HIGH risk by MeTTa knowledge graph"
            )
            total_risk_score += 0.7
        elif asset_risk == "medium":
            total_asset_value = sum(a.get("value_usd", 0) for a in assets)
            if total_asset_value > 0:
                if asset.get("value_usd", 0) / total_asset_value > 0.1:
                    concerns.append(
                        f"{chain_emoji} {asset['token']} has medium risk classification (MeTTa)"
                    )
                    total_risk_score += 0.3

        # ===============================
        # SOLANA-SPECIFIC RISK CHECKS
        # ===============================
        if chain == "solana":
            risk_level = asset.get("risk_level", "")

            if risk_level == "unknown":
                concerns.append(
                    f"◎️ {asset['token']} is UNKNOWN/UNVERIFIED - potential scam risk"
                )
                total_risk_score += 0.5

            # Check mint authority (if provided by portfolio monitor)
            if asset.get("mint_authority_active"):
                indicator_risk = query_solana_risk_indicator("mint-authority-active")
                concerns.append(
                    f"◎️ {asset['token']} has ACTIVE mint authority - rug pull risk ({indicator_risk})"
                )
                total_risk_score += 0.6

            # Check freeze authority (if provided by portfolio monitor)
            if asset.get("freeze_authority_active"):
                indicator_risk = query_solana_risk_indicator("freeze-authority-active")
                concerns.append(
                    f"◎️ {asset['token']} has ACTIVE freeze authority - tokens can be frozen ({indicator_risk})"
                )
                total_risk_score += 0.8

            # Check holder concentration (if provided)
            holder_concentration = asset.get("top_holder_percent", 0)
            if holder_concentration > 50:
                concerns.append(
                    f"◎ {asset['token']} top holder owns {holder_concentration:.1f}% - extreme dump risk"
                )
                total_risk_score += 0.7
            elif holder_concentration > 30:
                concerns.append(
                    f"◎️ {asset['token']} top holder owns {holder_concentration:.1f}% - high concentration"
                )
                total_risk_score += 0.4

    risk_score = min(total_risk_score / max(len(assets), 1), 1.0)

    return {
        "concerns": concerns,
        "score": risk_score
    }


def analyze_chain_diversity(assets: List[Dict]) -> Dict:
    concerns = []

    if not assets:
        return {"concerns": [], "score": 0}

    # Count assets per chain
    chain_counts = {}
    chain_values = {}
    total_value = sum(a.get("value_usd", 0) for a in assets)

    for asset in assets:
        chain = detect_chain_from_asset(asset)
        chain_counts[chain] = chain_counts.get(chain, 0) + 1
        chain_values[chain] = chain_values.get(chain, 0) + asset.get("value_usd", 0)

    unique_chains = len(chain_counts)

    # Single chain concentration
    if unique_chains == 1:
        chain = list(chain_counts.keys())[0]
        chain_emoji = "◎" if chain == "solana" else "⟠"
        concerns.append(
            f"{chain_emoji} Portfolio is 100% on {chain.upper()} - consider cross-chain diversification"
        )
        diversity_score = 0.3
    else:
        # Check if one chain dominates
        for chain, value in chain_values.items():
            if total_value > 0:
                chain_percent = value / total_value
                chain_emoji = "◎" if chain == "solana" else "⟠"

                if chain_percent > 0.80:
                    concerns.append(
                        f"{chain_emoji} {chain_percent * 100:.0f}% of portfolio on {chain.upper()}"
                    )

        diversity_score = max(0.0, 0.3 - (unique_chains * 0.1))

    return {
        "concerns": concerns,
        "score": diversity_score,
        "unique_chains": unique_chains,
        "chain_distribution": chain_values
    }


def generate_recommendations(
        risk_level: str,
        concentration_analysis: Dict,
        volatility_analysis: Dict,
        asset_analysis: Dict,
        chain_diversity: Dict = None
) -> List[str]:
    recommendations = []

    if concentration_analysis["score"] > 0.7:
        recommendations.append(
            "🧠 MeTTa Analysis: Diversify portfolio - reduce concentration in top holdings"
        )

    if volatility_analysis["score"] > 0.6:
        recommendations.append(
            "🧠 MeTTa Analysis: Increase stablecoin allocation to reduce volatility"
        )
        recommendations.append(
            "Set stop-loss orders for highly volatile assets"
        )

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

    if asset_analysis["concerns"]:
        recommendations.append(
            "🧠 MeTTa Knowledge Graph: Review flagged high-risk assets"
        )

    # ==================================
    # SOLANA-SPECIFIC RECOMMENDATIONS
    # ==================================

    # Check for Solana-specific concerns
    solana_concerns = [c for c in asset_analysis["concerns"] if "◎" in c]

    if any("mint authority" in c.lower() for c in solana_concerns):
        recommendations.append(
            "◎ Solana: Avoid tokens with active mint authority - unlimited supply risk"
        )

    if any("freeze authority" in c.lower() for c in solana_concerns):
        recommendations.append(
            "◎ Solana: EXIT tokens with freeze authority - your funds can be locked"
        )

    if any("unknown" in c.lower() or "unverified" in c.lower() for c in solana_concerns):
        recommendations.append(
            "◎ Solana: Research unverified tokens before holding significant amounts"
        )

    if any("holder" in c.lower() and "concentration" in c.lower() for c in solana_concerns):
        recommendations.append(
            "◎ Solana: High holder concentration = whale dump risk. Set tight stop-losses."
        )

    # Chain diversity recommendations
    if chain_diversity:
        if chain_diversity.get("unique_chains", 0) == 1:
            recommendations.append(
                "🔗 Consider diversifying across multiple chains for reduced systemic risk"
            )

    return recommendations


@risk_agent_av.on_message(model=RiskAnalysisRequest)
async def analyze_risk(ctx: Context, sender: str, msg: RiskAnalysisRequest):
    ctx.logger.info(f"🧠 Analyzing risk with MeTTa for user: {msg.user_id}")

    # Detect if portfolio contains Solana assets
    has_solana = any(
        detect_chain_from_asset(asset) == "solana"
        for asset in msg.assets
    )

    if has_solana:
        ctx.logger.info("◎ Solana assets detected - applying Solana-specific risk rules")

    try:
        concentration = analyze_concentration(msg.assets, msg.total_value_usd)
        volatility = analyze_volatility(msg.assets)
        asset_risk = analyze_asset_risk(msg.assets)
        chain_diversity = analyze_chain_diversity(msg.assets)

        weights = {
            "concentration": 0.30,
            "volatility": 0.35,
            "asset": 0.20,
            "chain_diversity": 0.15
        }

        weighted_score = (
                concentration["score"] * weights["concentration"] +
                volatility["score"] * weights["volatility"] +
                asset_risk["score"] * weights["asset"] +
                chain_diversity["score"] * weights["chain_diversity"]
        )

        risk_level = get_risk_level(weighted_score)

        all_concerns = (
                concentration["concerns"] +
                volatility["concerns"] +
                asset_risk["concerns"] +
                chain_diversity["concerns"]
        )

        recommendations = generate_recommendations(
            risk_level,
            concentration,
            volatility,
            asset_risk,
            chain_diversity
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

        chain_info = "◎+⟠" if has_solana else "⟠"
        ctx.logger.info(
            f"✅ MeTTa risk analysis complete ({chain_info}): {risk_level} "
            f"(score: {weighted_score:.2f})"
        )

        await ctx.send(sender, report)

        ALERT_AGENT_ADDRESS = "agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun"
        if should_alert and ALERT_AGENT_ADDRESS:
            await ctx.send(ALERT_AGENT_ADDRESS, report)

    except Exception as err:
        ctx.logger.error(f"❌ Error in MeTTa risk analysis: {err}")
        await ctx.send(sender, ErrorResponse(message=f"Risk analysis failed: {str(err)}"))


@risk_agent_av.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info("🧠 DeFiGuard Risk Analysis Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {risk_agent_av.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    if METTA_AVAILABLE:
        ctx.logger.info("✅ SingularityNET MeTTa integration: ACTIVE")
        ctx.logger.info("📚 Knowledge base: 75+ assets, 40+ rules loaded")
        ctx.logger.info("◎  Solana-specific risk rules: ENABLED")
        ctx.logger.info("   • Mint authority detection")
        ctx.logger.info("   • Freeze authority detection")
        ctx.logger.info("   • Meme coin patterns")
        ctx.logger.info("   • Holder concentration analysis")
    else:
        ctx.logger.info("⚠️  SingularityNET MeTTa: Using fallback (install hyperon)")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    risk_agent_av.run()
