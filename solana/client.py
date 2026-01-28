import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass

from .config import (
    SolanaConfig,
    SolanaCluster,
    SOLANA_TOKENS,
    SOLANA_PROGRAMS,
    is_valid_solana_address,
    get_solana_rpc_url
)


@dataclass
class SolanaBalance:
    mint: str
    symbol: str
    name: str
    balance: float
    decimals: int
    value_usd: float
    price: float
    change_24h: float
    risk_level: str


@dataclass
class SolanaWalletSnapshot:
    address: str
    sol_balance: float
    sol_value_usd: float
    tokens: List[SolanaBalance]
    total_value_usd: float
    timestamp: str


class SolanaClient:
    def __init__(
            self,
            cluster: SolanaCluster = SolanaCluster.MAINNET,
            custom_rpc: Optional[str] = None
    ):
        self.cluster = cluster
        self.rpc_url = custom_rpc or get_solana_rpc_url(cluster)
        self.config = SolanaConfig()
        self._price_cache: Dict[str, Tuple[float, float, float]] = {}  # mint -> (price, change_24h, timestamp)
        self._cache_ttl = 60

    async def _rpc_request(
            self,
            method: str,
            params: List[Any] = None,
            timeout: int = 10
    ) -> Dict:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or []
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self.rpc_url,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "error" in data:
                            raise Exception(f"RPC Error: {data['error']}")
                        return data.get("result", {})
                    else:
                        raise Exception(f"HTTP {response.status}")
        except asyncio.TimeoutError:
            raise Exception(f"RPC timeout after {timeout}s")
        except Exception as e:
            raise Exception(f"RPC request failed: {str(e)}")

    async def get_sol_balance(self, address: str) -> float:
        if not is_valid_solana_address(address):
            raise ValueError(f"Invalid Solana address: {address}")

        result = await self._rpc_request("getBalance", [address])
        lamports = result.get("value", 0)
        return lamports / 1e9

    async def get_token_accounts(self, address: str) -> List[Dict]:
        if not is_valid_solana_address(address):
            raise ValueError(f"Invalid Solana address: {address}")

        params = [
            address,
            {"programId": SOLANA_PROGRAMS["token_program"]},
            {"encoding": "jsonParsed"}
        ]

        result = await self._rpc_request("getTokenAccountsByOwner", params)
        return result.get("value", [])

    async def get_token_balance(self, token_account: str) -> Dict:
        result = await self._rpc_request(
            "getTokenAccountBalance",
            [token_account]
        )
        return result.get("value", {})

    async def get_token_supply(self, mint: str) -> Dict:
        result = await self._rpc_request("getTokenSupply", [mint])
        return result.get("value", {})

    async def get_token_largest_accounts(self, mint: str, limit: int = 10) -> List[Dict]:
        result = await self._rpc_request(
            "getTokenLargestAccounts",
            [mint]
        )
        accounts = result.get("value", [])
        return accounts[:limit]

    async def get_account_info(self, address: str) -> Optional[Dict]:
        result = await self._rpc_request(
            "getAccountInfo",
            [address, {"encoding": "jsonParsed"}]
        )
        return result.get("value")

    async def _fetch_token_price(self, coingecko_id: str) -> Tuple[float, float]:
        cache_key = coingecko_id
        now = datetime.now(timezone.utc).timestamp()

        if cache_key in self._price_cache:
            price, change, cached_at = self._price_cache[cache_key]
            if now - cached_at < self._cache_ttl:
                return price, change

        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coingecko_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        token_data = data.get(coingecko_id, {})
                        price = token_data.get("usd", 0)
                        change = token_data.get("usd_24h_change", 0)

                        self._price_cache[cache_key] = (price, change, now)
                        return price, change
        except Exception as e:
            print(f"Price fetch error for {coingecko_id}: {e}")

        return 0, 0

    @staticmethod
    def _get_token_info(_self, mint: str) -> Optional[Dict]:
        for token_data in SOLANA_TOKENS.values():
            if token_data["mint"] == mint:
                return token_data
        return None

    async def get_wallet_snapshot(self, address: str) -> SolanaWalletSnapshot:
        if not is_valid_solana_address(address):
            raise ValueError(f"Invalid Solana address: {address}")

        sol_balance = await self.get_sol_balance(address)
        sol_price, sol_change = await self._fetch_token_price("solana")
        sol_value_usd = sol_balance * sol_price

        token_accounts = await self.get_token_accounts(address)

        tokens: List[SolanaBalance] = []
        total_value_usd = sol_value_usd

        for account in token_accounts:
            try:
                account_data = account.get("account", {}).get("data", {})
                parsed = account_data.get("parsed", {}).get("info", {})

                mint = parsed.get("mint", "")
                token_amount = parsed.get("tokenAmount", {})

                ui_amount = float(token_amount.get("uiAmount", 0) or 0)
                decimals = token_amount.get("decimals", 0)

                if ui_amount <= 0:
                    continue

                token_info = self._get_token_info(mint)

                if token_info:
                    price, change = await self._fetch_token_price(token_info["coingecko_id"])
                    value_usd = ui_amount * price

                    tokens.append(SolanaBalance(
                        mint=mint,
                        symbol=token_info["symbol"],
                        name=token_info["name"],
                        balance=ui_amount,
                        decimals=decimals,
                        value_usd=value_usd,
                        price=price,
                        change_24h=change,
                        risk_level=token_info["risk_level"]
                    ))
                    total_value_usd += value_usd
                else:
                    tokens.append(SolanaBalance(
                        mint=mint,
                        symbol="UNKNOWN",
                        name=f"Unknown Token ({mint[:8]}...)",
                        balance=ui_amount,
                        decimals=decimals,
                        value_usd=0,  # Can't price unknown tokens
                        price=0,
                        change_24h=0,
                        risk_level="unknown"
                    ))

                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Error processing token account: {e}")
                continue

        return SolanaWalletSnapshot(
            address=address,
            sol_balance=sol_balance,
            sol_value_usd=sol_value_usd,
            tokens=tokens,
            total_value_usd=total_value_usd,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    async def check_mint_authority(self, mint: str) -> Dict:
        account_info = await self.get_account_info(mint)

        if not account_info:
            return {"exists": False, "mint_authority": None, "freeze_authority": None}

        data = account_info.get("data", {})
        parsed = data.get("parsed", {}).get("info", {})

        return {
            "exists": True,
            "mint_authority": parsed.get("mintAuthority"),
            "freeze_authority": parsed.get("freezeAuthority"),
            "supply": parsed.get("supply", "0"),
            "decimals": parsed.get("decimals", 0),
            "is_initialized": parsed.get("isInitialized", False)
        }

    async def get_holder_distribution(self, mint: str) -> Dict:
        supply_info = await self.get_token_supply(mint)
        total_supply = float(supply_info.get("uiAmount", 0) or 0)

        if total_supply == 0:
            return {"error": "Zero supply token"}

        largest_accounts = await self.get_token_largest_accounts(mint, limit=10)

        holders = []
        cumulative_percent = 0

        for account in largest_accounts:
            ui_amount = float(account.get("uiAmount", 0) or 0)
            percent = (ui_amount / total_supply) * 100 if total_supply > 0 else 0
            cumulative_percent += percent

            holders.append({
                "address": account.get("address", ""),
                "amount": ui_amount,
                "percent": percent
            })

        top_holder_percent = holders[0]["percent"] if holders else 0
        top_10_percent = cumulative_percent

        return {
            "total_supply": total_supply,
            "holder_count": len(largest_accounts),
            "top_holder_percent": top_holder_percent,
            "top_10_percent": top_10_percent,
            "holders": holders,
            "concentration_risk": "critical" if top_holder_percent > 50 else (
                "high" if top_holder_percent > 30 else (
                    "medium" if top_holder_percent > 20 else "low"
                )
            )
        }


async def test_solana_client():
    client = SolanaClient()

    test_address = "9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY"

    print(f"Testing Solana client with address: {test_address}")

    try:
        balance = await client.get_sol_balance(test_address)
        print(f"SOL Balance: {balance:.4f}")

        snapshot = await client.get_wallet_snapshot(test_address)
        print(f"Total Value: ${snapshot.total_value_usd:,.2f}")
        print(f"Token Count: {len(snapshot.tokens)}")

    except Exception as e:
        print(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(test_solana_client())
