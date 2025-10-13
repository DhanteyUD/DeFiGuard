from uagents import Agent, Context, Model, Protocol
# from uagents.setup import fund_agent_if_low
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
# from pydantic import UUID4
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


# Data Models
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


# Create Alert Agent
alert_agent = Agent(
    name="alert_agent",
    seed=os.getenv("ALERT_AGENT_SEED", "alert_demo_seed"),
    port=8002,
    endpoint=["http://localhost:8002/submit"],
    # mailbox=False,  # type: ignore[arg-type] # Required for ASI:One
    # publish_agent_details = True # type: ignore[arg-type] # Required for ASI:One
)

# fund_agent_if_low(str(alert_agent.wallet.address()))

print(f"Alert Agent Address: {alert_agent.address}")

# Initialize chat protocol for ASI:One
chat_proto = Protocol(spec=chat_protocol_spec)

# Alert history (use database in production)
alert_history = []
active_sessions = {}


# Helper functions
def format_alert_message(alert: AlertNotification) -> str:
    """Format alert into human-readable message"""

    # Risk emoji
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


# Message Handlers
@alert_agent.on_message(model=AlertNotification)
async def handle_alert(ctx: Context, sender: str, msg: AlertNotification):
    """Handle incoming alert from Risk Analysis Agent"""
    ctx.logger.info(
        f"Received {msg.overall_risk} risk alert for user: {msg.user_id}"
    )

    # Store in history
    alert_record = {
        "user_id": msg.user_id,
        "risk_level": msg.overall_risk,
        "risk_score": msg.risk_score,
        "timestamp": msg.timestamp,
        "concerns": msg.concerns,
        "recommendations": msg.recommendations
    }
    alert_history.append(alert_record)

    # Format message
    alert_message = format_alert_message(msg)

    # Send to user if they have an active session
    if msg.user_id in active_sessions:
        user_address = active_sessions[msg.user_id]
        chat_msg = create_text_chat(alert_message)
        await ctx.send(user_address, ChatWrapper(message=chat_msg))
        ctx.logger.info(f"Alert sent to user {msg.user_id}")
    else:
        ctx.logger.info(f"No active session for user {msg.user_id}")

    # Acknowledge receipt
    await ctx.send(sender, Acknowledgement(message=f"Alert processed for {msg.user_id}"))


# Chat Protocol Handlers
@chat_proto.on_message(ChatMessage)  # type: ignore[arg-type]
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages from ASI:One"""
    ctx.logger.info(f"Received chat message from {sender}")

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
            ctx.logger.info(f"Chat session started with {sender}")
            active_sessions[sender] = sender

            # Send welcome message
            welcome_msg = (
                "👋 Welcome to DeFiGuard Alert Agent!\n\n"
                "I monitor your DeFi portfolio and send real-time risk alerts.\n\n"
                "Commands:\n"
                "- `status` - Check current portfolio risk\n"
                "- `history` - View recent alerts\n"
                "- `help` - Show this message\n\n"
                "Your portfolio is being monitored 24/7."
            )
            response = create_text_chat(welcome_msg)
            await ctx.send(sender, response)  # type: ignore[arg-type]


        elif isinstance(item, TextContent):
            ctx.logger.info(f"Text message: {item.text}")

            # Parse command
            command = item.text.strip().lower()

            if command == "status":
                # Get latest risk status
                user_alerts = [
                    a for a in alert_history
                    if a.get("user_id") == sender
                ]

                if user_alerts:
                    latest = user_alerts[-1]
                    status_msg = (
                        f"📊 **Current Portfolio Status**\n\n"
                        f"Risk Level: {latest['risk_level'].upper()}\n"
                        f"Risk Score: {latest['risk_score']:.2%}\n"
                        f"Last Updated: {latest['timestamp']}\n\n"
                        f"Type `history` for more details."
                    )
                else:
                    status_msg = (
                        "No portfolio data available yet. "
                        "Make sure your portfolio is registered with DeFiGuard."
                    )

                await ctx.send(sender, create_text_chat(status_msg))  # type: ignore[arg-type]

            elif command == "history":
                # Get alert history
                user_alerts = [
                                  a for a in alert_history
                                  if a.get("user_id") == sender
                              ][-5:]  # Last 5 alerts

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
                    "🟢 Low - Portfolio is healthy\n"
                    "🟡 Medium - Monitor closely\n"
                    "🟠 High - Action recommended\n"
                    "🔴 Critical - Immediate action needed\n\n"
                    "You'll receive automatic alerts when risks are detected."
                )
                await ctx.send(sender, create_text_chat(help_msg))  # type: ignore[arg-type]

            else:
                # Unknown command
                response_msg = (
                    f"Command '{item.text}' not recognized.\n"
                    "Type `help` to see available commands."
                )
                await ctx.send(sender, create_text_chat(response_msg))  # type: ignore[arg-type]

        elif isinstance(item, EndSessionContent):
            ctx.logger.info(f"Chat session ended with {sender}")
            if sender in active_sessions:
                del active_sessions[sender]


@chat_proto.on_message(ChatAcknowledgement)  # type: ignore[arg-type]
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle message acknowledgements"""
    ctx.logger.info(f"Message {msg.acknowledged_msg_id} acknowledged by {sender}")


# Include chat protocol
alert_agent.include(chat_proto, publish_manifest=True)


# # Override the registration method to skip Almanac registration
# async def skip_registration(self):
#     """Skip Almanac registration for local testing"""
#     self._logger.info("Almanac registration disabled for local testing")
#
#
# alert_agent.register = skip_registration.__get__(alert_agent, Agent)


@alert_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Alert Agent started!")
    ctx.logger.info(f"Agent address: {alert_agent.address}")
    ctx.logger.info("ASI:One Chat Protocol enabled ✓")


if __name__ == "__main__":
    alert_agent.run()
