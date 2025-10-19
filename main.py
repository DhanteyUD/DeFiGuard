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
BUREAU_PORT = int(os.getenv("BUREAU_PORT", 8888))

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


async def root_handler(request):
    logger.info(f"Root endpoint hit from {request.remote}")
    return web.json_response({
        "service": "DeFiGuard Multi-Agent System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "status": "/status"
        }
    })


async def health_check(request):
    logger.info(f"Health check from {request.remote}")
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


async def agent_status(request):
    logger.info(f"Status check from {request.remote}")
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


async def submit_handler(request):
    logger.info(f"Submit endpoint hit from {request.remote}")
    try:
        body = await request.json()
        logger.debug(f"Received message: {body}")

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"http://localhost:{BUREAU_PORT}/submit",
                    json=body,
                    headers={"Content-Type": "application/json"}
            ) as resp:
                result = await resp.json()
                return web.json_response(result, status=resp.status)

    except Exception as e:
        logger.error(f"Error forwarding to bureau: {e}", exc_info=True)
        return web.json_response(
            {"error": str(e)},
            status=500
        )


async def submit_info(_request):
    return web.json_response({
        "endpoint": "/submit",
        "method": "POST",
        "description": "Agent message submission endpoint for Agentverse",
        "bureau_port": BUREAU_PORT,
        "status": "ready"
    })


async def start_http_server():
    app = web.Application()
    app.router.add_get('/', root_handler)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', agent_status)
    app.router.add_post('/submit', submit_handler)

    logger.info(f"🌐 Configuring HTTP server on 0.0.0.0:{HTTP_PORT}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', HTTP_PORT)
    await site.start()

    logger.info(f"✅ HTTP server successfully started and listening on port {HTTP_PORT}")
    logger.info(f"📍 Available routes: /, /health, /status, /submit")

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("HTTP server shutting down...")
        await runner.cleanup()


async def run_bureau():
    try:
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

        await bureau.run_async()

    except Exception as e:
        logger.error(f"Bureau error: {e}", exc_info=True)
        raise


async def main_async():
    print_banner()
    save_agent_addresses()

    logger.info("=" * 60)
    logger.info("🚀 Starting DeFiGuard services...")
    logger.info(f"📡 HTTP Port: {HTTP_PORT} (Railway assigned)")
    logger.info(f"📡 Bureau Port: {BUREAU_PORT} (internal)")
    logger.info("=" * 60)

    try:
        await asyncio.gather(
            start_http_server(),
            run_bureau(),
            return_exceptions=False
        )
    except Exception as e:
        logger.error(f"❌ Error in main loop: {e}", exc_info=True)
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