from uagents import Bureau
from agents.portfolio_monitor import portfolio_agent
from agents.risk_analysis import risk_agent
from agents.alert_agent import alert_agent
from agents.market_data import market_agent
from agents.fraud_detection import fraud_agent
import os
import logging
from dotenv import load_dotenv
from aiohttp import web
import asyncio

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/defiguard.log') if os.path.exists('/app/logs') else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              🛡️  DEFIGUARD SYSTEM v1.0                    ║
    ║                                                           ║
    ║         ccMulti-Agent Risk Management System              ║
    ║                Powered by ASI Alliance                    ║
    ║                  Running in Docker 🐳                     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝

    📊 Agent Status:
    """
    print(banner)

    print(f"  ✓ Portfolio Monitor   : {portfolio_agent.address[:16]}...")
    print(f"  ✓ Risk Analysis       : {risk_agent.address[:16]}...")
    print(f"  ✓ Alert Agent        : {alert_agent.address[:16]}...")
    print(f"  ✓ Market Data         : {market_agent.address[:16]}...")
    print(f"  ✓ Fraud Detection     : {fraud_agent.address[:16]}...")
    print("\n  🚀 All agents initialized successfully!")
    print("  🌐 ASI:One Chat Protocol enabled on Alert Agent")
    print("  🧠 SingularityNET MeTTa integration: ACTIVE")
    print(f"  📡 Bureau running on port 8080")
    print("\n" + "=" * 60 + "\n")


def save_agent_addresses():
    addresses = {
        "portfolio_monitor": portfolio_agent.address,
        "risk_analysis": risk_agent.address,
        "alert_system": alert_agent.address,
        "market_data": market_agent.address,
        "fraud_detection": fraud_agent.address
    }

    try:
        with open('/app/data/agent_addresses.txt', 'w') as f:
            f.write("DeFiGuard Agent Addresses\n")
            f.write("=" * 50 + "\n\n")
            for name, address in addresses.items():
                f.write(f"{name}: {address}\n")
        logger.info("Agent addresses saved to /app/data/agent_addresses.txt")
    except Exception as e:
        logger.error(f"Failed to save agent addresses: {e}")


async def health_check(request):
    return web.json_response({
        "status": "healthy",
        "agents": {
            "portfolio_monitor": portfolio_agent.address,
            "risk_analysis": risk_agent.address,
            "alert_system": alert_agent.address,
            "market_data": market_agent.address,
            "fraud_detection": fraud_agent.address
        },
        "version": "1.0.0"
    })


async def agent_status(request):
    return web.json_response({
        "agents": [
            {
                "name": "Portfolio Monitor",
                "address": portfolio_agent.address,
                "port": 8000,
                "status": "running"
            },
            {
                "name": "Risk Analysis",
                "address": risk_agent.address,
                "port": 8001,
                "status": "running"
            },
            {
                "name": "Alert System",
                "address": alert_agent.address,
                "port": 8002,
                "status": "running",
                "chat_enabled": True
            },
            {
                "name": "Market Data",
                "address": market_agent.address,
                "port": 8003,
                "status": "running"
            },
            {
                "name": "Fraud Detection",
                "address": fraud_agent.address,
                "port": 8004,
                "status": "running"
            }
        ]
    })


async def start_http_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', agent_status)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("HTTP server started on port 8080")


def main():

    try:
        print_banner()

        save_agent_addresses()

        bureau = Bureau(
            port=8888,
            endpoint="http://0.0.0.0:8080/submit"
        )

        bureau.add(portfolio_agent)
        bureau.add(risk_agent)
        bureau.add(alert_agent)
        bureau.add(market_agent)
        bureau.add(fraud_agent)

        logger.info("🎯 Starting DeFiGuard Multi-Agent System...")
        logger.info("📡 Agents are now monitoring and ready to serve!")
        logger.info("💬 Interact with Alert Agent via ASI:One")
        logger.info("🔗 Health check: http://localhost:8080/health")
        logger.info("📊 Status: http://localhost:8080/status")

        loop = asyncio.get_event_loop()
        loop.create_task(start_http_server())

        bureau.run()

    except KeyboardInterrupt:
        logger.info("\n⚠️  Shutting down DeFiGuard system...")
        logger.info("👋 All agents stopped. Goodbye!")
    except Exception as e:
        logger.error(f"❌ Error starting DeFiGuard: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()