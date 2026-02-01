from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from datetime import datetime, timezone
from typing import List, Dict
import aiohttp
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solana.fraud_detector import SolanaFraudDetector
from solana.config import is_valid_solana_address

load_dotenv()


class TokenAnalysisRequest(Model):
    token_address: str
    chain: str


class FraudReport(Model):
    token_address: str
    chain: str
    is_suspicious: bool
    risk_level: str  # safe, low, medium, high, critical
    findings: List[str]
    recommendations: List[str]
    timestamp: str


class ErrorResponse(Model):
    error: str
    source: str
    timestamp: str


fraud_agent = Agent(
    name="fraud_detection",
    seed=os.getenv("FRAUD_AGENT_SEED", "fraud_agent_seed"),
    port=8004,
    mailbox=True,
    # endpoint=["https://defiguard-production.up.railway.app/submit"]
)

fund_agent_if_low(str(fraud_agent.wallet.address()))

print(f"Fraud Detection Agent (Solana Enhanced) Address: {fraud_agent.address}")

solana_fraud_detector = SolanaFraudDetector()

SCAM_INDICATORS = {
    "honeypot_keywords": ["safemoon", "elon", "baby", "inu", "cum", "safe", "moon"],
    "suspicious_names": ["v2", "v3", "fork", "copy", "clone"],
    "high_tax_threshold": 10,
}

GOPLUS_API_BASE = "https://api.gopluslabs.io/api/v1"
HONEYPOT_API_BASE = "https://api.honeypot.is/v2"

CHAIN_ID_MAP = {
    "ethereum": "1",
    "eth": "1",
    "bsc": "56",
    "binance": "56",
    "bnb": "56",
    "polygon": "137",
    "matic": "137",
    "arbitrum": "42161",
    "arb": "42161",
    "optimism": "10",
    "op": "10",
    "avalanche": "43114",
    "avax": "43114",
    "base": "8453",
    "fantom": "250",
    "ftm": "250",
    "gnosis": "100",
    "xdai": "100",
    "moonbeam": "1284",
    "glmr": "1284",
    "celo": "42220",
    "cronos": "25",
    "cro": "25"
}


def detect_chain_type(chain: str, token_address: str) -> str:
    """Detect if this is a Solana or EVM analysis request"""
    chain_lower = chain.lower()

    if chain_lower in ["solana", "sol"]:
        return "solana"

    if is_valid_solana_address(token_address):
        return "solana"

    return "evm"


# ============================================
# SOLANA FRAUD ANALYSIS
# ============================================

async def analyze_solana_token(token_address: str) -> FraudReport:
    report = await solana_fraud_detector.analyze_token(token_address)

    return FraudReport(
        token_address=token_address,
        chain="solana",
        is_suspicious=report.is_suspicious,
        risk_level=report.risk_level,
        findings=report.findings,
        recommendations=report.recommendations,
        timestamp=report.timestamp
    )


# ============================================
# EVM FRAUD ANALYSIS (Existing GoPlus integration)
# ============================================

async def fetch_goplus_security(token_address: str, chain: str) -> Dict:
    chain_id = CHAIN_ID_MAP.get(chain.lower(), "1")

    url = f"{GOPLUS_API_BASE}/token_security/{chain_id}"
    params = {"contract_addresses": token_address.lower()}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 1 and data.get("result"):
                        token_data = data["result"].get(token_address.lower(), {})
                        return token_data
                    return {}
                return {}
    except Exception as e:
        print(f"GoPlus API error: {e}")
        return {}


async def fetch_token_metadata(token_address: str, _chain: str) -> Dict:
    API_KEY = os.getenv("ETHERSCAN_API_KEY")
    base_url = "https://api.etherscan.io/api"

    params = {
        "module": "token",
        "action": "tokeninfo",
        "contractaddress": token_address,
        "apikey": API_KEY
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "1":
                        result = data.get("result", [{}])[0]
                        return {
                            "name": result.get("tokenName", "Unknown"),
                            "symbol": result.get("symbol", "???")
                        }
    except Exception as e:
        print(f"Metadata API error: {e}")

    return {"name": "Unknown", "symbol": "???"}


async def check_evm_token_security(token_address: str, chain: str) -> Dict:
    print(f"🔍 Checking EVM security for: {token_address} on {chain}")

    findings = []
    risk_score = 0

    goplus_data = await fetch_goplus_security(token_address, chain)

    if not goplus_data:
        findings.append("⚠️ Unable to fetch security data from GoPlus API")
        risk_score += 15
        return {
            "findings": findings,
            "risk_score": risk_score,
            "is_verified": None,
            "is_honeypot": None
        }

    # Contract verification
    is_open_source = goplus_data.get("is_open_source", "0") == "1"
    if not is_open_source:
        findings.append("❌ Contract source code not verified")
        risk_score += 30

    # Honeypot check
    is_honeypot = goplus_data.get("is_honeypot", "0") == "1"
    if is_honeypot:
        findings.append("🚨 HONEYPOT DETECTED - Cannot sell tokens")
        risk_score = 100

    # Ownership check
    owner_address = goplus_data.get("owner_address")
    if owner_address and owner_address != "0x0000000000000000000000000000000000000000":
        findings.append("⚠️ Contract ownership not renounced - centralization risk")
        risk_score += 10

    # Tax analysis
    buy_tax = float(goplus_data.get("buy_tax", "0")) * 100
    sell_tax = float(goplus_data.get("sell_tax", "0")) * 100

    if buy_tax > SCAM_INDICATORS["high_tax_threshold"]:
        findings.append(f"💸 High buy tax: {buy_tax:.1f}%")
        risk_score += 15

    if sell_tax > SCAM_INDICATORS["high_tax_threshold"]:
        findings.append(f"💸 High sell tax: {sell_tax:.1f}%")
        risk_score += 15

    if sell_tax > buy_tax * 2 and sell_tax > 5:
        findings.append("⚠️ Sell tax significantly higher than buy tax")
        risk_score += 20

    # Holder analysis
    holder_count = int(goplus_data.get("holder_count", "0"))
    if holder_count < 100:
        findings.append(f"⚠️ Low holder count: {holder_count}")
        risk_score += 15

    # Dangerous functions
    if goplus_data.get("can_take_back_ownership", "0") == "1":
        findings.append("🚨 Owner can take back ownership")
        risk_score += 30

    if goplus_data.get("hidden_owner", "0") == "1":
        findings.append("🚨 Hidden owner detected")
        risk_score += 25

    if goplus_data.get("selfdestruct", "0") == "1":
        findings.append("🚨 Contract has selfdestruct function")
        risk_score += 40

    if goplus_data.get("is_blacklisted", "0") == "1":
        findings.append("🚨 Blacklist function exists")
        risk_score += 20

    # Holder concentration
    holders = goplus_data.get("holders", [])
    if holders and len(holders) > 0:
        top_holder_percent = float(holders[0].get("percent", 0)) * 100
        if top_holder_percent > 50:
            findings.append(f"⚠️ Top holder owns {top_holder_percent:.1f}% of supply")
            risk_score += 25
        elif top_holder_percent > 30:
            findings.append(f"⚠️ High concentration: Top holder owns {top_holder_percent:.1f}%")
            risk_score += 15

    return {
        "findings": findings,
        "risk_score": min(risk_score, 100),
        "is_verified": is_open_source,
        "is_honeypot": is_honeypot
    }


async def analyze_token_name(token_address: str, chain: str) -> Dict:
    metadata = await fetch_token_metadata(token_address, chain)
    token_name = metadata.get("name", "Unknown")

    findings = []
    risk_score = 0

    name_lower = token_name.lower()

    for keyword in SCAM_INDICATORS["honeypot_keywords"]:
        if keyword in name_lower:
            findings.append(f"⚠️ Suspicious keyword '{keyword}' in token name")
            risk_score += 10

    for pattern in SCAM_INDICATORS["suspicious_names"]:
        if pattern in name_lower:
            findings.append(f"⚠️ Token name contains '{pattern}' - possible clone/fork")
            risk_score += 5

    return {
        "findings": findings,
        "risk_score": risk_score,
        "token_name": token_name
    }


def calculate_risk_level(risk_score: int) -> str:
    if risk_score >= 80:
        return "critical"
    elif risk_score >= 60:
        return "high"
    elif risk_score >= 40:
        return "medium"
    elif risk_score >= 20:
        return "low"
    else:
        return "safe"


def generate_recommendations(findings: List[str], risk_level: str) -> List[str]:
    recommendations = []

    if risk_level == "critical":
        recommendations.append("🚨 DO NOT INVEST - Critical fraud indicators detected")
        recommendations.append("If you already own this token, attempt to exit immediately")
    elif risk_level == "high":
        recommendations.append("⚠️ HIGH RISK - Avoid this token")
        recommendations.append("Multiple red flags detected")
    elif risk_level == "medium":
        recommendations.append("⚠️ CAUTION - Proceed with extreme caution")
        recommendations.append("Only invest what you can afford to lose")
    elif risk_level == "low":
        recommendations.append("Some concerns identified - due diligence recommended")
    else:
        recommendations.append("✅ No major red flags detected")
        recommendations.append("Always conduct your own research (DYOR)")

    finding_text = " ".join(findings).lower()

    if "honeypot" in finding_text:
        recommendations.append("⚠️ HONEYPOT - you CANNOT sell these tokens")

    if "concentration" in finding_text or "holder" in finding_text:
        recommendations.append("High holder concentration = dump risk")

    if "mint authority" in finding_text and "not revoked" in finding_text:
        recommendations.append("⚠️ Unlimited supply risk - mint authority active")

    if "freeze" in finding_text:
        recommendations.append("🚨 Your tokens can be frozen at any time")

    return recommendations


async def analyze_evm_token(token_address: str, chain: str) -> FraudReport:
    security_analysis = await check_evm_token_security(token_address, chain)
    name_analysis = await analyze_token_name(token_address, chain)

    all_findings = security_analysis["findings"] + name_analysis["findings"]
    total_risk_score = security_analysis["risk_score"] + name_analysis["risk_score"]
    risk_level = calculate_risk_level(total_risk_score)
    recommendations = generate_recommendations(all_findings, risk_level)

    return FraudReport(
        token_address=token_address,
        chain=chain,
        is_suspicious=total_risk_score >= 40,
        risk_level=risk_level,
        findings=all_findings,
        recommendations=recommendations,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@fraud_agent.on_message(model=TokenAnalysisRequest)
async def analyze_token(ctx: Context, sender: str, msg: TokenAnalysisRequest):
    ctx.logger.info(f"🔍 Analyzing token {msg.token_address} on {msg.chain}")

    try:
        chain_type = detect_chain_type(msg.chain, msg.token_address)

        if chain_type == "solana":
            ctx.logger.info("◎ Detected Solana token - using Solana fraud detector")
            report = await analyze_solana_token(msg.token_address)
        else:
            ctx.logger.info("⟠ Detected EVM token - using GoPlus security API")
            report = await analyze_evm_token(msg.token_address, msg.chain)

        ctx.logger.info(
            f"✅ Analysis complete: {report.risk_level} risk "
            f"(suspicious: {report.is_suspicious})"
        )

        await ctx.send(sender, report)

        # Alert on critical risks
        if report.risk_level == "critical":
            ctx.logger.warning(f"🚨 CRITICAL FRAUD DETECTED: {msg.token_address}")

            ALERT_AGENT_ADDRESS = os.getenv("ALERT_AGENT_ADDRESS")
            if ALERT_AGENT_ADDRESS:
                await ctx.send(ALERT_AGENT_ADDRESS, report)

    except Exception as e:
        ctx.logger.error(f"❌ Error in fraud analysis: {e}")
        error_msg = ErrorResponse(
            error=str(e),
            source="fraud_detection_agent",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        await ctx.send(sender, error_msg)


@fraud_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info("🕵️  DeFiGuard Fraud Detection (Solana Enhanced)")
    ctx.logger.info(f"📍 Agent Address: {fraud_agent.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("🔍 Ready to analyze tokens for fraud indicators")
    ctx.logger.info("")
    ctx.logger.info("📡 Connected APIs:")
    ctx.logger.info("   ◎  Solana: RugCheck.xyz, Jupiter, Metaplex")
    ctx.logger.info("   ⟠  EVM: GoPlus Security, Honeypot.is")
    ctx.logger.info("")
    ctx.logger.info("🔗 Supported Chains:")
    ctx.logger.info("   Solana + 12 EVM chains")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    fraud_agent.run()
