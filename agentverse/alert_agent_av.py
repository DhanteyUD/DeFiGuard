from uagents import Agent, Context, Model, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    StartSessionContent,
    EndSessionContent,
    chat_protocol_spec,
)
from datetime import datetime, timezone
from uuid import uuid4
from typing import List, Dict


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


def parse_register_command(text: str) -> Dict:
    """
    Parse portfolio registration command
    Expected format: register <wallet_address> <chain1,chain2,...>
    Example: register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon
    """
    parts = text.strip().split()

    if len(parts) < 3:
        return {
            "valid": False,
            "error": "Invalid format. Use: `register <wallet_address> <chains>`"
        }

    wallet = parts[1]
    chains_str = parts[2]

    # Basic wallet address validation
    if not wallet.startswith("0x") or len(wallet) != 42:
        return {
            "valid": False,
            "error": "Invalid wallet address. Must start with '0x' and be 42 characters long"
        }

    # Parse chains
    chains = [c.strip().lower() for c in chains_str.split(",")]
    valid_chains = ["ethereum", "bsc", "polygon", "arbitrum", "optimism", "avalanche"]

    invalid_chains = [c for c in chains if c not in valid_chains]
    if invalid_chains:
        return {
            "valid": False,
            "error": f"Invalid chain(s): {', '.join(invalid_chains)}. Valid chains: {', '.join(valid_chains)}"
        }

    return {
        "valid": True,
        "wallet": wallet,
        "chains": chains
    }


def format_alert_message(alert: AlertNotification) -> str:
    """Format alert into human-readable message"""
    risk_emoji = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🟠",
        "critical": "🔴"
    }

    emoji = risk_emoji.get(alert.overall_risk, "⚪")

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
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)]
    )


@alert_agent.on_message(model=AlertNotification)
async def handle_alert(ctx: Context, sender: str, msg: AlertNotification):
    """Handle incoming alert from Risk Analysis Agent"""
    ctx.logger.info(
        f"🚨 Received {msg.overall_risk} risk alert for: {msg.user_id}"
    )

    # Store in persistent storage
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

    # Format message
    alert_message = format_alert_message(msg)

    # Send to user if they have an active session
    sessions = get_active_sessions(ctx)
    if msg.user_id in sessions:
        user_address = sessions[msg.user_id]
        chat_msg = create_text_chat(alert_message)
        await ctx.send(user_address, ChatWrapper(message=chat_msg))
        ctx.logger.info(f"✅ Alert sent to user {msg.user_id}")
    else:
        ctx.logger.info(f"ℹ️  No active session for {msg.user_id} - alert stored for later")

    # Acknowledge receipt
    await ctx.send(sender, Acknowledgement(message=f"Alert processed for {msg.user_id}"))


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages from ASI:One"""
    ctx.logger.info(f"💬 Received chat message from {sender}")

    # Send acknowledgement
    await ctx.send(
        sender,
        ChatAckWrapper(
            acknowledged_msg_id=str(msg.msg_id),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    )

    # Process message content
    for item in msg.content:
        if isinstance(item, StartSessionContent):
            ctx.logger.info(f"🟢 Chat session started with {sender}")
            add_active_session(ctx, sender, sender)

            # Check if user has registered portfolio
            portfolio = get_user_portfolio(ctx, sender)
            if portfolio:
                wallet_count = len(portfolio.get("wallets", []))
                chain_count = len(portfolio.get("chains", []))

                welcome_msg = (
                    f"👋 **Welcome back to DeFiGuard!**\n\n"
                    f"✅ Portfolio registered: {wallet_count} wallet(s) on {chain_count} chain(s)\n\n"
                    f"Your portfolio is being monitored 24/7.\n\n"
                    f"**Commands:**\n\n"

                    f"> To check current portfolio risk\n\n"
                    f"`status` \n\n"

                    f"> To view recent alerts (last 5)\n\n"
                    f"`history` \n\n"

                    f"> To view registered portfolio\n\n"
                    f"`portfolio` \n\n"

                    f"> To update portfolio\n\n"
                    f"`register <wallet> <chains>` \n\n"

                    f"> To show this message\n\n"
                    f"`help`"
                )
            else:
                welcome_msg = (
                    "👋 **Welcome to DeFiGuard Alert Agent!**\n\n"
                    "To get started, register your portfolio:\n\n"
                    "**Register Format:**\n\n"
                    "`register <wallet_address> <chain1,chain2,...>`\n\n"
                    "**Example:**\n\n"
                    "`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon`\n\n"
                    "**Supported Chains:**\n\n"
                    "ethereum, bsc, polygon\n\n"
                    "Type **help** for more commands."
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
                    error_msg = (
                        f"❌ {parse_result['error']}\n\n"
                        f"**Correct format:**\n\n"
                        f"`register <wallet_address> <chains>`\n\n"
                        f"**Example:**\n\n"
                        f"`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon`"
                    )
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

                    success_msg = (
                        f"✅ **Portfolio Registered Successfully!**\n\n"
                        f"**Wallet:** `{wallet}`\n\n"
                        f"**Chains:** {', '.join(chains)}\n\n"
                        f"Your portfolio is now being monitored 24/7.\n\n"
                        f"✓ No risks detected yet\n\n"
                        f"Alerts will appear here automatically when risks are found."
                    )
                    await ctx.send(sender, create_text_chat(success_msg))
                    ctx.logger.info(f"✅ Portfolio registered for {sender}")

            elif command == "portfolio":
                portfolio = get_user_portfolio(ctx, sender)
                if portfolio:
                    wallets = portfolio.get("wallets", [])
                    chains = portfolio.get("chains", [])
                    registered_at = portfolio.get("registered_at", "Unknown")

                    portfolio_msg = (
                        f"📋 **Your Registered Portfolio**\n\n"
                        f"**Wallets:**\n"
                    )
                    for i, wallet in enumerate(wallets, 1):
                        portfolio_msg += f"{i}. `{wallet}`\n\n"

                    portfolio_msg += f"\n**Chains:**\n{', '.join(chains)}\n\n"
                    portfolio_msg += f"**Registered:** {registered_at[:16]}\n\n"
                    portfolio_msg += f"To update, use:\n\n`register <new_wallet> <chains>`"
                else:
                    portfolio_msg = (
                        "❌ No portfolio registered yet.\n\n"
                        "Use: \n\n`register <wallet_address> <chains>`\n\n"
                        "Example:\n\n`register 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb ethereum,polygon`"
                    )

                await ctx.send(sender, create_text_chat(portfolio_msg))

            elif command == "status":
                portfolio = get_user_portfolio(ctx, sender)
                if not portfolio:
                    status_msg = (
                        "❌ No portfolio registered.\n\n"
                        "Please register your portfolio first:\n"
                        "`register <wallet_address> <chains>`"
                    )
                elif user_alerts:
                    latest = user_alerts[-1]
                    status_msg = (
                        f"📊 **Current Portfolio Status**\n\n"
                        f"**Risk Level:** {latest['risk_level'].upper()}\n\n"
                        f"**Risk Score:** {latest['risk_score']:.2%}\n\n"
                        f"**Last Updated:** {latest['timestamp']}\n\n"
                        f"Type `history` for more details."
                    )
                else:
                    status_msg = (
                        "⏳ Portfolio monitoring in progress...\n\n"
                        "No risk data available yet.\n\n"
                        "Initial scan may take a few minutes."
                    )

                await ctx.send(sender, create_text_chat(status_msg))

            elif command == "history":
                user_alerts = user_alerts[-5:]
                if user_alerts:
                    history_msg = "📜 **Recent Alerts**\n\n"
                    for i, alert in enumerate(reversed(user_alerts), 1):
                        history_msg += (
                            f"{i}. {alert['risk_level'].upper()} "
                            f"({alert['risk_score']:.1%}) - "
                            f"{alert['timestamp'][:16]}\n"
                        )
                else:
                    history_msg = "No alert history found."

                await ctx.send(sender, create_text_chat(history_msg))

            elif command == "help":
                help_msg = (
                    "🆘 **DeFiGuard Help**\n\n"

                    "**Setup:**\n\n"

                    "Register portfolio"
                    "`register <wallet> <chains>` \n\n"

                    "**Commands:**\n\n"

                    "Current portfolio risk level"
                    "`status` \n\n"

                    "View recent alerts (last 5)"
                    "`history` \n\n"

                    "View registered portfolio"
                    "`portfolio` \n\n"

                    "Show this message"
                    "`help` \n\n"

                    "**Risk Levels:**\n\n"

                    "🟢 **Low** - Portfolio is healthy\n\n"
                    "🟡 **Medium** - Monitor closely\n\n"
                    "🟠 **High** - Action recommended\n\n"
                    "🔴 **Critical** - Immediate action needed\n\n"

                    "**Supported Chains:**\n\n"

                    "ethereum, bsc, polygon, arbitrum, optimism, avalanche"
                )
                await ctx.send(sender, create_text_chat(help_msg))

            else:
                response_msg = (
                    f"Command '{item.text}' not recognized.\n\n"
                    "Type\n\n `help` \n\nto see available commands."
                )
                await ctx.send(sender, create_text_chat(response_msg))

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"🔴 Chat session ended with {sender}")
            remove_active_session(ctx, sender)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle message acknowledgements"""
    ctx.logger.info(f"Message {msg.acknowledged_msg_id} acknowledged by {sender}")


# IMPORTANT: This enables ASI:One integration
alert_agent.include(chat_proto, publish_manifest=True)


@alert_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("=" * 60)
    ctx.logger.info("🚨 DeFiGuard Alert Agent Started!")
    ctx.logger.info(f"📍 Agent Address: {alert_agent.address}")
    ctx.logger.info("☁️  Running on Agentverse")
    ctx.logger.info("💬 ASI:One Chat Protocol enabled ✓")
    ctx.logger.info(f"🔗 Portfolio Agent: {PORTFOLIO_AGENT_ADDRESS}")
    all_alerts = get_all_alerts(ctx)
    sessions = get_active_sessions(ctx)
    ctx.logger.info(f"📊 Stored alerts: {len(all_alerts)}")
    ctx.logger.info(f"👥 Active sessions: {len(sessions)}")
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    alert_agent.run()
