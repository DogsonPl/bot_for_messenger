import asyncio
import aioschedule
from . import database


async def reset_daily_table():
    print("Daily has been reset...")
    await database.execute("""UPDATE casino_players
                              SET daily_strike = 1 
                              WHERE take_daily = 0;""")
    await database.execute("""UPDATE casino_players
                              SET take_daily = 0;""")


async def restarting_scheduler(loop):
    aioschedule.every().day.at("00:00").do(daily_tasks)
    while True:
        loop.create_task(aioschedule.run_pending())
        await asyncio.sleep(60)


async def daily_tasks():
    await reset_daily_table()

