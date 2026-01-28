import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field

from .config import (
    SOLANA_FRAUD_INDICATORS,
    SOLANA_TOKENS,
    is_valid_solana_address
)
from .client import SolanaClient


@dataclass
class SolanaFraudReport:
    mint_address: str
    token_name: Optional[str]
    token_symbol: Optional[str]
    is_suspicious: bool
    risk_level: str  # safe, low, medium, high, critical
    risk_score: int  # 0-100
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SolanaFraudDetector:
    def __init__(self, client: Optional[SolanaClient] = None):
        self.client = client or SolanaClient()
        self.indicators = SOLANA_FRAUD_INDICATORS

    async def analyze_token(self, mint_address: str) -> SolanaFraudReport:
        if not is_valid_solana_address(mint_address):
            return SolanaFraudReport(
                mint_address=mint_address,
                token_name=None,
                token_symbol=None,
                is_suspicious=True,
                risk_level="critical",
                risk_score=100,
                findings=["❌ Invalid Solana address format"],
                recommendations=["Verify the token address is correct"]
            )

        findings = []
        risk_score = 0
        metadata = {}

        # Check 1: Mint Authority Status
        mint_info = await self._check_mint_authority(mint_address)
        findings.extend(mint_info["findings"])
        risk_score += mint_info["risk_score"]
        metadata["mint_authority"] = mint_info["data"]

        # Check 2: Token Metadata (name analysis)
        token_metadata = await self._check_token_metadata(mint_address)
        findings.extend(token_metadata["findings"])
        risk_score += token_metadata["risk_score"]
        metadata["token_info"] = token_metadata["data"]

        # Check 3: Holder Distribution
        distribution = await self._check_holder_distribution(mint_address)
        findings.extend(distribution["findings"])
        risk_score += distribution["risk_score"]
        metadata["distribution"] = distribution["data"]

        # Check 4: Liquidity Analysis
        liquidity = await self._check_liquidity(mint_address)
        findings.extend(liquidity["findings"])
        risk_score += liquidity["risk_score"]
        metadata["liquidity"] = liquidity["data"]

        # Check 5: Known Scam Database
        scam_check = await self._check_known_scams(mint_address)
        findings.extend(scam_check["findings"])
        risk_score += scam_check["risk_score"]

        risk_score = min(risk_score, 100)

        risk_level = self._calculate_risk_level(risk_score)

        recommendations = self._generate_recommendations(findings, risk_level)

        return SolanaFraudReport(
            mint_address=mint_address,
            token_name=metadata.get("token_info", {}).get("name"),
            token_symbol=metadata.get("token_info", {}).get("symbol"),
            is_suspicious=risk_score >= 40,
            risk_level=risk_level,
            risk_score=risk_score,
            findings=findings,
            recommendations=recommendations,
            metadata=metadata
        )

    async def _check_mint_authority(self, mint: str) -> Dict:
        findings = []
        risk_score = 0
        data = {}

        try:
            authority_info = await self.client.check_mint_authority(mint)
            data = authority_info

            if not authority_info.get("exists"):
                findings.append("❌ Token mint account does not exist")
                risk_score += 100
                return {"findings": findings, "risk_score": risk_score, "data": data}

            mint_authority = authority_info.get("mint_authority")
            if mint_authority and mint_authority != "null":
                findings.append("⚠️ Mint authority NOT revoked - can create more tokens")
                risk_score += 25
            else:
                findings.append("✅ Mint authority revoked")

            freeze_authority = authority_info.get("freeze_authority")
            if freeze_authority and freeze_authority != "null":
                findings.append("🚨 Freeze authority ACTIVE - can freeze your tokens")
                risk_score += 35
            else:
                findings.append("✅ Freeze authority revoked")

        except Exception as e:
            findings.append(f"⚠️ Could not verify mint authority: {str(e)[:50]}")
            risk_score += 15

        return {"findings": findings, "risk_score": risk_score, "data": data}

    async def _check_token_metadata(self, mint: str) -> Dict:
        findings = []
        risk_score = 0
        data = {"name": None, "symbol": None}

        for token_key, token_info in SOLANA_TOKENS.items():
            if token_info["mint"] == mint:
                data["name"] = token_info["name"]
                data["symbol"] = token_info["symbol"]
                findings.append(f"✅ Known token: {token_info['name']} ({token_info['symbol']})")
                return {"findings": findings, "risk_score": 0, "data": data}

        try:
            metadata = await self._fetch_token_metadata(mint)
            if metadata:
                data["name"] = metadata.get("name", "Unknown")
                data["symbol"] = metadata.get("symbol", "???")

                name_lower = data["name"].lower() if data["name"] else ""

                for keyword in self.indicators["suspicious_names"]:
                    if keyword in name_lower:
                        findings.append(f"⚠️ Suspicious keyword '{keyword}' in token name")
                        risk_score += 15

                if data["name"]:
                    special_chars = sum(1 for c in data["name"] if ord(c) > 127)
                    if special_chars > 3:
                        findings.append("⚠️ Excessive special characters/emojis in name")
                        risk_score += 10
            else:
                findings.append("⚠️ No metadata found - unverified token")
                risk_score += 20

        except Exception as e:
            findings.append(f"⚠️ Could not fetch token metadata: {str(e)[:50]}")
            risk_score += 10

        return {"findings": findings, "risk_score": risk_score, "data": data}

    async def _fetch_token_metadata(self, mint: str) -> Optional[Dict]:
        # Try Jupiter's token list (most comprehensive)
        try:
            url = f"https://token.jup.ag/strict"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        tokens = await response.json()
                        for token in tokens:
                            if token.get("address") == mint:
                                return {
                                    "name": token.get("name"),
                                    "symbol": token.get("symbol"),
                                    "decimals": token.get("decimals"),
                                    "verified": True
                                }
        except Exception:
            pass

        # Try Solana token list
        try:
            url = "https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        for token in data.get("tokens", []):
                            if token.get("address") == mint:
                                return {
                                    "name": token.get("name"),
                                    "symbol": token.get("symbol"),
                                    "decimals": token.get("decimals"),
                                    "verified": True
                                }
        except Exception:
            pass

        return None

    async def _check_holder_distribution(self, mint: str) -> Dict:
        findings = []
        risk_score = 0
        data = {}

        try:
            distribution = await self.client.get_holder_distribution(mint)
            data = distribution

            if "error" in distribution:
                findings.append(f"⚠️ {distribution['error']}")
                risk_score += 20
                return {"findings": findings, "risk_score": risk_score, "data": data}

            top_holder_percent = distribution.get("top_holder_percent", 0)
            top_10_percent = distribution.get("top_10_percent", 0)

            if top_holder_percent > 50:
                findings.append(f"🚨 CRITICAL: Top holder owns {top_holder_percent:.1f}% - extreme rug pull risk")
                risk_score += 40
            elif top_holder_percent > 30:
                findings.append(f"⚠️ Top holder owns {top_holder_percent:.1f}% - high concentration")
                risk_score += 25
            elif top_holder_percent > 20:
                findings.append(f"⚠️ Top holder owns {top_holder_percent:.1f}% - moderate concentration")
                risk_score += 15
            else:
                findings.append(f"✅ Top holder owns {top_holder_percent:.1f}% - healthy distribution")

            if top_10_percent > 80:
                findings.append(f"⚠️ Top 10 holders own {top_10_percent:.1f}% of supply")
                risk_score += 15

        except Exception as e:
            findings.append(f"⚠️ Could not analyze holder distribution: {str(e)[:50]}")
            risk_score += 10

        return {"findings": findings, "risk_score": risk_score, "data": data}

    async def _check_liquidity(self, mint: str) -> Dict:
        findings = []
        risk_score = 0
        data = {"pools_found": 0, "total_liquidity_usd": 0}

        try:
            liquidity_info = await self._fetch_jupiter_liquidity(mint)

            if liquidity_info:
                data["pools_found"] = liquidity_info.get("pool_count", 0)
                data["total_liquidity_usd"] = liquidity_info.get("liquidity_usd", 0)

                if data["pools_found"] == 0:
                    findings.append("🚨 No liquidity pools found - cannot trade")
                    risk_score += 50
                elif data["total_liquidity_usd"] < self.indicators["min_liquidity_usd"]:
                    findings.append(f"⚠️ Very low liquidity: ${data['total_liquidity_usd']:,.0f}")
                    risk_score += 30
                else:
                    findings.append(f"✅ Liquidity found: ${data['total_liquidity_usd']:,.0f}")
            else:
                findings.append("⚠️ Could not verify liquidity")
                risk_score += 15

        except Exception as e:
            findings.append(f"⚠️ Liquidity check failed: {str(e)[:50]}")
            risk_score += 10

        return {"findings": findings, "risk_score": risk_score, "data": data}

    async def _fetch_jupiter_liquidity(self, mint: str) -> Optional[Dict]:
        try:
            # Jupiter quote API to check if token is tradeable
            url = f"https://quote-api.jup.ag/v6/quote"
            params = {
                "inputMint": mint,
                "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                "amount": "1000000",  # 1 unit
                "slippageBps": "100"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "pool_count": len(data.get("routePlan", [])),
                            "liquidity_usd": 10000,  # Estimate if tradeable
                            "tradeable": True
                        }
                    else:
                        return {"pool_count": 0, "liquidity_usd": 0, "tradeable": False}
        except Exception:
            return None

    async def _check_known_scams(self, mint: str) -> Dict:
        findings = []
        risk_score = 0

        try:
            rugcheck_result = await self._check_rugcheck(mint)
            if rugcheck_result:
                if rugcheck_result.get("is_scam"):
                    findings.append("🚨 FLAGGED AS SCAM on RugCheck")
                    risk_score += 100
                elif rugcheck_result.get("risk_level") == "danger":
                    findings.append("🚨 RugCheck: DANGER level risk")
                    risk_score += 50
                elif rugcheck_result.get("risk_level") == "warn":
                    findings.append("⚠️ RugCheck: WARNING level risk")
                    risk_score += 25
                else:
                    findings.append("✅ RugCheck: No major issues found")
        except Exception as e:
            findings.append(f"⚠️ RugCheck unavailable: {str(e)[:30]}")

        return {"findings": findings, "risk_score": risk_score, "data": {}}

    async def _check_rugcheck(self, mint: str) -> Optional[Dict]:
        try:
            url = f"https://api.rugcheck.xyz/v1/tokens/{mint}/report"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()

                        risks = data.get("risks", [])
                        risk_level = "good"

                        for risk in risks:
                            level = risk.get("level", "")
                            if level == "danger":
                                risk_level = "danger"
                                break
                            elif level == "warn" and risk_level != "danger":
                                risk_level = "warn"

                        return {
                            "is_scam": False,
                            "risk_level": risk_level,
                            "risks": risks
                        }
        except Exception:
            pass

        return None

    def _calculate_risk_level(self, risk_score: int) -> str:
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

    def _generate_recommendations(self, findings: List[str], risk_level: str) -> List[str]:
        recommendations = []

        if risk_level == "critical":
            recommendations.append("🚨 DO NOT INVEST - Critical fraud indicators detected")
            recommendations.append("If you own this token, consider exiting immediately")
        elif risk_level == "high":
            recommendations.append("⚠️ HIGH RISK - Avoid this token")
            recommendations.append("Multiple red flags detected - not recommended")
        elif risk_level == "medium":
            recommendations.append("⚠️ CAUTION - Proceed with extreme care")
            recommendations.append("Only invest what you can afford to lose")
        elif risk_level == "low":
            recommendations.append("Some concerns identified - do your own research")
            recommendations.append("Check community feedback and verify team")
        else:
            recommendations.append("✅ No major red flags detected")
            recommendations.append("Always DYOR - even for safe-looking tokens")

        findings_text = " ".join(findings).lower()

        if "mint authority" in findings_text and "not revoked" in findings_text:
            recommendations.append("⚠️ Mint authority active - unlimited supply risk")

        if "freeze authority" in findings_text and "active" in findings_text:
            recommendations.append("🚨 Your tokens can be frozen at any time")

        if "concentration" in findings_text or "top holder" in findings_text:
            recommendations.append("High holder concentration = dump/rug pull risk")

        if "liquidity" in findings_text and ("low" in findings_text or "no" in findings_text):
            recommendations.append("Low liquidity = difficulty exiting position")

        return recommendations


async def test_fraud_detector():
    detector = SolanaFraudDetector()

    # Test with BONK (known meme coin)
    test_mint = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"

    print(f"Testing fraud detection for: {test_mint}")

    report = await detector.analyze_token(test_mint)

    print(f"\nToken: {report.token_name} ({report.token_symbol})")
    print(f"Risk Level: {report.risk_level.upper()}")
    print(f"Risk Score: {report.risk_score}/100")
    print(f"Suspicious: {report.is_suspicious}")

    print("\nFindings:")
    for finding in report.findings:
        print(f"  {finding}")

    print("\nRecommendations:")
    for rec in report.recommendations:
        print(f"  {rec}")


if __name__ == "__main__":
    asyncio.run(test_fraud_detector())
