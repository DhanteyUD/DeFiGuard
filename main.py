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

HTTP_PORT = int(os.getenv("PORT", 8000))
BUREAU_PORT = 8888

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
    ║           Multi-Agent Risk Management System              ║
    ║                Powered by ASI Alliance                    ║
    ║                  Running on Railway 🚂                    ║
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
    print(f"  📡 HTTP Server on port {HTTP_PORT}")
    print(f"  📡 Bureau running on port {BUREAU_PORT} (internal)")
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
        os.makedirs('/app/data', exist_ok=True)
        with open('/app/data/agent_addresses.txt', 'w') as f:
            f.write("DeFiGuard Agent Addresses\n")
            f.write("=" * 50 + "\n\n")
            for name, address in addresses.items():
                f.write(f"{name}: {address}\n")
        logger.info("Agent addresses saved to /app/data/agent_addresses.txt")
    except Exception as e:
        logger.error(f"Failed to save agent addresses: {e}")


async def health_check(_request):
    return web.json_response({
        "status": "healthy",
        "agents": {
            "portfolio_monitor": portfolio_agent.address,
            "risk_analysis": risk_agent.address,
            "alert_system": alert_agent.address,
            "market_data": market_agent.address,
            "fraud_detection": fraud_agent.address
        },
        "version": "1.0.0",
        "platform": "railway"
    })


async def agent_status(_request):
    return web.json_response({
        "agents": [
            {
                "name": "Portfolio Monitor",
                "address": portfolio_agent.address,
                "status": "running"
            },
            {
                "name": "Risk Analysis",
                "address": risk_agent.address,
                "status": "running"
            },
            {
                "name": "Alert System",
                "address": alert_agent.address,
                "status": "running",
                "chat_enabled": True
            },
            {
                "name": "Market Data",
                "address": market_agent.address,
                "status": "running"
            },
            {
                "name": "Fraud Detection",
                "address": fraud_agent.address,
                "status": "running"
            }
        ]
    })


async def home(_request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DeFiGuard - Multi-Agent Risk Management</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            h1 { margin-top: 0; font-size: 2.5em; }
            .status { color: #4ade80; font-weight: bold; }
            .endpoint {
                background: rgba(0, 0, 0, 0.2);
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                font-family: monospace;
            }
            a { color: #60a5fa; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .agent-list { margin: 20px 0; }
            .agent { 
                background: rgba(255, 255, 255, 0.05);
                padding: 10px;
                margin: 5px 0;
                border-radius: 5px;
                border-left: 3px solid #4ade80;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ DeFiGuard</h1>
            <p class="status">✅ System Online</p>
            <p>Multi-Agent Risk Management System powered by ASI Alliance</p>

            <h2>📡 API Endpoints</h2>
            <div class="endpoint">
                <strong>Health Check:</strong> <a href="/health">/health</a>
            </div>
            <div class="endpoint">
                <strong>Agent Status:</strong> <a href="/status">/status</a>
            </div>

            <h2>🤖 Active Agents</h2>
            <div class="agent-list">
                <div class="agent">📊 Portfolio Monitor</div>
                <div class="agent">⚠️ Risk Analysis</div>
                <div class="agent">🔔 Alert Agent (ASI:One Enabled)</div>
                <div class="agent">📈 Market Data</div>
                <div class="agent">🔍 Fraud Detection</div>
            </div>

            <p style="margin-top: 30px; font-size: 0.9em; opacity: 0.8;">
                🧠 Powered by SingularityNET MeTTa Integration
            </p>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')


async def start_http_server():
    app = web.Application()
    app.router.add_get('/', home)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', agent_status)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', HTTP_PORT)
    await site.start()
    logger.info(f"✅ HTTP server started on port {HTTP_PORT}")

    while True:
        await asyncio.sleep(3600)


async def run_bureau():
    bureau = Bureau(
        port=BUREAU_PORT,
        endpoint=f"http://0.0.0.0:{BUREAU_PORT}/submit"
    )

    bureau.add(portfolio_agent)
    bureau.add(risk_agent)
    bureau.add(alert_agent)
    bureau.add(market_agent)
    bureau.add(fraud_agent)

    logger.info("🎯 Starting DeFiGuard Multi-Agent System...")
    logger.info("📡 Agents are now monitoring and ready to serve!")
    logger.info("💬 Interact with Alert Agent via ASI:One")
    logger.info(f"🔗 Health check: http://0.0.0.0:{HTTP_PORT}/health")
    logger.info(f"📊 Status: http://0.0.0.0:{HTTP_PORT}/status")

    # Use run_async() instead of run() to avoid event loop conflicts
    await bureau.run_async()


async def main_async():
    try:
        print_banner()
        save_agent_addresses()

        await asyncio.gather(
            start_http_server(),
            run_bureau()
        )

    except KeyboardInterrupt:
        logger.info("\n⚠️  Shutting down DeFiGuard system...")
        logger.info("👋 All agents stopped. Goodbye!")
    except Exception as e:
        logger.error(f"❌ Error starting DeFiGuard: {e}", exc_info=True)
        raise


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Shutting down DeFiGuard system...")
        logger.info("👋 All agents stopped. Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()