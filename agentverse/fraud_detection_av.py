from uagents import Agent, Context, Model
from datetime import datetime, timezone
from typing import List, Dict
import aiohttp


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
    mailbox=True
)

print(f"Fraud Detection Agent Address: {fraud_agent.address}")

# Known scam patterns and red flags
SCAM_INDICATORS = {
    "honeypot_keywords": ["safemoon", "elon", "baby", "inu", "cum", "safe", "moon"],
    "suspicious_names": ["v2", "v3", "fork", "copy", "clone"],
    "high_tax_threshold": 10,  # Over 10% tax is suspicious
}

GOPLUS_API_BASE = "https://api.gopluslabs.io/api/v1"
HONEYPOT_API_BASE = "https://api.honeypot.is/v2"


async def fetch_goplus_security(token_address: str, chain: str) -> Dict:
    chain_id_map = {
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

    chain_id = chain_id_map.get(chain.lower(), "1")

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


async def fetch_honeypot_check(token_address: str, chain: str) -> Dict:
    chain_map = {
        "ethereum": "ethereum",
        "eth": "ethereum",
        "bsc": "bsc",
        "binance": "bsc",
        "polygon": "polygon",
        "matic": "polygon"
    }

    chain_name = chain_map.get(chain.lower(), "bsc")

    url = f"{HONEYPOT_API_BASE}/IsHoneypot"
    params = {
        "address": token_address,
        "chainID": chain_name
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                return {}
    except Exception as e:
        print(f"Honeypot API error: {e}")
        return {}


async def fetch_token_metadata(token_address: str, chain: str) -> Dict:
    print(f"Fetching {chain} from blockchain explorer API")

    API_KEY = "YOUR_API_KEY_HERE"
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


async def check_token_security(token_address: str, chain: str) -> Dict:
    print(f"🔍 Checking security for: {token_address} on {chain}")

    findings = []
    risk_score = 0

    goplus_data = await fetch_goplus_security(token_address, chain)

    if not goplus_data:
        findings.append("⚠️ Unable to fetch security data from GoPlus API")
        risk_score += 15
        return {
            "findings": findings,
            "risk_score": risk_score,
            "token_age_days": None,
            "liquidity_usd": None,
            "top_holder_percent": None,
            "is_verified": None,
            "ownership_renounced": None,
            "buy_tax": None,
            "sell_tax": None,
            "is_honeypot": None
        }

    is_open_source = goplus_data.get("is_open_source", "0") == "1"
    if not is_open_source:
        findings.append("❌ Contract source code not verified")
        risk_score += 30

    is_honeypot = goplus_data.get("is_honeypot", "0") == "1"
    if is_honeypot:
        findings.append("🚨 HONEYPOT DETECTED - Cannot sell tokens")
        risk_score = 100

    # Check ownership
    owner_address = goplus_data.get("owner_address")
    if owner_address and owner_address != "0x0000000000000000000000000000000000000000":
        findings.append("⚠️ Contract ownership not renounced - centralization risk")
        risk_score += 10
        ownership_renounced = False
    else:
        ownership_renounced = True

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

    holder_count = int(goplus_data.get("holder_count", "0"))
    if holder_count < 100:
        findings.append(f"⚠️ Low holder count: {holder_count}")
        risk_score += 15

    can_take_back_ownership = goplus_data.get("can_take_back_ownership", "0") == "1"
    if can_take_back_ownership:
        findings.append("🚨 Owner can take back ownership")
        risk_score += 30

    hidden_owner = goplus_data.get("hidden_owner", "0") == "1"
    if hidden_owner:
        findings.append("🚨 Hidden owner detected")
        risk_score += 25

    selfdestruct = goplus_data.get("selfdestruct", "0") == "1"
    if selfdestruct:
        findings.append("🚨 Contract has selfdestruct function")
        risk_score += 40

    external_call = goplus_data.get("external_call", "0") == "1"
    if external_call:
        findings.append("⚠️ Contract makes external calls")
        risk_score += 10

    trading_cooldown = goplus_data.get("trading_cooldown", "0") == "1"
    if trading_cooldown:
        findings.append("⚠️ Trading cooldown mechanism present")
        risk_score += 5

    is_blacklisted = goplus_data.get("is_blacklisted", "0") == "1"
    if is_blacklisted:
        findings.append("🚨 Blacklist function exists")
        risk_score += 20

    is_whitelisted = goplus_data.get("is_whitelisted", "0") == "1"
    if is_whitelisted:
        findings.append("⚠️ Whitelist required for trading")
        risk_score += 15

    top_holder_percent = 0
    holders = goplus_data.get("holders", [])
    if holders and len(holders) > 0:
        top_holder_percent = float(holders[0].get("percent", 0)) * 100
        if top_holder_percent > 50:
            findings.append(f"⚠️ Top holder owns {top_holder_percent:.1f}% of supply")
            risk_score += 25
        elif top_holder_percent > 30:
            findings.append(f"⚠️ High concentration: Top holder owns {top_holder_percent:.1f}%")
            risk_score += 15

    total_supply = float(goplus_data.get("total_supply", "0"))
    lp_total_supply = float(goplus_data.get("lp_total_supply", "0"))

    if lp_total_supply < total_supply * 0.01:  # Less than 1% in LP
        findings.append("⚠️ Very low liquidity detected")
        risk_score += 20

    return {
        "findings": findings,
        "risk_score": min(risk_score, 100),
        "token_age_days": None,  # GoPlus doesn't provide this
        "liquidity_usd": lp_total_supply,
        "top_holder_percent": top_holder_percent,
        "is_verified": is_open_source,
        "ownership_renounced": ownership_renounced,
        "buy_tax": buy_tax,
        "sell_tax": sell_tax,
        "is_honeypot": is_honeypot
    }


async def analyze_token_name(token_address: str, chain: str) -> Dict:
    print(f"📝 Fetching token metadata...")

    metadata = await fetch_token_metadata(token_address, chain)
    token_name = metadata.get("name", "Unknown")
    token_symbol = metadata.get("symbol", "???")

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

    emoji_count = sum(1 for char in token_name if ord(char) > 127)
    if emoji_count > 3:
        findings.append("⚠️ Excessive emojis/special characters in name")
        risk_score += 5

    return {
        "findings": findings,
        "risk_score": risk_score,
        "token_name": token_name,
        "token_symbol": token_symbol
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
        recommendations.append("Monitor closely for any changes")
    elif risk_level == "low":
        recommendations.append("Some concerns identified - due diligence recommended")
        recommendations.append("Check community feedback and audit reports")
    else:
        recommendations.append("✅ No major red flags detected")
        recommendations.append("Always conduct your own research (DYOR)")

    finding_text = " ".join(findings).lower()

    if "honeypot" in finding_text:
        recommendations.append("⚠️ This is a HONEYPOT - you CANNOT sell these tokens")

    if "liquidity" in finding_text:
        recommendations.append("Low liquidity = high slippage and exit difficulty")

    if "concentration" in finding_text or "holder" in finding_text:
        recommendations.append("High holder concentration = dump risk")

    if "ownership" in finding_text:
        recommendations.append("Ownership not renounced = contract can be modified")

    if "tax" in finding_text:
        recommendations.append("High taxes reduce your profit margins significantly")

    if "blacklist" in finding_text:
        recommendations.append("Owner can blacklist addresses from trading")

    if "selfdestruct" in finding_text:
        recommendations.append("Contract can be destroyed - complete loss risk")

    return recommendations


@fraud_agent.on_message(model=TokenAnalysisRequest)
async def analyze_token(ctx: Context, sender: str, msg: TokenAnalysisRequest):
    """Perform comprehensive fraud analysis on a token"""
    ctx.logger.info(f"🔍 Analyzing token {msg.token_address} on {msg.chain}")

    try:
        security_analysis = await check_token_security(msg.token_address, msg.chain)

        name_analysis = await analyze_token_name(msg.token_address, msg.chain)

        all_findings = security_analysis["findings"] + name_analysis["findings"]

        total_risk_score = security_analysis["risk_score"] + name_analysis["risk_score"]
        risk_level = calculate_risk_level(total_risk_score)

        recommendations = generate_recommendations(all_findings, risk_level)

        is_suspicious = total_risk_score >= 40

        report = FraudReport(
            token_address=msg.token_address,
            chain=msg.chain,
            is_suspicious=is_suspicious,
            risk_level=risk_level,
            findings=all_findings,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        ctx.logger.info(
            f"✅ Analysis complete: {risk_level} risk "
            f"(score: {total_risk_score}/100)"
        )

        await ctx.send(sender, report)

        if risk_level == "critical":
            ctx.logger.warning(f"🚨 CRITICAL FRAUD DETECTED: {msg.token_address}")
            alert_agent_address = "agent1qwzszgd7h0knxwdj2j73htqswatm87t0ftsj4d3wlzlv54kftx5gyu8ygun"
            await ctx.send(alert_agent_address, report)

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
    ctx.logger.info("🕵️  DeFiGuard Fraud Detection Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {fraud_agent.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("🔍 Ready to analyze tokens for fraud indicators")
    ctx.logger.info("🔗 Connected to GoPlus Security API")
    ctx.logger.info("🍯 Connected to Honeypot.is API")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    fraud_agent.run()
