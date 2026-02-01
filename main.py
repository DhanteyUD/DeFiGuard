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
import requests
from uagents_core.utils.registration import (
    register_chat_agent,
    RegistrationRequestCredentials,
)

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

AGENT_NAME = "DeFiGuard-2.0"
AGENT_URL = "https://defiguard-production.up.railway.app/submit"

SYSTEM_VERSION = "2.0.0-solana"
SUPPORTED_CHAINS = {
    "solana": 1,  # Solana ecosystem
    "evm": 12  # EVM chains
}
TOTAL_CHAINS = sum(SUPPORTED_CHAINS.values())


def check_agent_status():
    try:
        headers = {
            "Authorization": f"Bearer {os.environ['AGENTVERSE_KEY']}"
        }

        res = requests.get(
            "https://agentverse.ai/api/agents",
            headers=headers,
            timeout=10
        )

        if res.status_code == 404:
            # API endpoint changed or not available - return unknown status
            logger.warning("Agentverse /api/agents endpoint returned 404")
            return False, "api_unavailable"

        if res.status_code != 200:
            logger.warning(f"Failed to fetch agents: {res.status_code} - {res.text}")
            return False, "api_error"

        try:
            data = res.json()
        except ValueError:
            logger.warning(f"Invalid JSON response from Agentverse: {res.text[:100]}")
            return False, "invalid_response"

        # Handle different possible response formats
        agents = data.get("agents", [])
        if not agents and isinstance(data, list):
            agents = data

        for agent in agents:
            agent_name = agent.get("name")
            if agent_name == AGENT_NAME:
                is_active = agent.get("active", False)
                agent_id = agent.get("id", "unknown")
                logger.info(f"Found agent '{AGENT_NAME}' (ID: {agent_id}) - Active: {is_active}")
                return True, "active" if is_active else "inactive"

        all_agent_names = [a.get("name", "unnamed") for a in agents]
        logger.info(f"Agent '{AGENT_NAME}' not found in Agentverse. Available agents: {all_agent_names[:10]}")
        return False, "not_found"

    except requests.exceptions.Timeout:
        logger.warning("Timeout checking agent status - Agentverse API unreachable")
        return False, "timeout"
    except requests.exceptions.ConnectionError:
        logger.warning("Connection error checking agent status - Network issue")
        return False, "connection_error"
    except requests.exceptions.RequestException as e:
        logger.warning(f"Network error checking agent status: {e}")
        return False, "network_error"
    except Exception as e:
        logger.error(f"Unexpected error checking agent status: {e}", exc_info=True)
        return False, "error"


def register_agent():
    try:
        logger.info("🔄 Registering agent with Agentverse...")

        logger.debug(f"AGENTVERSE_KEY exists: {'AGENTVERSE_KEY' in os.environ}")
        logger.debug(f"AGENT_SEED_PHRASE exists: {'AGENT_SEED_PHRASE' in os.environ}")

        if 'AGENTVERSE_KEY' in os.environ:
            logger.debug(f"AGENTVERSE_KEY length: {len(os.environ['AGENTVERSE_KEY'])}")
            logger.debug(f"AGENTVERSE_KEY first 10 chars: {os.environ['AGENTVERSE_KEY'][:10]}...")

        logger.info(f"🧠 Registering agent with Agentverse...")
        logger.info(f"   Name: {AGENT_NAME}")
        logger.info(f"   URL: {AGENT_URL}")

        register_chat_agent(
            AGENT_NAME,
            AGENT_URL,
            active=True,
            credentials=RegistrationRequestCredentials(
                agentverse_api_key=os.environ["AGENTVERSE_KEY"],
                agent_seed_phrase=os.environ["AGENT_SEED_PHRASE"],
            ),
        )

        logger.info("✅ Agent registration completed!")

        import time
        time.sleep(2)

        exists, status = check_agent_status()
        logger.info(f"✅ Registration completed. Verification status: {status}")

        return True, f"registration_completed_{status}"

    except KeyError as e:
        logger.error(f"❌ Missing environment variable: {e}")
        logger.error("Please ensure AGENTVERSE_KEY and AGENT_SEED_PHRASE are set")
        return False, "missing_env_vars"
    except Exception as e:
        logger.error(f"❌ Agent registration failed: {e}", exc_info=True)
        return False, f"exception_{str(e)[:50]}"


async def periodic_health_check():
    """Periodic check to ensure agent is properly registered"""
    check_interval = 300  # 5 minutes

    while True:
        try:
            await asyncio.sleep(check_interval)

            logger.info("🔍 Performing periodic agent health check...")
            exists, status = check_agent_status()

            if status == "active":
                logger.info("✅ Agent health check passed - Agent is ACTIVE")
            elif status == "inactive":
                logger.warning("⚠️  Agent is INACTIVE! Attempting re-registration...")
                success, message = register_agent()
                if success:
                    logger.info(f"✅ Re-registration successful: {message}")
                else:
                    logger.error(f"❌ Re-registration failed: {message}")
            elif status == "not_found":
                logger.warning("⚠️  Agent not found! Attempting registration...")
                success, message = register_agent()
                if success:
                    logger.info(f"✅ Registration successful: {message}")
                else:
                    logger.error(f"❌ Registration failed: {message}")
            elif status in ["api_unavailable", "api_error", "timeout", "connection_error", "network_error"]:
                logger.warning(f"⚠️  Agentverse API issue: {status}. Will retry later.")
            else:
                logger.warning(f"⚠️  Unknown agent status: {status}")

        except Exception as e:
            logger.error(f"Error in periodic health check: {e}", exc_info=True)


def print_banner():
    banner = f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         🛡️  DEFIGUARD SYSTEM v{SYSTEM_VERSION}            ║
    ║                                                           ║
    ║           Multi-Agent Risk Management System              ║
    ║                Powered by ASI Alliance                    ║
    ║                  Running on Railway 🚂                    ║
    ║                                                           ║
    ║         ◎  NOW WITH SOLANA BLOCKCHAIN SUPPORT ◎           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝

    📊 Agent Status:
    """
    print(banner)

    print(f"  ✓ Portfolio Monitor   : {portfolio_agent.address[:16]}...")
    print(f"  ✓ Risk Analysis       : {risk_agent.address[:16]}...")
    print(f"  ✓ Alert Agent         : {alert_agent.address[:16]}...")
    print(f"  ✓ Market Data         : {market_agent.address[:16]}...")
    print(f"  ✓ Fraud Detection     : {fraud_agent.address[:16]}...")
    print("\n  🚀 All agents initialized successfully!")
    print("  🌐 ASI:One Chat Protocol enabled on Alert Agent")
    print("  🧠 SingularityNET MeTTa integration: ACTIVE")
    print(f"\n  🔗 Supported Chains ({TOTAL_CHAINS} total):")
    print(f"     ◎  Solana: {SUPPORTED_CHAINS['solana']} chain")
    print(f"     ⟠  EVM: {SUPPORTED_CHAINS['evm']} chains")
    print(f"\n  📡 HTTP Server on port {HTTP_PORT}")
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
            f.write(f"DeFiGuard Agent Addresses (v{SYSTEM_VERSION})\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Supported Chains: {TOTAL_CHAINS} (Solana + {SUPPORTED_CHAINS['evm']} EVM)\n\n")
            for name, address in addresses.items():
                f.write(f"{name}: {address}\n")
        logger.info("Agent addresses saved to /app/data/agent_addresses.txt")
    except Exception as e:
        logger.error(f"Failed to save agent addresses: {e}")


async def root_handler(request):
    logger.info(f"Root endpoint hit from {request.remote}")
    return web.json_response({
        "service": "DeFiGuard Multi-Agent System",
        "version": SYSTEM_VERSION,
        "status": "running",
        "chains": {
            "total": TOTAL_CHAINS,
            "solana": SUPPORTED_CHAINS["solana"],
            "evm": SUPPORTED_CHAINS["evm"]
        },
        "features": [
            "Multi-chain portfolio monitoring",
            "AI-powered risk analysis (MeTTa)",
            "Solana fraud detection",
            "Real-time alerts",
            "Natural language chat"
        ],
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "chains": "/chains",
            "reregister": "/reregister"
        }
    })


async def health_check(request):
    logger.info(f"Health check from {request.remote}")
    return web.json_response({
        "status": "healthy",
        "version": SYSTEM_VERSION,
        "agents": {
            "portfolio_monitor": portfolio_agent.address,
            "risk_analysis": risk_agent.address,
            "alert_system": alert_agent.address,
            "market_data": market_agent.address,
            "fraud_detection": fraud_agent.address
        },
        "chains": {
            "solana": True,
            "evm": True,
            "total": TOTAL_CHAINS
        },
        "platform": "railway"
    })


async def chains_handler(request):
    logger.info(f"Chains endpoint hit from {request.remote}")
    return web.json_response({
        "total_chains": TOTAL_CHAINS,
        "solana": {
            "count": 1,
            "chains": ["solana"],
            "features": [
                "SPL token monitoring",
                "Mint authority detection",
                "Freeze authority detection",
                "RugCheck integration",
                "Holder concentration analysis"
            ]
        },
        "evm": {
            "count": 12,
            "chains": [
                "ethereum", "bsc", "polygon", "arbitrum", "optimism",
                "avalanche", "base", "fantom", "gnosis", "moonbeam",
                "celo", "cronos"
            ],
            "features": [
                "Native token monitoring",
                "GoPlus security integration",
                "Honeypot detection",
                "Contract verification check"
            ]
        }
    })


async def agent_status(request):
    logger.info(f"Status check from {request.remote}")

    exists, av_status = check_agent_status()

    return web.json_response({
        "version": SYSTEM_VERSION,
        "agents": [
            {
                "name": "Portfolio Monitor",
                "address": portfolio_agent.address,
                "status": "running",
                "chains": ["solana"] + ["ethereum", "bsc", "polygon", "arbitrum", "optimism",
                                        "avalanche", "base", "fantom", "gnosis", "moonbeam",
                                        "celo", "cronos"]
            },
            {
                "name": "Risk Analysis",
                "address": risk_agent.address,
                "status": "running",
                "features": ["MeTTa AI", "Solana risk rules", "Chain diversity analysis"]
            },
            {
                "name": "Alert System",
                "address": alert_agent.address,
                "status": "running",
                "chat_enabled": True,
                "agentverse_registered": exists,
                "agentverse_status": av_status,
                "features": ["Solana wallet support", "Token analysis command"]
            },
            {
                "name": "Market Data",
                "address": market_agent.address,
                "status": "running",
                "features": ["Solana token prices", "Meme coin volatility alerts"]
            },
            {
                "name": "Fraud Detection",
                "address": fraud_agent.address,
                "status": "running",
                "features": ["Solana fraud detection", "RugCheck API", "Mint/Freeze authority checks"]
            }
        ],
        "agentverse": {
            "registered": exists,
            "status": av_status,
            "note": "active = verified active, inactive = verified inactive, other = error state"
        },
        "chains": {
            "solana": SUPPORTED_CHAINS["solana"],
            "evm": SUPPORTED_CHAINS["evm"],
            "total": TOTAL_CHAINS
        }
    })


async def reregister_handler(request):
    logger.info(f"Manual re-registration triggered from {request.remote}")

    try:
        success, message = register_agent()

        if success:
            return web.json_response({
                "success": True,
                "message": f"Agent re-registered successfully: {message}",
                "agent_name": AGENT_NAME,
                "version": SYSTEM_VERSION
            })
        else:
            return web.json_response({
                "success": False,
                "message": f"Re-registration failed: {message}",
                "agent_name": AGENT_NAME
            }, status=500)

    except Exception as e:
        logger.error(f"Error in manual re-registration: {e}", exc_info=True)
        return web.json_response({
            "success": False,
            "message": f"Re-registration error: {str(e)}",
            "agent_name": AGENT_NAME
        }, status=500)


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
        return web.json_response({"error": str(e)}, status=500)


async def start_http_server():
    app = web.Application()
    app.router.add_get('/', root_handler)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', agent_status)
    app.router.add_get('/chains', chains_handler)
    app.router.add_post('/submit', submit_handler)
    app.router.add_post('/reregister', reregister_handler)

    logger.info(f"🌐 Configuring HTTP server on 0.0.0.0:{HTTP_PORT}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', HTTP_PORT)
    await site.start()

    logger.info(f"✅ HTTP server started on port {HTTP_PORT}")
    logger.info("📍 Available routes: /, /health, /status, /chains, /submit, /reregister")

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("HTTP server shutting down...")
        await runner.cleanup()


async def run_bureau():
    try:
        bureau = Bureau(port=BUREAU_PORT, endpoint=f"http://0.0.0.0:{BUREAU_PORT}/submit")

        bureau.add(portfolio_agent)
        bureau.add(risk_agent)
        bureau.add(alert_agent)
        bureau.add(market_agent)
        bureau.add(fraud_agent)

        logger.info("🎯 Starting DeFiGuard Multi-Agent System...")
        logger.info(f"◎  Solana support: ENABLED")
        logger.info(f"⟠  EVM chains: {SUPPORTED_CHAINS['evm']} supported")
        await bureau.run_async()

    except Exception as e:
        logger.error(f"Bureau error: {e}", exc_info=True)
        raise


async def main_async():
    print_banner()
    save_agent_addresses()

    # Wait for services to initialize before registering
    logger.info("⏳ Waiting for services to initialize...")
    await asyncio.sleep(3)

    # Register agent with Agentverse - always attempt registration
    logger.info("🔄 Attempting agent registration...")
    registration_success, message = register_agent()

    if not registration_success:
        logger.warning(f"⚠️  Initial registration failed: {message}")
        logger.warning("⚠️  The system will retry registration in 5 minutes via health check")
    else:
        logger.info(f"✅ Registration status: {message}")

    logger.info("=" * 60)
    logger.info(f"🚀 Starting DeFiGuard services (v{SYSTEM_VERSION})...")
    logger.info(f"📡 HTTP Port: {HTTP_PORT} (Railway assigned)")
    logger.info(f"📡 Bureau Port: {BUREAU_PORT} (internal)")
    logger.info(f"🔗 Chains: {TOTAL_CHAINS} (◎ Solana + ⟠ {SUPPORTED_CHAINS['evm']} EVM)")
    logger.info("🔄 Periodic health checks: ENABLED (every 5 minutes)")
    logger.info("=" * 60)

    try:
        await asyncio.gather(
            start_http_server(),
            run_bureau(),
            periodic_health_check(),
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
