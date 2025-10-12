from uagents import Agent, Context, Model
from datetime import datetime, timezone
from typing import List, Dict


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
    mailbox=True  # type: ignore[arg-type]
)

print(f"Fraud Detection Agent Address: {fraud_agent.address}")

# Known scam patterns and red flags
SCAM_INDICATORS = {
    "honeypot_keywords": ["safemoon", "elon", "baby", "inu", "cum", "safe", "moon"],
    "suspicious_names": ["v2", "v3", "fork", "copy", "clone"],
    "high_tax_threshold": 10,  # Over 10% tax is suspicious
}


async def check_token_security(token_address: str, chain: str) -> Dict:
    """
    Check token for common security issues
    NOTE: Using simulated data for demo
    In production, integrate with GoPlus Security API, Honeypot.is, etc.
    """

    print(f"Token Address: {token_address}")
    print(f"Chain: {chain}")

    findings = []
    risk_score = 0

    # Simulation data for demo purposes
    # In production, query actual blockchain/security APIs

    # Check 1: Token age
    token_age_days = 30  # Simulated
    if token_age_days < 7:
        findings.append("Token is very new (less than 7 days old)")
        risk_score += 20

    # Check 2: Liquidity
    liquidity_usd = 50000  # Simulated
    if liquidity_usd < 10000:
        findings.append(f"Low liquidity (${liquidity_usd:,.2f})")
        risk_score += 15

    # Check 3: Holder concentration
    top_holder_percent = 45  # Simulated
    if top_holder_percent > 50:
        findings.append(f"Top holder owns {top_holder_percent}% of supply")
        risk_score += 25
    elif top_holder_percent > 30:
        findings.append(f"High concentration: Top holder owns {top_holder_percent}%")
        risk_score += 15

    # Check 4: Contract verification
    is_verified = True  # Simulated
    if not is_verified:
        findings.append("Contract is not verified on block explorer")
        risk_score += 30

    # Check 5: Ownership renounced
    ownership_renounced = False  # Simulated
    if not ownership_renounced:
        findings.append("Contract ownership not renounced - centralization risk")
        risk_score += 10

    # Check 6: Trading tax analysis
    buy_tax = 5  # Simulated
    sell_tax = 8  # Simulated

    if buy_tax > SCAM_INDICATORS["high_tax_threshold"]:
        findings.append(f"High buy tax: {buy_tax}%")
        risk_score += 15

    if sell_tax > SCAM_INDICATORS["high_tax_threshold"]:
        findings.append(f"High sell tax: {sell_tax}%")
        risk_score += 15

    if sell_tax > buy_tax * 2:
        findings.append("Sell tax significantly higher than buy tax")
        risk_score += 20

    # Check 7: Honeypot detection (CRITICAL)
    is_honeypot = False  # Simulated
    if is_honeypot:
        findings.append("🚨 HONEYPOT DETECTED - Cannot sell tokens")
        risk_score = 100  # Maximum risk

    return {
        "findings": findings,
        "risk_score": min(risk_score, 100),
        "token_age_days": token_age_days,
        "liquidity_usd": liquidity_usd,
        "top_holder_percent": top_holder_percent,
        "is_verified": is_verified,
        "ownership_renounced": ownership_renounced,
        "buy_tax": buy_tax,
        "sell_tax": sell_tax,
        "is_honeypot": is_honeypot
    }


def analyze_token_name(token_address: str) -> Dict:
    """
    Analyze token name for scam indicators
    NOTE: Using simulated data for demo
    """

    print(f"Token Address: {token_address}")

    # In production, fetch actual token name/symbol from blockchain
    token_name = "SafeMoonRocket"  # Simulated
    token_symbol = "SMR"  # Simulated

    findings = []
    risk_score = 0

    name_lower = token_name.lower()

    # Check for suspicious keywords
    for keyword in SCAM_INDICATORS["honeypot_keywords"]:
        if keyword in name_lower:
            findings.append(f"Suspicious keyword '{keyword}' in token name")
            risk_score += 10

    # Check for suspicious patterns
    for pattern in SCAM_INDICATORS["suspicious_names"]:
        if pattern in name_lower:
            findings.append(f"Token name contains '{pattern}' - possible clone/fork")
            risk_score += 5

    # Check for excessive emojis or special characters
    emoji_count = sum(1 for char in token_name if ord(char) > 127)
    if emoji_count > 3:
        findings.append("Excessive emojis/special characters in name")
        risk_score += 5

    return {
        "findings": findings,
        "risk_score": risk_score,
        "token_name": token_name,
        "token_symbol": token_symbol
    }


def calculate_risk_level(risk_score: int) -> str:
    """Convert risk score to risk level"""
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
    """Generate recommendations based on findings"""
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

    # Specific recommendations based on findings
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

    return recommendations


@fraud_agent.on_message(model=TokenAnalysisRequest)
async def analyze_token(ctx: Context, sender: str, msg: TokenAnalysisRequest):
    """Perform comprehensive fraud analysis on a token"""
    ctx.logger.info(f"🔍 Analyzing token {msg.token_address} on {msg.chain}")

    try:
        # Run security checks
        security_analysis = await check_token_security(msg.token_address, msg.chain)

        # Analyze token name
        name_analysis = analyze_token_name(msg.token_address)

        # Combine findings
        all_findings = security_analysis["findings"] + name_analysis["findings"]

        # Calculate total risk score
        total_risk_score = security_analysis["risk_score"] + name_analysis["risk_score"]
        risk_level = calculate_risk_level(total_risk_score)

        # Generate recommendations
        recommendations = generate_recommendations(all_findings, risk_level)

        # Determine if suspicious
        is_suspicious = total_risk_score >= 40

        # Create report
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

        # Send report
        await ctx.send(sender, report)

        # If critical, alert the Alert Agent
        if risk_level == "critical":
            ctx.logger.warning(f"🚨 CRITICAL FRAUD DETECTED: {msg.token_address}")
            alert_agent_address = "agent1qftjr2fh4uuk0se60sp6e6yevamtlmh5tlsjxx9ny2kgenggf089unxed9f"
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
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    fraud_agent.run()
