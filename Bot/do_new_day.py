import asyncio
import aioschedule
from .casino_actions import DrawJackpotWinner
from .sql.database import cursor, loop


async def reset_daily_table():
    print("Daily has been reset...")
    await cursor.execute("""UPDATE casino_players
                              SET daily_strike = 1 
                              WHERE take_daily = 0;""")
    await cursor.execute("""UPDATE casino_players
                              SET take_daily = 0;""")


async def restarting_scheduler():
    aioschedule.every().day.at("00:00").do(daily_tasks)
    while True:
        loop.create_task(aioschedule.run_pending())
        await asyncio.sleep(60)


async def daily_tasks():
    await reset_daily_table()
    await draw_jackpot_winner.draw_jackpot_winner()


draw_jackpot_winner = DrawJackpotWinner()
