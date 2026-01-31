from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    StartSessionContent,
    EndSessionContent,
    chat_protocol_spec,
)
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from typing import List, Dict

from web3 import Web3
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, BadRequestError
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
import re
import os
from dotenv import load_dotenv

load_dotenv()


class PingMessage(Model):
    text: str
    timestamp: str


class AlertNotification(Model):
    user_id: str
    overall_risk: str
    risk_score: float
    concerns: List[str]
    recommendations: List[str]
    timestamp: str


class Portfolio(Model):
    user_id: str
    wallets: List[str]
    chains: List[str]
    timestamp: str


class ChatWrapper(Model):
    message: ChatMessage


class Acknowledgement(Model):
    message: str


class ChatAckWrapper(Model):
    acknowledged_msg_id: str
    timestamp: str


class InteractionPing(Model):
    text: str
    timestamp: str
    interaction_id: str


def log_interaction(ctx: Context, sender: str, message_type: str):
    count = ctx.storage.get("total_interactions") or 0
    count += 1
    ctx.storage.set("total_interactions", count)

    user_count = ctx.storage.get(f"user_interactions_{sender}") or 0
    user_count += 1
    ctx.storage.set(f"user_interactions_{sender}", user_count)

    ctx.logger.info("🔔" * 25)
    ctx.logger.info(f"📊 INTERACTION #{count}")
    ctx.logger.info(f"👤 User: {sender[:8]}...")
    ctx.logger.info(f"📝 Type: {message_type}")
    ctx.logger.info(f"📈 User Total: {user_count}")
    ctx.logger.info("🔔" * 25)


client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key=os.getenv("ASI_ONE_API_KEY"),
)

alert_agent = Agent(
    name="alert_agent",
    seed=os.getenv("ALERT_AGENT_SEED", "alert_agent_seed"),
    port=8002,
    mailbox=True,
    publish_agent_details=True,
    # endpoint=[os.getenv("DEFIGUARD_ENDPOINT", "")],
    # mailbox=os.getenv("ALERT_AGENT_MAILBOX"),  # type: ignore
    readme_path="README.md",
)

fund_agent_if_low(str(alert_agent.wallet.address()))

print(f"Alert Agent Address: {alert_agent.address}")
print(f"Alert Agent Mailbox: {os.getenv('ALERT_AGENT_MAILBOX', 'Not configured')}")

PORTFOLIO_AGENT_ADDRESS = os.getenv("PORTFOLIO_AGENT_ADDRESS")


@alert_agent.on_message(model=InteractionPing)
async def handle_interaction_ping(ctx: Context, sender: str, msg: InteractionPing):
    log_interaction(ctx, sender, "InteractionPing")

    await ctx.send(
        sender,
        InteractionPing(
            text=f"Acknowledged: {msg.text}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            interaction_id=msg.interaction_id
        )
    )


chat_proto = Protocol(spec=chat_protocol_spec)

SUPPORTED_CHAINS = {
    # Solana
    "solana": "Solana",
    "sol": "Solana",

    # EVM Chains
    "ethereum": "Ethereum",
    "eth": "Ethereum",
    "bsc": "BNB Smart Chain",
    "bnb": "BNB Smart Chain",
    "polygon": "Polygon",
    "matic": "Polygon",
    "arbitrum": "Arbitrum One",
    "arb": "Arbitrum One",
    "optimism": "Optimism",
    "op": "Optimism",
    "avalanche": "Avalanche C-Chain",
    "avax": "Avalanche C-Chain",
    "base": "Base",
    "fantom": "Fantom",
    "ftm": "Fantom",
    "gnosis": "Gnosis Chain",
    "xdai": "Gnosis Chain",
    "moonbeam": "Moonbeam",
    "glmr": "Moonbeam",
    "celo": "Celo",
    "cronos": "Cronos",
    "cro": "Cronos"
}

CHAIN_CANONICAL = {
    "sol": "solana",
    "eth": "ethereum",
    "bnb": "bsc",
    "matic": "polygon",
    "arb": "arbitrum",
    "op": "optimism",
    "avax": "avalanche",
    "ftm": "fantom",
    "xdai": "gnosis",
    "glmr": "moonbeam",
    "cro": "cronos"
}

CHAIN_TYPES = {
    "solana": "solana",
    "ethereum": "evm",
    "bsc": "evm",
    "polygon": "evm",
    "arbitrum": "evm",
    "optimism": "evm",
    "avalanche": "evm",
    "base": "evm",
    "fantom": "evm",
    "gnosis": "evm",
    "moonbeam": "evm",
    "celo": "evm",
    "cronos": "evm"
}

DIRECT_COMMANDS = ["register", "chains", "portfolio", "status", "history", "help", "analyze"]


def is_valid_solana_address(address: str) -> bool:
    if not isinstance(address, str):
        return False

    base58_pattern = r'^[1-9A-HJ-NP-Za-km-z]{32,44}$'
    return bool(re.match(base58_pattern, address))


def detect_address_type(address: str) -> str:
    """Detect if address is EVM (0x...) or Solana (base58)"""
    if not isinstance(address, str):
        return "unknown"

    address = address.strip()

    if address.startswith("0x") and len(address) == 42:
        return "evm"
    elif is_valid_solana_address(address):
        return "solana"
    else:
        return "unknown"


def validate_wallet_address(address: str) -> Dict:
    if not isinstance(address, str):
        return {"valid": False, "error": "Address must be a string", "checksum": None, "type": None}

    address = address.strip()
    addr_type = detect_address_type(address)

    # ===== SOLANA VALIDATION =====
    if addr_type == "solana":
        if is_valid_solana_address(address):
            return {
                "valid": True,
                "checksum": address,
                "error": None,
                "type": "solana"
            }
        else:
            return {
                "valid": False,
                "error": "Invalid Solana address format",
                "checksum": None,
                "type": "solana"
            }

    # ===== EVM VALIDATION =====
    elif addr_type == "evm":
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            if not address.startswith("0x"):
                return {
                    "valid": False,
                    "error": "EVM address must start with '0x'",
                    "checksum": None,
                    "type": "evm"
                }
            elif len(address) != 42:
                return {
                    "valid": False,
                    "error": f"EVM address must be 42 characters (currently {len(address)})",
                    "checksum": None,
                    "type": "evm"
                }
            else:
                return {
                    "valid": False,
                    "error": "Address contains invalid characters (only 0-9, a-f, A-F allowed)",
                    "checksum": None,
                    "type": "evm"
                }

        try:
            checksum_address = Web3.to_checksum_address(address)

            if checksum_address == "0x0000000000000000000000000000000000000000":
                return {
                    "valid": False,
                    "error": "Cannot use zero address (0x0000...)",
                    "checksum": None,
                    "type": "evm"
                }

            burn_addresses = [
                "0x000000000000000000000000000000000000dEaD",
                "0xdead000000000000000042069420694206942069"
            ]
            if checksum_address.lower() in [b.lower() for b in burn_addresses]:
                return {
                    "valid": False,
                    "error": "Cannot use burn address",
                    "checksum": None,
                    "type": "evm"
                }

            return {
                "valid": True,
                "checksum": checksum_address,
                "error": None,
                "type": "evm"
            }
        except ValueError as e:
            return {
                "valid": False,
                "error": f"Invalid checksum: {str(e)}",
                "checksum": None,
                "type": "evm"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "checksum": None,
                "type": "evm"
            }

    # ===== UNKNOWN FORMAT =====
    else:
        return {
            "valid": False,
            "error": "Unknown address format. Use EVM (0x...) or Solana (base58) address",
            "checksum": None,
            "type": None
        }


def add_alert_key(ctx: Context, key: str):
    keys = ctx.storage.get("alert_keys") or []
    if key not in keys:
        keys.append(key)
        ctx.storage.set("alert_keys", keys)


def get_all_alerts(ctx: Context) -> Dict[str, dict]:
    keys = ctx.storage.get("alert_keys") or []
    alerts = {}
    for key in keys:
        value = ctx.storage.get(key)
        if value:
            alerts[key] = value
    return alerts


def add_active_session(ctx: Context, user_id: str, address: str):
    sessions = ctx.storage.get("active_sessions") or {}
    sessions[user_id] = address
    ctx.storage.set("active_sessions", sessions)


def remove_active_session(ctx: Context, user_id: str):
    sessions = ctx.storage.get("active_sessions") or {}
    if user_id in sessions:
        del sessions[user_id]
        ctx.storage.set("active_sessions", sessions)


def get_active_sessions(ctx: Context) -> Dict[str, str]:
    return ctx.storage.get("active_sessions") or {}


def get_user_portfolio(ctx: Context, user_id: str) -> Dict:
    return ctx.storage.get(f"user_portfolio_{user_id}")


def save_user_portfolio(ctx: Context, user_id: str, wallets: List[str], chains: List[str], wallet_type: str):
    portfolio_data = {
        "wallets": wallets,
        "chains": chains,
        "wallet_type": wallet_type,
        "registered_at": datetime.now(timezone.utc).isoformat()
    }
    ctx.storage.set(f"user_portfolio_{user_id}", portfolio_data)


def validate_chain(chain: str) -> Dict:
    chain_lower = chain.strip().lower()

    if chain_lower in SUPPORTED_CHAINS:
        canonical = CHAIN_CANONICAL.get(chain_lower, chain_lower)
        return {
            "valid": True,
            "chain_name": SUPPORTED_CHAINS[chain_lower],
            "chain_key": canonical,
            "chain_type": CHAIN_TYPES.get(canonical, "evm"),
            "error": None
        }
    else:
        suggestions = []
        for supported_chain in SUPPORTED_CHAINS.keys():
            if chain_lower in supported_chain or supported_chain in chain_lower:
                suggestions.append(supported_chain)

        error_msg = f"Unsupported chain: '{chain}'"
        if suggestions:
            error_msg += f". Did you mean: {', '.join(suggestions)}?"

        return {
            "valid": False,
            "chain_name": None,
            "chain_key": None,
            "chain_type": None,
            "error": error_msg
        }


def parse_register_command(text: str) -> Dict:
    text = text.strip()

    # EVM address pattern
    evm_pattern = r'(0x[a-fA-F0-9]{40})'
    # Solana address pattern (base58, 32-44 chars)
    solana_pattern = r'\b([1-9A-HJ-NP-Za-km-z]{32,44})\b'

    evm_match = re.search(evm_pattern, text)
    solana_match = None

    if not evm_match:
        solana_match = re.search(solana_pattern, text)

    # Determine wallet from matches
    wallet = None
    if evm_match:
        wallet = evm_match.group(1)
    elif solana_match:
        wallet = solana_match.group(1)

    if not wallet:
        parts = text.split()

        # Find "register" and get the next word as potential wallet
        for i, part in enumerate(parts):
            if part.lower() == "register" and i + 1 < len(parts):
                potential_wallet = parts[i + 1]
                potential_wallet = potential_wallet.rstrip('.,;:!?')
                if potential_wallet.startswith("0x") or is_valid_solana_address(potential_wallet):
                    wallet = potential_wallet
                    break

        if not wallet:
            for part in parts:
                part = part.rstrip('.,;:!?')
                if part.startswith("0x") and len(part) >= 42:
                    wallet = part[:42]
                    break
                elif is_valid_solana_address(part):
                    wallet = part
                    break

    if not wallet:
        return {
            "valid": False,
            "error": (
                "**Could not find a valid wallet address.**\n\n"
                "Use:\n"
                "`register <wallet_address> <chains>`\n\n"
                "**EVM Example:**\n"
                "`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon`\n\n"
                "**Solana Example:**\n"
                "`register 9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY solana`"
            )
        }

    wallet_validation = validate_wallet_address(wallet)
    if not wallet_validation["valid"]:
        return {
            "valid": False,
            "error": f"❌ {wallet_validation['error']}"
        }

    wallet_type = wallet_validation["type"]  # "solana" or "evm"

    text_without_wallet = text.replace(wallet, " ")

    chain_keywords = list(SUPPORTED_CHAINS.keys())

    found_chains = []
    text_lower = text_without_wallet.lower()

    for chain in chain_keywords:
        if re.search(r'\b' + re.escape(chain) + r'\b', text_lower):
            found_chains.append(chain)

    if not found_chains:
        parts = text_without_wallet.strip().split()
        for part in parts:
            part_clean = part.lower().rstrip('.,;:!?').lstrip('.,;:!?')
            # Handle comma-separated
            if "," in part_clean:
                for sub_part in part_clean.split(","):
                    sub_part = sub_part.strip()
                    if sub_part in SUPPORTED_CHAINS:
                        found_chains.append(sub_part)
            elif part_clean in SUPPORTED_CHAINS:
                found_chains.append(part_clean)

    found_chains = list(dict.fromkeys(found_chains))

    valid_chains = []
    for chain in found_chains:
        chain_validation = validate_chain(chain)
        if chain_validation["valid"]:
            valid_chains.append(chain_validation["chain_key"])

    valid_chains = list(dict.fromkeys(valid_chains))

    if not valid_chains:
        if wallet_type == "solana":
            valid_chains = ["solana"]
        else:
            return {
                "valid": False,
                "error": (
                    "**Please specify which chains to monitor.**\n\n"
                    f"Your wallet: `{wallet[:10]}...{wallet[-6:]}`\n\n"
                    "**Example:**\n"
                    f"`register {wallet} ethereum,polygon,arbitrum`\n\n"
                    "**Available EVM chains:** ethereum, bsc, polygon, arbitrum, optimism, avalanche, base, fantom, gnosis, moonbeam, celo, cronos"
                )
            }

    # ===== CROSS-CHAIN COMPATIBILITY CHECK =====
    if wallet_type == "solana":
        evm_chains = [c for c in valid_chains if CHAIN_TYPES.get(c) == "evm"]
        if evm_chains:
            return {
                "valid": False,
                "error": (
                    f"❌ **Wallet/Chain Mismatch**\n\n"
                    f"Your Solana wallet cannot monitor EVM chains: {', '.join(evm_chains)}\n\n"
                    f"**Solution:** Use `solana` as your chain:\n\n"
                    f"`register {wallet[:20]}... solana`"
                )
            }
        valid_chains = ["solana"]

    elif wallet_type == "evm":
        solana_chains = [c for c in valid_chains if CHAIN_TYPES.get(c) == "solana"]
        if solana_chains:
            return {
                "valid": False,
                "error": (
                    f"❌ **Wallet/Chain Mismatch**\n\n"
                    f"Your EVM wallet (0x...) cannot monitor Solana.\n\n"
                    f"**Solution:** Use EVM chains like ethereum, polygon, arbitrum, etc.\n\n"
                    f"Or register a Solana wallet address for Solana monitoring."
                )
            }

        valid_chains = [c for c in valid_chains if CHAIN_TYPES.get(c) == "evm"]

    if len(valid_chains) > 10:
        return {
            "valid": False,
            "error": "Too many chains (max 10). Please select your main chains."
        }

    return {
        "valid": True,
        "wallet": wallet_validation["checksum"],
        "wallet_type": wallet_type,
        "chains": valid_chains
    }


def get_risk_level_emoji(risk_level: str) -> str:
    risk_emoji = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴"
    }
    return risk_emoji.get(risk_level.lower(), "⚪")


def get_risk_action(risk_level: str) -> str:
    actions = {
        "low": "Continue monitoring",
        "medium": "Review within week",
        "high": "Rebalance within 24h",
        "critical": "Review immediately"
    }
    return actions.get(risk_level.lower(), "Monitor portfolio")


def format_alert_message(alert: AlertNotification) -> str:
    emoji = get_risk_level_emoji(alert.overall_risk)

    message = f"{emoji} **DeFiGuard Alert** {emoji}\n\n"
    message += f"**Risk Level:** {alert.overall_risk.upper()}\n"
    message += f"**Risk Score:** {alert.risk_score:.2%}\n"
    message += f"**Time:** {alert.timestamp[:16]}\n\n"

    if alert.concerns:
        message += "**⚠️ Concerns:**\n"
        for i, concern in enumerate(alert.concerns, 1):
            message += f"{i}. {concern}\n"
        message += "\n"

    if alert.recommendations:
        message += "**💡 Recommendations:**\n"
        for i, rec in enumerate(alert.recommendations, 1):
            message += f"{i}. {rec}\n"

    return message


def create_text_chat(text: str) -> ChatMessage:
    """Create a ChatMessage with text content"""
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=str(uuid4()),  # type: ignore[arg-type]
        content=[TextContent(type="text", text=text)]
    )


def format_timestamp(iso_timestamp: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        dt = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=1)))
        return dt.strftime('%b %d, %Y %I:%M %p')
    except (ValueError, AttributeError):
        return iso_timestamp[:16]


def get_default_risk_status() -> Dict:
    return {
        "risk_level": "low",
        "risk_score": 0.0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def get_chain_type_emoji(chain_type: str) -> str:
    if chain_type == "solana":
        return "◎"
    else:
        return "⟠"


def build_context_for_ai(ctx: Context, sender: str) -> str:
    portfolio = get_user_portfolio(ctx, sender)
    all_alerts = get_all_alerts(ctx)
    user_alerts = [a for a in all_alerts.values() if a.get("user_id") == sender]

    context = "USER PORTFOLIO DATA:\n\n"

    if portfolio:
        wallets = portfolio.get("wallets", [])
        chains = portfolio.get("chains", [])
        wallet_type = portfolio.get("wallet_type", "unknown")
        chain_names = [SUPPORTED_CHAINS.get(c, c) for c in chains]

        context += f"- Wallet Type: {wallet_type.upper()} {'(Solana)' if wallet_type == 'solana' else '(EVM)'}\n\n"
        context += f"- Registered: {len(wallets)} wallet(s)\n\n"
        context += f"- Monitored chains: {', '.join(chain_names)}\n\n"
        context += f"- Registration date: {portfolio.get('registered_at', 'Unknown')}\n\n"
    else:
        context += "- No portfolio registered yet\n\n"

    context += "\nRISK STATUS:\n\n"
    if user_alerts:
        latest = user_alerts[-1]
        context += f"- Current risk level: {latest['risk_level'].upper()}\n\n"
        context += f"- Risk score: {latest['risk_score']:.0%}\n\n"
        context += f"- Last updated: {latest['timestamp']}\n\n"

        if latest.get('concerns'):
            context += f"- Active concerns: {', '.join(latest['concerns'][:3])}\n\n"

        context += f"\n- Total alerts received: {len(user_alerts)}\n\n"

        recent_alerts = user_alerts[-3:]
        context += "- Recent risk levels: "
        context += ", ".join([f"{a['risk_level']} ({a['risk_score']:.0%})" for a in recent_alerts])
        context += "\n\n"
    else:
        context += "- No alerts yet (portfolio is healthy)\n\n"

    return context


async def query_asi1_model(ctx: Context, sender: str, user_question: str) -> str:
    try:
        user_context = build_context_for_ai(ctx, sender)

        unique_chains = {v for k, v in SUPPORTED_CHAINS.items() if k not in CHAIN_CANONICAL}

        system_prompt = f"""You are DeFiGuard AI, an intelligent assistant for a multi-chain DeFi portfolio risk monitoring system.

                            Your role is to help users understand their portfolio risks, explain alerts, and provide actionable advice about DeFi security.
                            
                            CAPABILITIES:
                            - Explain portfolio risk levels and what they mean
                            - Provide context about DeFi risks (smart contract risk, liquidity risk, market volatility, etc.)
                            - Help users understand alerts and recommendations
                            - Suggest risk mitigation strategies
                            - Answer questions about supported chains and features
                            - Explain Solana-specific risks (mint authority, freeze authority, rug pulls)
                            
                            SUPPORTED CHAINS: 
                            ◎ Solana
                            ⟠ EVM: {', '.join([c for c in unique_chains if c != 'Solana'])}
                            
                            WALLET TYPES:
                            - Solana wallets: Base58 format (e.g., 9WzDXwBbm...) - monitors Solana chain only
                            - EVM wallets: 0x format (e.g., 0x742d35...) - monitors Ethereum, BSC, Polygon, etc.
                            
                            SOLANA-SPECIFIC RISKS:
                            - Mint Authority: If not revoked, token supply can be inflated (rug pull risk)
                            - Freeze Authority: If active, your tokens can be frozen
                            - Holder Concentration: If top holder owns >30%, high dump risk
                            - Low Liquidity: Difficulty exiting position
                            
                            RISK LEVELS:
                            - 🟢 LOW (0-30%): Portfolio is healthy, continue monitoring
                            - 🟡 MEDIUM (30-50%): Some concerns, review within a week
                            - 🟠 HIGH (50-70%): Action needed, rebalance within 24 hours
                            - 🔴 CRITICAL (70-100%): Urgent action required, review immediately
                            
                            CURRENT USER DATA:
                            {user_context}
                            
                            IMPORTANT GUIDELINES:
                            - Be concise and helpful
                            - Use the user's actual portfolio data when available
                            - If the user asks about commands, guide them to use: status, history, portfolio, chains, register, analyze, help
                            - Always maintain a professional but friendly tone
                            - If you don't have specific information, be honest about limitations
                            - Focus on actionable insights
                            - Never make specific investment recommendations or financial advice
                            - Explain technical concepts in simple terms
                            - For Solana users, emphasize Solana-specific security checks
                            
                            If the user asks how to use the system, mention these commands:
                            - `status` - Check current risk level
                            - `history` - View recent alerts
                            - `portfolio` - View registered wallet(s)
                            - `chains` - List supported chains
                            - `register <wallet> <chains>` - Register/update portfolio
                            - `analyze <token_address> <chain>` - Analyze a token for fraud
                            - `help` - Show all commands
                            """

        messages: list[
            ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam
            ] = [
            ChatCompletionSystemMessageParam(role="system", content=system_prompt),
            ChatCompletionUserMessageParam(role="user", content=user_question),
        ]

        response = client.chat.completions.create(
            model="asi1-mini",
            messages=messages,
            max_tokens=2048,
        )

        return str(response.choices[0].message.content)


    except (APIError, APIConnectionError, RateLimitError, BadRequestError) as e:
        ctx.logger.exception(f"Error querying ASI-1 model: {e}")
        return (
            "I apologize, but I'm having trouble processing your question right now. "
            "Please try again, or use one of these commands:\n\n"
            "`status` `history` `portfolio` `chains` `analyze` `help`"
        )


def is_direct_command(text: str) -> bool:
    text_lower = text.strip().lower()

    first_word = text_lower.split()[0] if text_lower.split() else ""
    if first_word in DIRECT_COMMANDS:
        return True

    if "register" in text_lower:
        if "0x" in text or re.search(r'[1-9A-HJ-NP-Za-km-z]{32,44}', text):
            return True

    return False


@alert_agent.on_message(model=AlertNotification)
async def handle_alert(ctx: Context, sender: str, msg: AlertNotification):
    ctx.logger.info(
        f"🚨 Received {msg.overall_risk} risk alert for: {msg.user_id}"
    )

    key = f"alert_{msg.user_id}_{msg.timestamp}"
    alert_record = {
        "user_id": msg.user_id,
        "risk_level": msg.overall_risk,
        "risk_score": msg.risk_score,
        "timestamp": msg.timestamp,
        "concerns": msg.concerns,
        "recommendations": msg.recommendations
    }

    ctx.storage.set(key, alert_record)
    add_alert_key(ctx, key)

    alert_message = format_alert_message(msg)

    sessions = get_active_sessions(ctx)
    if msg.user_id in sessions:
        user_address = sessions[msg.user_id]
        chat_msg = create_text_chat(alert_message)
        await ctx.send(user_address, ChatWrapper(message=chat_msg))
        ctx.logger.info(f"✅ Alert sent to user {msg.user_id}")
    else:
        ctx.logger.info(f"ℹ️  No active session for {msg.user_id} - alert stored")

    await ctx.send(sender, Acknowledgement(message=f"Alert processed for {msg.user_id}"))


def increment_interaction_count(ctx: Context, sender: str):
    count = ctx.storage.get("total_interactions") or 0
    count += 1
    ctx.storage.set("total_interactions", count)

    # Track per-user interactions
    user_count = ctx.storage.get(f"interactions_{sender}") or 0
    user_count += 1
    ctx.storage.set(f"interactions_{sender}", user_count)

    ctx.logger.info(f"📊 Total interactions: {count} | User {sender}: {user_count}")


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    log_interaction(ctx, sender, "ChatMessage")
    increment_interaction_count(ctx, sender)

    ctx.logger.info("=" * 50)
    ctx.logger.info(f"[INTERACTION COUNT] Message from: {sender}")
    ctx.logger.info(f"[INTERACTION COUNT] Message ID: {msg.msg_id}")
    ctx.logger.info(f"[INTERACTION COUNT] Timestamp: {msg.timestamp}")
    ctx.logger.info("=" * 50)

    ctx.logger.info(f"💬 Received chat message from {sender}")

    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id
        )
    )

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"🟢 Chat session started with {sender}")
            add_active_session(ctx, sender, sender)

            portfolio = get_user_portfolio(ctx, sender)
            if portfolio:
                wallet_count = len(portfolio.get("wallets", []))
                chains = portfolio.get("chains", [])
                wallet_type = portfolio.get("wallet_type", "unknown")
                chain_names = [SUPPORTED_CHAINS.get(c, c) for c in chains]

                type_emoji = get_chain_type_emoji(wallet_type)

                welcome_msg = (
                    f"👋 **Welcome back to DeFiGuard AI!**\n\n"
                    f"✅ Portfolio registered:\n\n"
                    f"• {type_emoji} {wallet_type.upper()} wallet ({wallet_count})\n\n"
                    f"• {len(chains)} chain(s): {', '.join(chain_names)}\n\n"
                    f"Your portfolio is being monitored 24/7 with AI-powered risk analysis.\n\n"
                    f"**Ask me anything:**\n\n"
                    f"💬 \"What's my current risk?\"\n\n"
                    f"💬 \"Explain my latest alert\"\n\n"
                    f"💬 \"How can I reduce my risk?\"\n\n"
                )

                if wallet_type == "solana":
                    welcome_msg += (
                        f"**Solana-specific:**\n\n"
                        f"💬 \"What is mint authority?\"\n\n"
                        f"💬 \"Is this token safe?\" (use `analyze`)\n\n"
                    )

                welcome_msg += (
                    f"**Or use commands:**\n\n"
                    f"`status`\n\n `history`\n\n `portfolio`\n\n `chains`\n\n `analyze`\n\n `help`"
                )
            else:
                welcome_msg = (
                    "👋 **Welcome to DeFiGuard AI!**\n\n"
                    "Multi-chain portfolio risk monitoring with AI-powered insights.\n\n"
                    "**Now supporting ◎ Solana + ⟠ 12 EVM chains!**\n\n"
                    "**Get Started:**\n\n"
                    "`register <wallet_address> <chains>`\n\n"
                    "**EVM Example:**\n\n"
                    "`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon,arbitrum`\n\n"
                    "**Solana Example:**\n\n"
                    "`register 9WzDXwBbmPdCBoccoc9Ra8JVoJLxp6YhHvCKioeNFfZY solana`\n\n"
                    "**Ask me anything:**\n\n"
                    "💬 \"What chains do you support?\"\n\n"
                    "💬 \"What risks do you monitor?\"\n\n"
                    "💬 \"How does the risk scoring work?\"\n\n"
                    f"**Monitoring:** 13 chains with ASI-1 AI"
                )

            response = create_text_chat(welcome_msg)
            await ctx.send(sender, response)

        elif isinstance(item, TextContent):
            ctx.logger.info(f"📝 Text message: {item.text}")

            user_input = item.text.strip()

            if is_direct_command(user_input):
                command = user_input.lower()
                all_alerts = get_all_alerts(ctx)
                user_alerts = [
                    a for a in all_alerts.values() if a.get("user_id") == sender
                ]

                if command.startswith("register "):
                    parse_result = parse_register_command(user_input)

                    if not parse_result["valid"]:
                        error_msg = parse_result['error']
                        await ctx.send(sender, create_text_chat(error_msg))
                    else:
                        wallet = parse_result["wallet"]
                        chains = parse_result["chains"]
                        wallet_type = parse_result["wallet_type"]

                        save_user_portfolio(ctx, sender, [wallet], chains, wallet_type)

                        portfolio_msg = Portfolio(
                            user_id=sender,
                            wallets=[wallet],
                            chains=chains,
                            timestamp=datetime.now(timezone.utc).isoformat()
                        )

                        await ctx.send(PORTFOLIO_AGENT_ADDRESS, portfolio_msg)

                        chain_names = [SUPPORTED_CHAINS[c] for c in chains]
                        type_emoji = get_chain_type_emoji(wallet_type)

                        success_msg = (
                                f"✅ **Portfolio Registered!**\n\n"
                                f"**Wallet ({type_emoji} {wallet_type.upper()}):** \n\n`{wallet[:10]}...{wallet[-8:]}`\n\n"
                                f"**Monitoring {len(chains)} chain(s):**\n\n" +
                                "\n".join(f"• {name}" for name in chain_names) +
                                f"\n\n🛡️ AI-powered protection activated!\n\n"
                        )

                        if wallet_type == "solana":
                            success_msg += (
                                f"**◎ Solana Protection Includes:**\n\n"
                                f"• Mint authority checks\n\n"
                                f"• Freeze authority detection\n\n"
                                f"• Rug pull analysis\n\n"
                                f"• Holder concentration alerts\n\n"
                            )

                        success_msg += (
                            f"💬 Ask me: \"What should I know about my risk?\"\n\n"
                            f"Or use\n\n `status`\n\n `history`\n\n `analyze`\n\n `help`"
                        )

                        await ctx.send(sender, create_text_chat(success_msg))
                        ctx.logger.info(f"✅ Portfolio registered for {sender} ({wallet_type})")

                elif command.startswith("analyze "):
                    parts = command.split()
                    if len(parts) < 2:
                        analyze_help = (
                            "**🔍 Token Analysis**\n\n"
                            "Analyze any token for fraud indicators.\n\n"
                            "**Usage:**\n\n"
                            "`analyze <token_address> [chain]`\n\n"
                            "**Solana Example:**\n\n"
                            "`analyze DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263`\n\n"
                            "**EVM Example:**\n\n"
                            "`analyze 0x...tokenaddress ethereum`\n\n"
                            "Chain is auto-detected for Solana tokens."
                        )
                        await ctx.send(sender, create_text_chat(analyze_help))
                    else:
                        token_address = parts[1]
                        chain = parts[2] if len(parts) > 2 else None

                        addr_type = detect_address_type(token_address)
                        if addr_type == "solana":
                            chain = "solana"
                        elif not chain:
                            chain = "ethereum"

                        analyze_msg = (
                            f"🔍 **Analyzing Token...**\n\n"
                            f"**Address:** `{token_address[:15]}...`\n\n"
                            f"**Chain:** {SUPPORTED_CHAINS.get(chain, chain)}\n\n"
                            f"**Type:** {'◎ Solana' if addr_type == 'solana' else '⟠ EVM'}\n\n"
                            f"---\n\n"
                            f"⏳ Analysis in progress...\n\n"
                            f"The fraud detection agent will check:\n\n"
                        )

                        if addr_type == "solana":
                            analyze_msg += (
                                f"• Mint authority status\n\n"
                                f"• Freeze authority status\n\n"
                                f"• Holder distribution\n\n"
                                f"• RugCheck database\n\n"
                                f"• Jupiter token list\n\n"
                            )
                        else:
                            analyze_msg += (
                                f"• Contract verification\n\n"
                                f"• Honeypot detection\n\n"
                                f"• Buy/sell taxes\n\n"
                                f"• Ownership status\n\n"
                                f"• Holder concentration\n\n"
                            )

                        analyze_msg += f"\n💡 Results will appear shortly or ask me about this token!"

                        await ctx.send(sender, create_text_chat(analyze_msg))

                elif command == "chains":
                    unique_chains = {}
                    for key, name in SUPPORTED_CHAINS.items():
                        if key not in CHAIN_CANONICAL:
                            chain_type = CHAIN_TYPES.get(key, "evm")
                            if name not in unique_chains:
                                unique_chains[name] = (key, chain_type)

                    chains_msg = f"🔗 **Supported Chains ({len(unique_chains)})**\n\n"

                    # Solana first
                    chains_msg += "**◎ Solana Ecosystem:**\n\n"
                    chains_msg += "• **Solana** `solana`\n\n"

                    chains_msg += "**⟠ EVM Chains:**\n\n"
                    for name, (key, chain_type) in unique_chains.items():
                        if chain_type == "evm":
                            chains_msg += f"• **{name}** `{key}`\n\n"

                    chains_msg += (
                        f"---\n\n"
                        f"**Usage:**\n\n"
                        f"◎ `register <solana_wallet> solana`\n\n"
                        f"⟠ `register <evm_wallet> ethereum,bsc,polygon`\n\n"
                        f"\n💬 **Ask me:** \"Which chain is best for low fees?\""
                    )
                    await ctx.send(sender, create_text_chat(chains_msg))

                elif command == "portfolio":
                    portfolio = get_user_portfolio(ctx, sender)
                    if portfolio:
                        wallets = portfolio.get("wallets", [])
                        chains = portfolio.get("chains", [])
                        wallet_type = portfolio.get("wallet_type", "unknown")
                        chain_names = [SUPPORTED_CHAINS.get(c, c) for c in chains]
                        registered_at = portfolio.get("registered_at", "Unknown")
                        type_emoji = get_chain_type_emoji(wallet_type)

                        portfolio_msg = (
                            f"📋 **Your Portfolio**\n\n"
                            f"**Wallet Type:** {type_emoji} {wallet_type.upper()}\n\n"
                            f"**Wallet(s):**\n"
                        )
                        for i, wallet in enumerate(wallets, 1):
                            portfolio_msg += f"{i}. `{wallet[:10]}...{wallet[-8:]}`\n\n"

                        portfolio_msg += f"\n**Monitoring {len(chains)} chain(s):**\n\n"
                        portfolio_msg += "\n".join(f"• {name}" for name in chain_names)
                        portfolio_msg += f"\n\n**Registered:** {format_timestamp(registered_at)}\n\n"
                        portfolio_msg += f"💬 Ask me: \"How's my portfolio looking?\""
                    else:
                        portfolio_msg = (
                            "❌ No portfolio registered.\n\n"
                            "**EVM:**\n\n`register <0x_wallet> <chains>`\n\n"
                            "**Solana:**\n\n`register <solana_wallet> solana`\n\n"
                            "💬 Or ask: \"How do I get started?\""
                        )

                    await ctx.send(sender, create_text_chat(portfolio_msg))

                elif command == "status":
                    portfolio = get_user_portfolio(ctx, sender)
                    if not portfolio:
                        status_msg = (
                            "❌ No portfolio registered.\n\n"
                            "Register first:\n\n`register <wallet_address> <chains>`"
                        )
                    else:
                        wallet_type = portfolio.get("wallet_type", "unknown")
                        type_emoji = get_chain_type_emoji(wallet_type)

                        if user_alerts:
                            latest = user_alerts[-1]
                        else:
                            latest = get_default_risk_status()

                        emoji = get_risk_level_emoji(latest['risk_level'])
                        action = get_risk_action(latest['risk_level'])

                        status_msg = (
                            f"📊 **Portfolio Status** {type_emoji}\n\n"
                            f"**Risk Level:**  {emoji} {latest['risk_level'].upper()} \n\n"
                            f"**Risk Score:** {latest['risk_score']:.0%}\n\n"
                            f"**Updated:** {format_timestamp(latest['timestamp'])}\n\n"
                            f"**Action:** {action}\n\n"
                            f"💬 Ask me: \"What does this risk level mean?\""
                        )

                    await ctx.send(sender, create_text_chat(status_msg))

                elif command == "history":
                    user_alerts_list = user_alerts[-5:]
                    if user_alerts_list:
                        history_msg = "📜 **Recent Alerts (Last 5)**\n\n"
                        for i, alert in enumerate(reversed(user_alerts_list), 1):
                            emoji = get_risk_level_emoji(alert['risk_level'])
                            timestamp_str = alert['timestamp'][:16].replace('T', ' ')
                            history_msg += (
                                f"{i}. {emoji} {alert['risk_level'].upper()} "
                                f"({alert['risk_score']:.0%}) - "
                                f"{timestamp_str}\n"
                            )
                        history_msg += f"\n{len(user_alerts)} total alerts stored.\n\n"
                        history_msg += f"💬 Ask me: \"Why did my risk increase?\""
                    else:
                        history_msg = "📜 **Alert History**\n\nNo alerts yet. This is good! 🎉"

                    await ctx.send(sender, create_text_chat(history_msg))

                elif command == "help":
                    help_msg = (
                        "🆘 **DeFiGuard AI Commands**\n\n"
                        "**Setup:**\n\n"
                        "`register <wallet> <chains>` \n\n"
                        "⌙ Register portfolio (EVM or Solana)\n\n"

                        "---\n\n"

                        "**Monitoring:**\n\n"

                        "`status` \n\n"
                        "⌙ Current risk level\n\n"

                        "`history` \n\n"
                        "⌙ Recent alerts\n\n"

                        "`portfolio` \n\n"
                        "⌙ View registered wallet(s)\n\n"

                        "`chains` \n\n"
                        "⌙ List supported chains\n\n"

                        "`analyze <token> [chain]` \n\n"
                        "⌙ Analyze token for fraud\n\n"

                        "---\n\n"

                        "**💬 Ask Me Anything:**\n\n"
                        "• \"What's my biggest risk?\"\n\n"
                        "• \"How can I diversify better?\"\n\n"
                        "• \"Explain smart contract risk\"\n\n"
                        "• \"What is mint authority?\" (Solana)\n\n"
                        "• \"Which chains are safest?\"\n\n"

                        "---\n\n"

                        "**Supported Wallets:**\n\n"
                        "◎ Solana (base58)\n\n"
                        "⟠ EVM (0x...)\n\n"

                        "---\n\n"

                        "**AI-Powered:** ASI-1 model\n\n"
                        f"**Monitoring:** 13 chains (Solana + 12 EVM)\n\n"
                        f"**Frequency:** Every 10 minutes"
                    )
                    await ctx.send(sender, create_text_chat(help_msg))

                else:
                    response_msg = (
                        f"❓ Command '{user_input}' not recognized.\n\n"
                        "💬 Try asking me naturally:\n\n"
                        "\"What commands are available?\"\n\n"
                        "Or type\n\n `help` \n\nfor command list."
                    )
                    await ctx.send(sender, create_text_chat(response_msg))

            else:
                ctx.logger.info(f"🤖 Processing with ASI-1: {user_input}")
                ai_response = await query_asi1_model(ctx, sender, user_input)
                await ctx.send(sender, create_text_chat(ai_response))

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"🔴 Chat session ended with {sender}")
            remove_active_session(ctx, sender)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"✓ Message {msg.acknowledged_msg_id} acknowledged by {sender}")


@alert_agent.on_interval(period=300.0)
async def log_status(ctx: Context):
    total_interactions = ctx.storage.get("total_interactions") or 0
    active_sessions = get_active_sessions(ctx)
    all_alerts = get_all_alerts(ctx)

    ctx.logger.info("=" * 50)
    ctx.logger.info("📊 PERIODIC STATUS CHECK")
    ctx.logger.info(f"Total interactions tracked: {total_interactions}")
    ctx.logger.info(f"Active chat sessions: {len(active_sessions)}")
    ctx.logger.info(f"Total alerts stored: {len(all_alerts)}")
    ctx.logger.info("=" * 50)


@alert_agent.on_message(model=PingMessage)
async def handle_ping(ctx: Context, sender: str, msg: PingMessage):
    ctx.logger.info(f"[INTERACTION] Ping from {sender}: {msg.text}")

    await ctx.send(
        sender,
        PingMessage(
            text=f"Pong: {msg.text}",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    )
    ctx.logger.info(f"✅ Interaction logged with {sender}")


alert_agent.include(chat_proto, publish_manifest=True)


@alert_agent.on_event("startup")
async def startup(ctx: Context):
    all_alerts = get_all_alerts(ctx)
    sessions = get_active_sessions(ctx)

    mailbox_configured = bool(os.getenv('ALERT_AGENT_MAILBOX'))
    endpoint_configured = bool(os.getenv('DEFIGUARD_ENDPOINT'))

    unique_chains = len([k for k in SUPPORTED_CHAINS.keys() if k not in CHAIN_CANONICAL])

    ctx.logger.info("=" * 70)
    ctx.logger.info("🚨 DeFiGuard AI Alert Agent Started! (Solana Enhanced)")
    ctx.logger.info(f"📍 Agent Address: {alert_agent.address}")
    ctx.logger.info(f"📫 Mailbox: {os.getenv('ALERT_AGENT_MAILBOX', 'Not configured')}")
    ctx.logger.info(f"📫 Mailbox Status: {'✅ CONFIGURED' if mailbox_configured else '❌ NOT CONFIGURED'}")
    ctx.logger.info(f"🌐 Endpoint: {os.getenv('DEFIGUARD_ENDPOINT', 'Not configured')}")
    ctx.logger.info(f"🌐 Endpoint Status: {'✅ CONFIGURED' if endpoint_configured else '❌ NOT CONFIGURED'}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("💬 ASI:One Chat Protocol enabled ✓")
    ctx.logger.info("🤖 ASI-1 AI Integration enabled ✓")
    ctx.logger.info(f"🔗 Portfolio Agent: {PORTFOLIO_AGENT_ADDRESS}")
    ctx.logger.info(f"🔗 Supporting {unique_chains} chains:")
    ctx.logger.info(f"   ◎  Solana: 1 chain")
    ctx.logger.info(f"   ⟠  EVM: {unique_chains - 1} chains")
    ctx.logger.info(f"📊 Stored alerts: {len(all_alerts)}")
    ctx.logger.info(f"👥 Active sessions: {len(sessions)}")

    ctx.logger.info("🧪 Testing message reception capability...")
    if mailbox_configured:
        ctx.logger.info("✅ Agent ready to receive messages")
    else:
        ctx.logger.error("❌ MAILBOX NOT CONFIGURED - Messages won't be received!")

    ctx.logger.info("=" * 70)


if __name__ == "__main__":
    alert_agent.run()
