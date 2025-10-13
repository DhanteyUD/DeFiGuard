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


class ChatWrapper(Model):
    message: ChatMessage


class Acknowledgement(Model):
    message: str


class ChatAckWrapper(Model):
    acknowledged_msg_id: str
    timestamp: str


alert_agent = Agent(
    name="alert_agent",
    mailbox=True,  # type: ignore[arg-type]
    publish_agent_details = True  # type: ignore[arg-type]
)

print(f"Alert Agent Address: {alert_agent.address}")


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
    message += f"**Time:** {alert.timestamp}\n\n"

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
        msg_id=uuid4(), # type: ignore[arg-type] # UUID4(str(uuid4()))
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
        ctx.logger.info(f"ℹ️  No active session for {msg.user_id}")

    # Acknowledge receipt
    await ctx.send(sender, Acknowledgement(message=f"Alert processed for {msg.user_id}"))


@chat_proto.on_message(ChatMessage) # type: ignore[arg-type]
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

            welcome_msg = (
                "👋 **Welcome to DeFiGuard Alert Agent!**\n\n"
                "I monitor your DeFi portfolio and send real-time risk alerts.\n\n"
                "**Commands:**\n"
                "• `status` - Check current portfolio risk\n"
                "• `history` - View recent alerts (last 5)\n"
                "• `help` - Show this message\n\n"
                "Your portfolio is being monitored 24/7. "
                "You'll receive automatic alerts when risks are detected."
            )
            response = create_text_chat(welcome_msg)
            await ctx.send(sender, response)  # type: ignore[arg-type]

        elif isinstance(item, TextContent):
            ctx.logger.info(f"📝 Text message: {item.text}")

            command = item.text.strip().lower()
            all_alerts = get_all_alerts(ctx)
            user_alerts = [
                a for a in all_alerts.values() if a.get("user_id") == sender
            ]

            if command == "status":
                if user_alerts:
                    latest = user_alerts[-1]
                    status_msg = (
                        f"📊 **Current Portfolio Status**\n\n"
                        f"**Risk Level:** {latest['risk_level'].upper()}\n"
                        f"**Risk Score:** {latest['risk_score']:.2%}\n"
                        f"**Last Updated:** {latest['timestamp']}\n\n"
                        f"Type `history` for more details."
                    )
                else:
                    status_msg = (
                        "No portfolio data available yet.\n\n"
                        "Make sure your portfolio is registered with DeFiGuard."
                    )

                await ctx.send(sender, create_text_chat(status_msg))  # type: ignore[arg-type]

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

                await ctx.send(sender, create_text_chat(history_msg))  # type: ignore[arg-type]

            elif command == "help":
                help_msg = (
                    "🆘 **DeFiGuard Help**\n\n"
                    "**Commands:**\n"
                    "• `status` - Current portfolio risk level\n"
                    "• `history` - View recent alerts (last 5)\n"
                    "• `help` - Show this message\n\n"
                    "**Risk Levels:**\n"
                    "🟢 **Low** - Portfolio is healthy\n"
                    "🟡 **Medium** - Monitor closely\n"
                    "🟠 **High** - Action recommended\n"
                    "🔴 **Critical** - Immediate action needed\n\n"
                    "You'll receive automatic alerts when risks are detected."
                )
                await ctx.send(sender, create_text_chat(help_msg))  # type: ignore[arg-type]

            else:
                response_msg = (
                    f"Command '{item.text}' not recognized.\n\n"
                    "Type `help` to see available commands."
                )
                await ctx.send(sender, create_text_chat(response_msg))  # type: ignore[arg-type]

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"🔴 Chat session ended with {sender}")
            remove_active_session(ctx, sender)


@chat_proto.on_message(ChatAcknowledgement)  # type: ignore[arg-type]
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
    ctx.logger.info("=" * 60)


if __name__ == "__main__":
    alert_agent.run()