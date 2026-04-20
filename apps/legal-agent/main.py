import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    agent_name = os.getenv("AGENT_NAME", "AGENT")
    agent_role = os.getenv("AGENT_ROLE", "specialist")
    logger.info(f"🤖 {agent_name} ({agent_role}) starting...")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(300)
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
