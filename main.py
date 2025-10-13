from uagents import Bureau
from agents.portfolio_monitor import portfolio_agent
from agents.risk_analysis import risk_agent
from agents.alert_agent import alert_agent
from agents.market_data import market_agent
from agents.fraud_detection import fraud_agent
from dotenv import load_dotenv

load_dotenv()


def print_banner():
    """Print DeFiGuard banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║                  DEFIGUARD SYSTEM v1.0                    ║
    ║                                                           ║
    ║           Multi-Agent Risk Management System              ║
    ║                Powered by ASI Alliance                    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝

    📊 Agent Status:
    """
    print(banner)

    print(f"  ✓ Portfolio Monitor   : {portfolio_agent.address[:16]}...")
    print(f"  ✓ Risk Analyzer       : {risk_agent.address[:16]}...")
    print(f"  ✓ Alert System        : {alert_agent.address[:16]}...")
    print(f"  ✓ Market Data         : {market_agent.address[:16]}...")
    print(f"  ✓ Fraud Detection     : {fraud_agent.address[:16]}...")
    print("\n  🚀 All agents initialized successfully!")
    print("  🌐 ASI:One Chat Protocol enabled on Alert Agent")
    print("  🧠 SingularityNET MeTTa integration: ACTIVE")
    print("\n" + "=" * 60 + "\n")


def print_agent_addresses():
    """Print all agent addresses for configuration"""
    print("📋 Agent Addresses (save these for .env):\n")
    print(f"PORTFOLIO_AGENT_ADDRESS={portfolio_agent.address}")
    print(f"RISK_AGENT_ADDRESS={risk_agent.address}")
    print(f"ALERT_AGENT_ADDRESS={alert_agent.address}")
    print(f"MARKET_AGENT_ADDRESS={market_agent.address}")
    print(f"FRAUD_AGENT_ADDRESS={fraud_agent.address}")
    print("\n" + "=" * 60 + "\n")


def main():
    """Main entry point for DeFiGuard system"""

    # Print banner
    print_banner()

    # Print agent addresses
    print_agent_addresses()

    # Create bureau to manage all agents
    bureau = Bureau(
        port=8888,
        endpoint="http://localhost:8888/submit"
    )

    # Add all agents to bureau
    bureau.add(portfolio_agent)
    bureau.add(risk_agent)
    bureau.add(alert_agent)
    bureau.add(market_agent)
    bureau.add(fraud_agent)

    print("🎯 Starting DeFiGuard Multi-Agent System...")
    print("📡 Agents are now monitoring and ready to serve!\n")
    print("💬 Interact with the Alert Agent via ASI:One interface")
    print("🔗 Register portfolios by sending messages to Portfolio Agent\n")

    # Run the bureau
    try:
        bureau.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutting down DeFiGuard system...")
        print("👋 All agents stopped. Goodbye!")


if __name__ == "__main__":
    main()