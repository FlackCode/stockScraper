import asyncio
import bots.finvizBot as finvizBot
import bots.tradingBot as tradingBot

async def main():
    await finvizBot.finvizMain()
    await tradingBot.tradingMain()

asyncio.run(main())
