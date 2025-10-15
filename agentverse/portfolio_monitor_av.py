from uagents import Agent, Context, Model
from datetime import datetime, timezone
from typing import List, Dict, Optional
from web3 import Web3
from requests.exceptions import ConnectionError, ReadTimeout
from web3.exceptions import BadFunctionCallOutput, ContractLogicError
import aiohttp
import asyncio
import re


class Portfolio(Model):
    user_id: str
    wallets: List[str]
    chains: List[str]
    timestamp: str


class AssetBalance(Model):
    token: str
    balance: float
    value_usd: float
    chain: str
    price: float
    change_24h: float


class PortfolioSnapshot(Model):
    user_id: str
    total_value_usd: float
    assets: List[Dict]
    timestamp: str
    risk_score: float


class MessageResponse(Model):
    message: str


portfolio_agent = Agent(
    name="portfolio_monitor",
    mailbox=True
)

print(f"Portfolio Monitor Agent Address: {portfolio_agent.address}")

CHAIN_CONFIG = {
    "ethereum": {
        "name": "Ethereum",
        "rpc": [
            "https://eth.llamarpc.com",
            "https://rpc.ankr.com/eth",
            "https://ethereum.publicnode.com"
        ],
        "native_token": "ethereum",
        "native_symbol": "ETH",
        "chain_id": 1,
        "explorer": "https://etherscan.io"
    },
    "bsc": {
        "name": "BNB Smart Chain",
        "rpc": [
            "https://bsc-dataseed.binance.org",
            "https://rpc.ankr.com/bsc",
            "https://bsc.publicnode.com"
        ],
        "native_token": "binancecoin",
        "native_symbol": "BNB",
        "chain_id": 56,
        "explorer": "https://bscscan.com"
    },
    "polygon": {
        "name": "Polygon",
        "rpc": [
            "https://polygon-rpc.com",
            "https://rpc.ankr.com/polygon",
            "https://polygon.llamarpc.com"
        ],
        "native_token": "matic-network",
        "native_symbol": "MATIC",
        "chain_id": 137,
        "explorer": "https://polygonscan.com"
    },
    "arbitrum": {
        "name": "Arbitrum One",
        "rpc": [
            "https://arb1.arbitrum.io/rpc",
            "https://rpc.ankr.com/arbitrum",
            "https://arbitrum.llamarpc.com"
        ],
        "native_token": "ethereum",
        "native_symbol": "ETH",
        "chain_id": 42161,
        "explorer": "https://arbiscan.io"
    },
    "optimism": {
        "name": "Optimism",
        "rpc": [
            "https://mainnet.optimism.io",
            "https://rpc.ankr.com/optimism",
            "https://optimism.llamarpc.com"
        ],
        "native_token": "ethereum",
        "native_symbol": "ETH",
        "chain_id": 10,
        "explorer": "https://optimistic.etherscan.io"
    },
    "avalanche": {
        "name": "Avalanche C-Chain",
        "rpc": [
            "https://api.avax.network/ext/bc/C/rpc",
            "https://rpc.ankr.com/avalanche",
            "https://avalanche.public-rpc.com"
        ],
        "native_token": "avalanche-2",
        "native_symbol": "AVAX",
        "chain_id": 43114,
        "explorer": "https://snowtrace.io"
    },
    "base": {
        "name": "Base",
        "rpc": [
            "https://mainnet.base.org",
            "https://base.llamarpc.com",
            "https://rpc.ankr.com/base"
        ],
        "native_token": "ethereum",
        "native_symbol": "ETH",
        "chain_id": 8453,
        "explorer": "https://basescan.org"
    },
    "fantom": {
        "name": "Fantom",
        "rpc": [
            "https://rpc.ftm.tools",
            "https://rpc.ankr.com/fantom",
            "https://fantom.publicnode.com"
        ],
        "native_token": "fantom",
        "native_symbol": "FTM",
        "chain_id": 250,
        "explorer": "https://ftmscan.com"
    },
    "gnosis": {
        "name": "Gnosis Chain",
        "rpc": [
            "https://rpc.gnosischain.com",
            "https://rpc.ankr.com/gnosis",
            "https://gnosis.publicnode.com"
        ],
        "native_token": "xdai",
        "native_symbol": "XDAI",
        "chain_id": 100,
        "explorer": "https://gnosisscan.io"
    },
    "moonbeam": {
        "name": "Moonbeam",
        "rpc": [
            "https://rpc.api.moonbeam.network",
            "https://moonbeam.public.blastapi.io"
        ],
        "native_token": "moonbeam",
        "native_symbol": "GLMR",
        "chain_id": 1284,
        "explorer": "https://moonscan.io"
    },
    "celo": {
        "name": "Celo",
        "rpc": [
            "https://forno.celo.org",
            "https://rpc.ankr.com/celo"
        ],
        "native_token": "celo",
        "native_symbol": "CELO",
        "chain_id": 42220,
        "explorer": "https://celoscan.io"
    },
    "cronos": {
        "name": "Cronos",
        "rpc": [
            "https://evm.cronos.org",
            "https://cronos.publicnode.com"
        ],
        "native_token": "crypto-com-chain",
        "native_symbol": "CRO",
        "chain_id": 25,
        "explorer": "https://cronoscan.com"
    }
}


def get_supported_chains() -> List[str]:
    return list(CHAIN_CONFIG.keys())


def validate_chain(chain: str) -> bool:
    return chain.lower() in CHAIN_CONFIG


def validate_wallet_address(address: str) -> Dict:
    if not isinstance(address, str):
        return {"valid": False, "error": "Address must be a string"}

    address = address.strip()

    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return {
            "valid": False,
            "error": "Invalid format. EVM address must be 0x followed by 40 hex characters"
        }

    try:
        checksum_address = Web3.to_checksum_address(address)

        if checksum_address == "0x0000000000000000000000000000000000000000":
            return {"valid": False, "error": "Cannot use zero address"}

        return {
            "valid": True,
            "checksum": checksum_address,
            "error": None
        }
    except Exception as e:
        return {"valid": False, "error": f"Invalid address: {str(e)}"}


async def get_working_rpc(chain: str) -> Optional[str]:
    config = CHAIN_CONFIG.get(chain.lower())
    if not config:
        return None

    for rpc_url in config["rpc"]:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 10}))
            if web3.is_connected():
                # Test with a simple call
                await asyncio.to_thread(lambda: web3.eth.block_number)
                return rpc_url
        except (ConnectionError, ReadTimeout, aiohttp.ClientError, ValueError) as e:
            # Connection errors, bad responses, or malformed URLs
            print(f"[WARN] RPC check failed for {rpc_url}: {e}")
            continue

    return None


async def fetch_token_price(token_id: str) -> Dict:
    """Fetch token price from CoinGecko API with retry logic"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": token_id.lower(),
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        token_data = data.get(token_id.lower(), {})
                        return {
                            "price": token_data.get("usd", 0),
                            "change_24h": token_data.get("usd_24h_change", 0),
                            "success": True
                        }
                    elif response.status == 429:  # Rate limit
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
        except Exception as e:
            print(f"⚠️ Price fetch error for {token_id}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue

    return {"price": 0, "change_24h": 0, "success": False}


async def get_wallet_balance(ctx: Context, wallet: str, chain: str) -> List[Dict]:
    """Get real wallet balances using Web3 with fallback RPC"""

    # Validate chain
    if not validate_chain(chain):
        raise ValueError(f"Unsupported chain: {chain}")

    # Validate and get checksum address
    validation = validate_wallet_address(wallet)
    if not validation["valid"]:
        raise ValueError(f"Invalid wallet address: {validation['error']}")

    wallet_checksum = validation["checksum"]
    chain_lower = chain.lower()
    config = CHAIN_CONFIG[chain_lower]

    # Get working RPC endpoint
    rpc_url = await get_working_rpc(chain_lower)
    if not rpc_url:
        raise ConnectionError(f"Unable to connect to any {config['name']} RPC")

    ctx.logger.info(f"🔗 Connected to {config['name']} via {rpc_url[:50]}...")

    web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 15}))

    # Get native token balance
    try:
        native_balance_wei = await asyncio.to_thread(
            lambda: web3.eth.get_balance(wallet_checksum)
        )
        native_balance = float(web3.from_wei(native_balance_wei, "ether"))
    except Exception as e:
        ctx.logger.error(f"Error getting native balance: {e}")
        native_balance = 0.0

    balances = [{
        "token": config["native_token"],
        "symbol": config["native_symbol"],
        "balance": native_balance,
        "chain": chain_lower
    }]

    # Common stablecoin addresses across chains
    stablecoins = {
        "ethereum": {
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F"
        },
        "bsc": {
            "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
            "USDT": "0x55d398326f99059fF775485246999027B3197955",
            "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
        },
        "polygon": {
            "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
            "DAI": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063"
        },
        "arbitrum": {
            "USDC": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
            "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
        },
        "optimism": {
            "USDC": "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
            "USDT": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58"
        },
        "avalanche": {
            "USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
            "USDT": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7"
        },
        "base": {
            "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        }
    }

    # ERC20 ABI for balanceOf
    erc20_abi = [{
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }, {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }]

    # Fetch stablecoin balances if available for this chain
    if chain_lower in stablecoins:
        for symbol, address in stablecoins[chain_lower].items():
            try:
                contract = web3.eth.contract(
                    address=Web3.to_checksum_address(address),
                    abi=erc20_abi
                )

                # Get balance
                token_balance_raw = await asyncio.to_thread(
                    lambda: contract.functions.balanceOf(wallet_checksum).call()
                )

                # Get decimals
                try:
                    decimals = await asyncio.to_thread(lambda: contract.functions.decimals().call())
                except (BadFunctionCallOutput, ContractLogicError, ValueError) as e:
                    ctx.logger.warning(f"Error fetching decimals for {symbol}: {e}")
                    decimals = 6 if symbol in ["USDC", "USDT"] else 18

                token_balance = token_balance_raw / (10 ** decimals)

                if token_balance > 0.01:
                    balances.append({
                        "token": symbol.lower(),
                        "symbol": symbol,
                        "balance": token_balance,
                        "chain": chain_lower
                    })

            except Exception as e:
                ctx.logger.warning(f"Could not fetch {symbol} balance: {e}")
                continue

    # Fetch USD prices for all tokens
    enriched_balances = []
    for asset in balances:
        price_data = await fetch_token_price(asset["token"])

        value_usd = asset["balance"] * price_data["price"]

        if value_usd > 0.01 or asset["symbol"] == config["native_symbol"]:
            ctx.logger.info(
                f"[{config['name']}] {asset['symbol']}: "
                f"{asset['balance']:.4f} = ${value_usd:.2f} "
                f"({price_data['change_24h']:.2f}%)"
            )

            enriched_balances.append({
                "token": asset["symbol"],
                "balance": asset["balance"],
                "price": price_data["price"],
                "value_usd": value_usd,
                "change_24h": price_data["change_24h"],
                "chain": asset["chain"]
            })

    return enriched_balances


def calculate_risk_score(assets: List[Dict]) -> float:
    """Calculate comprehensive risk score"""
    if not assets:
        return 0.0

    total_value = sum(a["value_usd"] for a in assets)
    if total_value == 0:
        return 0.0

    # Concentration risk (Herfindahl-Hirschman Index)
    concentration = sum((a["value_usd"] / total_value) ** 2 for a in assets)

    # Volatility risk
    avg_volatility = sum(abs(a.get("change_24h", 0)) for a in assets) / len(assets)
    volatility_score = min(avg_volatility / 20, 1)

    # Chain diversification risk
    unique_chains = len(set(a["chain"] for a in assets))
    chain_diversity_score = 1.0 if unique_chains == 1 else max(0.0, 1.0 - (unique_chains / 5.0))

    # Combined risk score
    risk_score = (
            concentration * 0.35 +
            volatility_score * 0.45 +
            chain_diversity_score * 0.20
    )

    return min(risk_score, 1.0)


async def add_portfolio_key(ctx: Context, key: str):
    """Add portfolio key to the master list"""
    keys = ctx.storage.get("portfolio_keys") or []
    if key not in keys:
        keys.append(key)
        ctx.storage.set("portfolio_keys", keys)


async def get_all_portfolios(ctx: Context) -> Dict[str, dict]:
    """Fetch all portfolios"""
    keys = ctx.storage.get("portfolio_keys") or []
    portfolios = {}
    for key in keys:
        value = ctx.storage.get(key)
        if value:
            portfolios[key] = value
    return portfolios


@portfolio_agent.on_message(model=Portfolio)
async def register_portfolio(ctx: Context, sender: str, msg: Portfolio):
    """Register a new portfolio for monitoring"""
    ctx.logger.info(f"📝 Registering portfolio for user: {msg.user_id}")

    invalid_wallets = []
    valid_wallets = []

    for wallet in msg.wallets:
        validation = validate_wallet_address(wallet)
        if validation["valid"]:
            valid_wallets.append(validation["checksum"])
        else:
            invalid_wallets.append(f"{wallet}: {validation['error']}")

    if invalid_wallets:
        error_msg = "Invalid wallet address(es):\n" + "\n".join(invalid_wallets)
        await ctx.send(sender, MessageResponse(message=error_msg))
        return

    # Validate all chains
    invalid_chains = [c for c in msg.chains if not validate_chain(c)]
    if invalid_chains:
        supported = ", ".join(get_supported_chains())
        error_msg = (
            f"Unsupported chain(s): {', '.join(invalid_chains)}\n"
            f"Supported chains: {supported}"
        )
        await ctx.send(sender, MessageResponse(message=error_msg))
        return

    # Store portfolio
    portfolio_key = f"portfolio_{msg.user_id}"
    ctx.storage.set(portfolio_key, {
        "wallets": valid_wallets,
        "chains": [c.lower() for c in msg.chains],
        "registered_at": msg.timestamp,
        "owner": sender
    })

    await add_portfolio_key(ctx, portfolio_key)

    chain_names = [CHAIN_CONFIG[c.lower()]["name"] for c in msg.chains]
    await ctx.send(
        sender,
        MessageResponse(
            message=f"✅ Portfolio registered: {len(valid_wallets)} wallet(s) on {len(chain_names)} chain(s)"
        )
    )

    await scan_portfolio(ctx, msg.user_id)


async def scan_portfolio(ctx: Context, user_id: str):
    """Scan portfolio and create snapshot"""
    portfolio = ctx.storage.get(f"portfolio_{user_id}")
    if not portfolio:
        ctx.logger.warning(f"Portfolio {user_id} not found")
        return None

    all_assets = []
    total_value = 0
    failed_scans = []

    for wallet in portfolio["wallets"]:
        for chain in portfolio["chains"]:
            try:
                ctx.logger.info(f"🔍 Scanning {wallet[:10]}... on {CHAIN_CONFIG[chain]['name']}")
                balances = await get_wallet_balance(ctx, wallet, chain)
                all_assets.extend(balances)
                total_value += sum(b["value_usd"] for b in balances)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                error_msg = f"{wallet[:10]}... on {chain}"
                failed_scans.append(error_msg)
                ctx.logger.error(f"❌ Error scanning {error_msg}: {e}")

    if failed_scans:
        ctx.logger.warning(f"Failed to scan: {', '.join(failed_scans)}")

    risk_score = calculate_risk_score(all_assets)

    snapshot = PortfolioSnapshot(
        user_id=user_id,
        total_value_usd=total_value,
        assets=all_assets,
        timestamp=datetime.now(timezone.utc).isoformat(),
        risk_score=risk_score
    )

    user_snapshots = ctx.storage.get(f"snapshots_{user_id}") or []
    user_snapshots.append(snapshot.dict())
    ctx.storage.set(f"snapshots_{user_id}", user_snapshots[-10:])  # Keep last 10

    ctx.logger.info(
        f"📊 Snapshot: ${total_value:.2f} across {len(set(a['chain'] for a in all_assets))} chains, "
        f"Risk: {risk_score:.2%}"
    )

    risk_agent_address = "agent1qwwc3jwx0x6z0sk07029n9ngztsrapcc0ngdwy8swzq50tt7t0nf726tmkm"
    if risk_agent_address and total_value > 0:
        await ctx.send(risk_agent_address, snapshot)

    return snapshot


@portfolio_agent.on_interval(period=300.0)
async def monitor_portfolios(ctx: Context):
    """Periodically scan all registered portfolios"""
    portfolios = await get_all_portfolios(ctx)

    if not portfolios:
        return

    ctx.logger.info(f"🔄 Monitoring {len(portfolios)} portfolio(s)...")

    for key, _ in portfolios.items():
        user_id = key.replace("portfolio_", "")
        try:
            await scan_portfolio(ctx, user_id)
            await asyncio.sleep(5)
        except Exception as e:
            ctx.logger.error(f"Error monitoring {user_id}: {e}")


@portfolio_agent.on_event("startup")
async def startup(ctx: Context):
    portfolios = await get_all_portfolios(ctx)
    supported_chains = get_supported_chains()

    ctx.logger.info("=" * 70)
    ctx.logger.info("🛡️  DeFiGuard Portfolio Monitor Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {portfolio_agent.address}")
    ctx.logger.info(f"📊 Loaded {len(portfolios)} portfolio(s) from storage")
    ctx.logger.info(f"🔗 Supporting {len(supported_chains)} chains:")
    for i, chain in enumerate(supported_chains, 1):
        ctx.logger.info(f"   {i}. {CHAIN_CONFIG[chain]['name']}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("=" * 70)


if __name__ == "__main__":
    portfolio_agent.run()
