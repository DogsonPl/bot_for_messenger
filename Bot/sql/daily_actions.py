import asyncio
import aioschedule
from Bot.casino_actions import DrawJackpotWinner


async def reset_daily_table(database):
    print("Daily has been reset...")
    await database.execute("""UPDATE casino_players
                              SET daily_strike = 1 
                              WHERE take_daily = 0;""")
    await database.execute("""UPDATE casino_players
                              SET take_daily = 0;""")


async def get_jackpot_winner():
    await draw_jackpot_winner.draw_jackpot_winner()
    await draw_jackpot_winner.reset_table()


async def restarting_scheduler(loop, database):
    aioschedule.every().day.at("00:00").do(daily_tasks, database)
    while True:
        loop.create_task(aioschedule.run_pending())
        await asyncio.sleep(60)


async def daily_tasks(database):
    await reset_daily_table(database)
    await get_jackpot_winner()


draw_jackpot_winner = DrawJackpotWinner()
