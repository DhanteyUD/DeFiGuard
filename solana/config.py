from typing import List
from dataclasses import dataclass
from enum import Enum


class SolanaCluster(Enum):
    MAINNET = "mainnet-beta"
    DEVNET = "devnet"
    TESTNET = "testnet"


@dataclass
class SolanaConfig:
    name: str = "Solana"
    native_token: str = "solana"
    native_symbol: str = "SOL"
    decimals: int = 9
    explorer: str = "https://solscan.io"

    rpc_endpoints: List[str] = None

    def __post_init__(self):
        if self.rpc_endpoints is None:
            self.rpc_endpoints = [
                "https://api.mainnet-beta.solana.com",
                "https://solana-api.projectserum.com",
                "https://rpc.ankr.com/solana",
                "https://solana.public-rpc.com",
            ]


SOLANA_PROGRAMS = {
    # Token Programs
    "token_program": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
    "token_2022": "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
    "associated_token": "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL",

    # DeFi Protocols
    "raydium_amm": "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    "orca_whirlpool": "whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc",
    "jupiter_aggregator": "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
    "marinade_finance": "MarBmsSgKXdrN1egZf5sqe1TMai9K1rChYNDJgjq7aD",

    # Lending Protocols
    "solend": "So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo",
    "mango_v4": "4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg",

    # NFT Programs
    "metaplex": "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s",
}

# Known Solana token addresses for risk classification
SOLANA_TOKENS = {
    # Native & Wrapped
    "SOL": {
        "mint": "So11111111111111111111111111111111111111112",
        "name": "Solana",
        "symbol": "SOL",
        "decimals": 9,
        "risk_level": "low",
        "coingecko_id": "solana"
    },

    # Major Stablecoins
    "USDC": {
        "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "name": "USD Coin",
        "symbol": "USDC",
        "decimals": 6,
        "risk_level": "low",
        "coingecko_id": "usd-coin"
    },
    "USDT": {
        "mint": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        "name": "Tether USD",
        "symbol": "USDT",
        "decimals": 6,
        "risk_level": "low",
        "coingecko_id": "tether"
    },

    # Major DeFi Tokens
    "RAY": {
        "mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        "name": "Raydium",
        "symbol": "RAY",
        "decimals": 6,
        "risk_level": "medium",
        "coingecko_id": "raydium"
    },
    "ORCA": {
        "mint": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
        "name": "Orca",
        "symbol": "ORCA",
        "decimals": 6,
        "risk_level": "medium",
        "coingecko_id": "orca"
    },
    "JUP": {
        "mint": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
        "name": "Jupiter",
        "symbol": "JUP",
        "decimals": 6,
        "risk_level": "medium",
        "coingecko_id": "jupiter-exchange-solana"
    },
    "MNDE": {
        "mint": "MNDEFzGvMt87ueuHvVU9VcTqsAP5b3fTGPsHuuPA5ey",
        "name": "Marinade",
        "symbol": "MNDE",
        "decimals": 9,
        "risk_level": "medium",
        "coingecko_id": "marinade"
    },

    # Meme Coins (Higher Risk)
    "BONK": {
        "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "name": "Bonk",
        "symbol": "BONK",
        "decimals": 5,
        "risk_level": "high",
        "coingecko_id": "bonk"
    },
    "WIF": {
        "mint": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "name": "dogwifhat",
        "symbol": "WIF",
        "decimals": 6,
        "risk_level": "high",
        "coingecko_id": "dogwifcoin"
    },
}

SOLANA_FRAUD_INDICATORS = {
    # Token metadata red flags
    "suspicious_names": [
        "safe", "moon", "elon", "baby", "inu", "shib",
        "pepe", "doge", "floki", "cum", "porn", "xxx"
    ],

    # Mint authority concerns
    "mint_authority_active": True,
    "freeze_authority_active": True,

    # Supply concerns
    "low_holder_count": 100,
    "high_concentration_threshold": 0.50,

    # Liquidity concerns
    "min_liquidity_usd": 10000,
    "min_pool_age_hours": 24,
}


def get_solana_rpc_url(cluster: SolanaCluster = SolanaCluster.MAINNET) -> str:
    urls = {
        SolanaCluster.MAINNET: "https://api.mainnet-beta.solana.com",
        SolanaCluster.DEVNET: "https://api.devnet.solana.com",
        SolanaCluster.TESTNET: "https://api.testnet.solana.com",
    }
    return urls.get(cluster, urls[SolanaCluster.MAINNET])


def is_valid_solana_address(address: str) -> bool:
    import re
    if not isinstance(address, str):
        return False

    base58_pattern = r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'
    return bool(re.match(base58_pattern, address))


def get_token_risk_level(mint_address: str) -> str:
    for token_data in SOLANA_TOKENS.values():
        if token_data["mint"] == mint_address:
            return token_data["risk_level"]
    return "unknown"
