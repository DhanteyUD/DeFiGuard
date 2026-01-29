import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solana.client import SolanaClient
from solana.fraud_detector import SolanaFraudDetector
from solana.config import (
    is_valid_solana_address,
    SOLANA_TOKENS,
    SOLANA_PROGRAMS
)


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(test_name: str, passed: bool, details: str = ""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"       {details}")


async def test_address_validation():
    print_header("TEST 1: Address Validation")

    # Valid addresses
    valid_addresses = [
        "9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY",  # Standard
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC mint
        "So11111111111111111111111111111111111111112",  # Wrapped SOL
    ]

    # Invalid addresses
    invalid_addresses = [
        "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",  # EVM address
        "invalid_address",
        "too_short",
        "",
    ]

    all_passed = True

    for addr in valid_addresses:
        result = is_valid_solana_address(addr)
        passed = result == True
        all_passed = all_passed and passed
        print_result(f"Valid: {addr[:20]}...", passed)

    for addr in invalid_addresses:
        result = is_valid_solana_address(addr)
        passed = result == False
        all_passed = all_passed and passed
        print_result(f"Invalid: {addr[:20] if addr else '(empty)'}...", passed)

    return all_passed


async def test_solana_client_connection():
    print_header("TEST 2: Solana RPC Connection")

    client = SolanaClient()

    try:
        # Test with known address
        test_address = "9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY"
        balance = await client.get_sol_balance(test_address)

        print_result("RPC Connection", True, f"Balance: {balance:.4f} SOL")
        return True
    except Exception as e:
        print_result("RPC Connection", False, str(e))
        return False


async def test_wallet_snapshot():
    print_header("TEST 3: Wallet Snapshot")

    client = SolanaClient()

    # Use a known active wallet (Solana Foundation)
    test_address = "9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY"

    try:
        snapshot = await client.get_wallet_snapshot(test_address)

        print_result("Snapshot Creation", True)
        print(f"       Address: {snapshot.address[:20]}...")
        print(f"       SOL Balance: {snapshot.sol_balance:.4f}")
        print(f"       SOL Value: ${snapshot.sol_value_usd:,.2f}")
        print(f"       Token Count: {len(snapshot.tokens)}")
        print(f"       Total Value: ${snapshot.total_value_usd:,.2f}")

        return True
    except Exception as e:
        print_result("Snapshot Creation", False, str(e))
        return False


async def test_mint_authority_check():
    print_header("TEST 4: Mint Authority Check")

    client = SolanaClient()

    # Test USDC (should have specific authority setup)
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    try:
        authority_info = await client.check_mint_authority(usdc_mint)

        print_result("Mint Authority Query", True)
        print(f"       Exists: {authority_info.get('exists')}")
        print(
            f"       Mint Authority: {authority_info.get('mint_authority', 'None')[:20] if authority_info.get('mint_authority') else 'Revoked'}...")
        print(
            f"       Freeze Authority: {authority_info.get('freeze_authority', 'None')[:20] if authority_info.get('freeze_authority') else 'Revoked'}...")

        return True
    except Exception as e:
        print_result("Mint Authority Query", False, str(e))
        return False


async def test_holder_distribution():
    print_header("TEST 5: Holder Distribution Analysis")

    client = SolanaClient()

    # Test with BONK (popular meme coin with many holders)
    bonk_mint = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"

    try:
        distribution = await client.get_holder_distribution(bonk_mint)

        if "error" not in distribution:
            print_result("Distribution Analysis", True)
            print(f"       Total Supply: {distribution['total_supply']:,.0f}")
            print(f"       Top Holder: {distribution['top_holder_percent']:.2f}%")
            print(f"       Top 10: {distribution['top_10_percent']:.2f}%")
            print(f"       Concentration Risk: {distribution['concentration_risk']}")
            return True
        else:
            print_result("Distribution Analysis", False, distribution.get("error"))
            return False
    except Exception as e:
        print_result("Distribution Analysis", False, str(e))
        return False


async def test_fraud_detector_known_token():
    print_header("TEST 6: Fraud Detection - Known Token (USDC)")

    detector = SolanaFraudDetector()
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    try:
        report = await detector.analyze_token(usdc_mint)

        expected_low_risk = report.risk_level in ["safe", "low"]

        print_result("Known Token Analysis", expected_low_risk)
        print(f"       Token: {report.token_name} ({report.token_symbol})")
        print(f"       Risk Level: {report.risk_level.upper()}")
        print(f"       Risk Score: {report.risk_score}/100")
        print(f"       Suspicious: {report.is_suspicious}")

        return expected_low_risk
    except Exception as e:
        print_result("Known Token Analysis", False, str(e))
        return False


async def test_fraud_detector_meme_coin():
    print_header("TEST 7: Fraud Detection - Meme Coin (BONK)")

    detector = SolanaFraudDetector()
    bonk_mint = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"

    try:
        report = await detector.analyze_token(bonk_mint)

        print_result("Meme Coin Analysis", True)
        print(f"       Token: {report.token_name} ({report.token_symbol})")
        print(f"       Risk Level: {report.risk_level.upper()}")
        print(f"       Risk Score: {report.risk_score}/100")
        print(f"       Suspicious: {report.is_suspicious}")

        if report.findings:
            print("       Findings:")
            for finding in report.findings[:3]:
                print(f"         - {finding}")

        return True
    except Exception as e:
        print_result("Meme Coin Analysis", False, str(e))
        return False


async def test_fraud_detector_invalid_address():
    print_header("TEST 8: Fraud Detection - Invalid Address")

    detector = SolanaFraudDetector()
    invalid_mint = "invalid_address_12345"

    try:
        report = await detector.analyze_token(invalid_mint)

        is_critical = report.risk_level == "critical"

        print_result("Invalid Address Handling", is_critical)
        print(f"       Risk Level: {report.risk_level.upper()}")
        print(f"       Findings: {report.findings[0] if report.findings else 'None'}")

        return is_critical
    except Exception as e:
        print_result("Invalid Address Handling", False, str(e))
        return False


async def test_token_config():
    print_header("TEST 9: Token Configuration")

    required_tokens = ["SOL", "USDC", "USDT", "RAY", "BONK"]

    all_present = True
    for token in required_tokens:
        present = token in SOLANA_TOKENS
        all_present = all_present and present
        print_result(f"Token: {token}", present)

    required_programs = ["token_program", "jupiter_aggregator", "raydium_amm"]
    for program in required_programs:
        present = program in SOLANA_PROGRAMS
        all_present = all_present and present
        print_result(f"Program: {program}", present)

    return all_present


async def run_all_tests():
    print("\n" + "🧪 " * 20)
    print("  DEFIGUARD SOLANA INTEGRATION TESTS")
    print("🧪 " * 20)

    results = [("Address Validation", await test_address_validation()),
               ("Token Configuration", await test_token_config()),
               ("RPC Connection", await test_solana_client_connection()),
               ("Wallet Snapshot", await test_wallet_snapshot()),
               ("Mint Authority", await test_mint_authority_check()),
               ("Holder Distribution", await test_holder_distribution()),
               ("Fraud - Known Token", await test_fraud_detector_known_token()),
               ("Fraud - Meme Coin", await test_fraud_detector_meme_coin()),
               ("Fraud - Invalid Address", await test_fraud_detector_invalid_address())]

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")

    print(f"\n  Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n  🎉 ALL TESTS PASSED! Solana integration is ready.")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Review the output above.")

    print("\n" + "=" * 60)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
