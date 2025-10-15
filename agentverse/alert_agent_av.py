from uagents import Agent, Context, Model, Protocol
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
from pydantic import UUID4
from typing import List, Dict
from web3 import Web3
import re


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


alert_agent = Agent(
    name="alert_agent",
    mailbox=True,
    publish_agent_details=True
)

print(f"Alert Agent Address: {alert_agent.address}")

# Portfolio Monitor Agent address
PORTFOLIO_AGENT_ADDRESS = "agent1qt2fhu92p6uq3yq692drxrnx74yh7jqs0vjm65st3tz6wej6rxf7qehenpc"

chat_proto = Protocol(spec=chat_protocol_spec)

SUPPORTED_CHAINS = {
    "ethereum": "Ethereum",
    "bsc": "BNB Smart Chain",
    "polygon": "Polygon",
    "arbitrum": "Arbitrum One",
    "optimism": "Optimism",
    "avalanche": "Avalanche C-Chain",
    "base": "Base",
    "fantom": "Fantom",
    "gnosis": "Gnosis Chain",
    "moonbeam": "Moonbeam",
    "celo": "Celo",
    "cronos": "Cronos"
}


def add_alert_key(ctx: Context, key: str):
    """Add alert key to master list"""
    keys = ctx.storage.get("alert_keys") or []
    if key not in keys:
        keys.append(key)
        ctx.storage.set("alert_keys", keys)


def get_all_alerts(ctx: Context) -> Dict[str, dict]:
    """Fetch all alerts"""
    keys = ctx.storage.get("alert_keys") or []
    alerts = {}
    for key in keys:
        value = ctx.storage.get(key)
        if value:
            alerts[key] = value
    return alerts


def add_active_session(ctx: Context, user_id: str, address: str):
    """Track active chat session"""
    sessions = ctx.storage.get("active_sessions") or {}
    sessions[user_id] = address
    ctx.storage.set("active_sessions", sessions)


def remove_active_session(ctx: Context, user_id: str):
    """Remove active chat session"""
    sessions = ctx.storage.get("active_sessions") or {}
    if user_id in sessions:
        del sessions[user_id]
        ctx.storage.set("active_sessions", sessions)


def get_active_sessions(ctx: Context) -> Dict[str, str]:
    """Retrieve all active sessions"""
    return ctx.storage.get("active_sessions") or {}


def get_user_portfolio(ctx: Context, user_id: str) -> Dict:
    """Get user's registered portfolio"""
    return ctx.storage.get(f"user_portfolio_{user_id}")


def save_user_portfolio(ctx: Context, user_id: str, wallets: List[str], chains: List[str]):
    """Save user's portfolio registration"""
    portfolio_data = {
        "wallets": wallets,
        "chains": chains,
        "registered_at": datetime.now(timezone.utc).isoformat()
    }
    ctx.storage.set(f"user_portfolio_{user_id}", portfolio_data)


def validate_wallet_address(address: str) -> Dict:
    if not isinstance(address, str):
        return {"valid": False, "error": "Address must be a string", "checksum": None}

    address = address.strip()

    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        if not address.startswith("0x"):
            return {
                "valid": False,
                "error": "Address must start with '0x'",
                "checksum": None
            }
        elif len(address) != 42:
            return {
                "valid": False,
                "error": f"Address must be 42 characters (currently {len(address)})",
                "checksum": None
            }
        else:
            return {
                "valid": False,
                "error": "Address contains invalid characters (only 0-9, a-f, A-F allowed)",
                "checksum": None
            }

    try:
        checksum_address = Web3.to_checksum_address(address)

        if checksum_address == "0x0000000000000000000000000000000000000000":
            return {
                "valid": False,
                "error": "Cannot use zero address (0x0000...)",
                "checksum": None
            }

        burn_addresses = [
            "0x000000000000000000000000000000000000dEaD",
            "0xdead000000000000000042069420694206942069"
        ]
        if checksum_address.lower() in [b.lower() for b in burn_addresses]:
            return {
                "valid": False,
                "error": "Cannot use burn address",
                "checksum": None
            }

        return {
            "valid": True,
            "checksum": checksum_address,
            "error": None
        }
    except ValueError as e:
        return {
            "valid": False,
            "error": f"Invalid checksum: {str(e)}",
            "checksum": None
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}",
            "checksum": None
        }


def validate_chain(chain: str) -> Dict:
    chain_lower = chain.strip().lower()

    if chain_lower in SUPPORTED_CHAINS:
        return {
            "valid": True,
            "chain_name": SUPPORTED_CHAINS[chain_lower],
            "chain_key": chain_lower,
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
            "error": error_msg
        }


def parse_register_command(text: str) -> Dict:
    parts = text.strip().split()

    if len(parts) < 3:
        return {
            "valid": False,
            "error": (
                "Invalid format. Use:\n\n"
                "`register <wallet_address> <chains>`\n\n"
                "Examples:\n\n"
                "`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon`\n\n"
                "`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum polygon arbitrum`"
            )
        }

    wallet = parts[1]

    wallet_validation = validate_wallet_address(wallet)
    if not wallet_validation["valid"]:
        return {
            "valid": False,
            "error": f"❌ {wallet_validation['error']}"
        }

    chains_input = " ".join(parts[2:])

    # comma-separated
    if "," in chains_input:
        chains = [c.strip().lower() for c in chains_input.split(",")]
    else:
        # Space-separated
        chains = [c.strip().lower() for c in parts[2:]]

    chains = list(dict.fromkeys(chains))

    valid_chains = []
    invalid_chains = []

    for chain in chains:
        if not chain:
            continue

        chain_validation = validate_chain(chain)
        if chain_validation["valid"]:
            valid_chains.append(chain_validation["chain_key"])
        else:
            invalid_chains.append(chain_validation["error"])

    if invalid_chains:
        supported_list = ", ".join(SUPPORTED_CHAINS.keys())
        return {
            "valid": False,
            "error": (
                    f"❌ Invalid chain(s):\n\n" +
                    "\n".join(f"• {err}" for err in invalid_chains) +
                    f"\n\n**Supported chains:**\n\n{supported_list}"
            )
        }

    if not valid_chains:
        return {
            "valid": False,
            "error": "No valid chains specified"
        }

    if len(valid_chains) > 10:
        return {
            "valid": False,
            "error": "Too many chains (max 10). Please select your main chains."
        }

    return {
        "valid": True,
        "wallet": wallet_validation["checksum"],
        "chains": valid_chains
    }


def get_risk_level_emoji(risk_level: str) -> str:
    """Get emoji for risk level"""
    risk_emoji = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴"
    }
    return risk_emoji.get(risk_level.lower(), "⚪")


def get_risk_action(risk_level: str) -> str:
    """Get recommended action based on risk level"""
    actions = {
        "low": "Continue monitoring",
        "medium": "Review within week",
        "high": "Rebalance within 24h",
        "critical": "Review immediately"
    }
    return actions.get(risk_level.lower(), "Monitor portfolio")


def format_alert_message(alert: AlertNotification) -> str:
    """Format alert into human-readable message"""
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
        msg_id=UUID(str(uuid4())),
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
    """Return default risk status for new portfolios"""
    return {
        "risk_level": "low",
        "risk_score": 0.0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@alert_agent.on_message(model=AlertNotification)
async def handle_alert(ctx: Context, sender: str, msg: AlertNotification):
    """Handle incoming alert from Risk Analysis Agent"""
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


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages from ASI:One"""
    ctx.logger.info(f"💬 Received chat message from {sender}")

    await ctx.send(
        sender,
        ChatAckWrapper(
            acknowledged_msg_id=str(msg.msg_id),
            timestamp=datetime.now(timezone.utc).isoformat()
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
                chain_names = [SUPPORTED_CHAINS.get(c, c) for c in chains]

                welcome_msg = (
                    f"👋 **Welcome back to DeFiGuard!**\n\n"
                    f"✅ Portfolio registered:\n\n"

                    f"• {wallet_count} wallet(s)\n"
                    f"• {len(chains)} chain(s): {', '.join(chain_names)}\n\n"

                    f"Your portfolio is being monitored 24/7 across all chains.\n\n"

                    f"**Commands:**\n\n"

                    f"`status` \n"
                    f"Check curren risk\n\n"

                    f"`history` \n"
                    f"View recent alerts\n\n"

                    f"`portfolio` \n"
                    f"View registered wallet(s)\n\n"

                    f"`chains` \n"
                    f"View supported chains\n\n"

                    f"`register <wallet> <chains>` \n"
                    f"Update portfolio\n\n"

                    f"`help` \n"
                    f"Show all commands"
                )
            else:
                welcome_msg = (
                    "👋 **Welcome to DeFiGuard!**\n\n"

                    "Multi-chain portfolio risk monitoring with AI.\n\n"

                    "**Get Started:**\n\n"

                    "`register <wallet_address> <chains>`\n\n"

                    "**Example:**\n\n"
                    "`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon,arbitrum`\n\n"

                    "**Supported:**\n\n"
                    f"{len(SUPPORTED_CHAINS)} chains including Ethereum, BSC, Polygon, Arbitrum, Optimism, Avalanche, Base & more!\n\n"

                    "Type\n\n `chains` \n\nto see all supported chains.\n"
                    "Type\n\n `help` \n\nfor more commands."
                )

            response = create_text_chat(welcome_msg)
            await ctx.send(sender, response)

        elif isinstance(item, TextContent):
            ctx.logger.info(f"📝 Text message: {item.text}")

            command = item.text.strip().lower()
            all_alerts = get_all_alerts(ctx)
            user_alerts = [
                a for a in all_alerts.values() if a.get("user_id") == sender
            ]

            # Handle portfolio registration
            if command.startswith("register "):
                parse_result = parse_register_command(item.text)

                if not parse_result["valid"]:
                    error_msg = parse_result['error']
                    await ctx.send(sender, create_text_chat(error_msg))
                else:
                    wallet = parse_result["wallet"]
                    chains = parse_result["chains"]

                    # Save locally
                    save_user_portfolio(ctx, sender, [wallet], chains)

                    # Send to Portfolio Monitor Agent
                    portfolio_msg = Portfolio(
                        user_id=sender,
                        wallets=[wallet],
                        chains=chains,
                        timestamp=datetime.now(timezone.utc).isoformat()
                    )

                    await ctx.send(PORTFOLIO_AGENT_ADDRESS, portfolio_msg)

                    chain_names = [SUPPORTED_CHAINS[c] for c in chains]
                    success_msg = (
                            f"✅ **Portfolio Registered!**\n\n"
                            f"**Wallet:** \n\n`{wallet[:10]}...{wallet[-8:]}`\n\n"
                            f"**Monitoring {len(chains)} chain(s):**\n" +
                            "\n".join(f"• {name}" for name in chain_names) +
                            f"\n\n🛡️ Your portfolio is now protected 24/7\n\n"
                            f"You'll receive alerts automatically when risks are detected.\n\n"
                            f"Type\n\n `status` \n\nto check current risk level."
                    )
                    await ctx.send(sender, create_text_chat(success_msg))
                    ctx.logger.info(f"✅ Portfolio registered for {sender}")

            elif command == "chains":
                chains_msg = (
                    f"🔗 **Supported Chains ({len(SUPPORTED_CHAINS)})**\n\n"
                )
                for i, (key, name) in enumerate(SUPPORTED_CHAINS.items(), 1):
                    chains_msg += f"{i}. **{name}** (`{key}`)\n"

                chains_msg += (
                    f"\n**Usage:**\n\n"
                    f"`register <wallet> ethereum,bsc,polygon`\n\n"
                    f"Or space-separated:\n\n"
                    f"`register <wallet> ethereum bsc polygon`"
                )
                await ctx.send(sender, create_text_chat(chains_msg))

            elif command == "portfolio":
                portfolio = get_user_portfolio(ctx, sender)
                if portfolio:
                    wallets = portfolio.get("wallets", [])
                    chains = portfolio.get("chains", [])
                    chain_names = [SUPPORTED_CHAINS.get(c, c) for c in chains]
                    registered_at = portfolio.get("registered_at", "Unknown")

                    portfolio_msg = (
                        f"📋 **Your Portfolio**\n\n"
                        f"**Wallet(s):**\n"
                    )
                    for i, wallet in enumerate(wallets, 1):
                        portfolio_msg += f"{i}. `{wallet[:10]}...{wallet[-8:]}`\n"

                    portfolio_msg += f"\n**Monitoring {len(chains)} chain(s):**\n"
                    portfolio_msg += "\n".join(f"• {name}" for name in chain_names)
                    portfolio_msg += f"\n\n**Registered:** {format_timestamp(registered_at)}\n\n"
                    portfolio_msg += f"To update:\n\n`register <new_wallet> <chains>`"
                else:
                    portfolio_msg = (
                        "❌ No portfolio registered.\n\n"
                        "Use:\n\n`register <wallet_address> <chains>`\n\n"
                        "Example:\n\n`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon`"
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
                    if user_alerts:
                        latest = user_alerts[-1]
                    else:
                        latest = get_default_risk_status()

                    emoji = get_risk_level_emoji(latest['risk_level'])
                    action = get_risk_action(latest['risk_level'])

                    status_msg = (
                        f"📊 **Portfolio Status**\n\n"
                        f"{emoji} **Risk Level:** {latest['risk_level'].upper()}\n\n"
                        f"**Risk Score:** {latest['risk_score']:.0%}\n\n"
                        f"**Updated:** {format_timestamp(latest['timestamp'])}\n\n"
                        f"**Action:** {action}\n\n"
                        f"Type\n\n `history` \n\nfor details."
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
                    history_msg += f"\n{len(user_alerts)} total alerts stored."
                else:
                    history_msg = "📜 **Alert History**\n\nNo alerts yet. This is good! 🎉"

                await ctx.send(sender, create_text_chat(history_msg))

            elif command == "help":
                help_msg = (
                    "🆘 **DeFiGuard Commands**\n\n"

                    "**Setup:**\n\n"

                    "`register <wallet> <chains>` \n"
                    "Register portfolio\n\n"

                    "**Monitoring:**\n\n"

                    "`status` \n"
                    "Current risk level\n\n"

                    "`history` \n"
                    "Recent alerts\n\n"

                    "`portfolio` \n"
                    "View registered wallet(s)\n\n"

                    "`chains` \n"
                    "List supported chains\n\n"

                    "`help` \n"
                    "Show command message\n\n"

                    "**Risk Levels:**\n\n"
                    "🟢 **Low** (0-30%) - Healthy\n"
                    "🟡 **Medium** (30-50%) - Monitor\n"
                    "🟠 **High** (50-70%) - Action needed\n"
                    "🔴 **Critical** (70-100%) - Urgent\n\n"

                    f"**Monitoring:** {len(SUPPORTED_CHAINS)} chains\n"
                    f"**Frequency:** Every 5 minutes\n"
                    f"**AI-Powered:** MeTTa reasoning"
                )
                await ctx.send(sender, create_text_chat(help_msg))

            else:
                response_msg = (
                    f"❓ Command '{item.text}' not recognized.\n\n"
                    "Type\n\n `help` \n\nfor available commands."
                )
                await ctx.send(sender, create_text_chat(response_msg))

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"🔴 Chat session ended with {sender}")
            remove_active_session(ctx, sender)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle message acknowledgements"""

    ctx.logger.info(f"✓ Message {msg.acknowledged_msg_id} acknowledged by {sender}")


alert_agent.include(chat_proto, publish_manifest=True)


@alert_agent.on_event("startup")
async def startup(ctx: Context):
    all_alerts = get_all_alerts(ctx)
    sessions = get_active_sessions(ctx)

    ctx.logger.info("=" * 70)
    ctx.logger.info("🚨 DeFiGuard Alert Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {alert_agent.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("💬 ASI:One Chat Protocol enabled ✓")
    ctx.logger.info(f"🔗 Portfolio Agent: {PORTFOLIO_AGENT_ADDRESS}")
    ctx.logger.info(f"🔗 Supporting {len(SUPPORTED_CHAINS)} chains")
    ctx.logger.info(f"📊 Stored alerts: {len(all_alerts)}")
    ctx.logger.info(f"👥 Active sessions: {len(sessions)}")
    ctx.logger.info("=" * 70)


if __name__ == "__main__":
    alert_agent.run()
