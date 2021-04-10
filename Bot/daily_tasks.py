import asyncio
import aioschedule
from .casino_actions import DrawJackpotWinner
from .sql import handling_casino_sql
from .sql.database import loop


async def reset_daily_table():
    await handling_casino_sql.reset_casino_daily_label()
    await handling_casino_sql.reset_jackpot_label()


async def daily_tasks_scheduler():
    aioschedule.every().day.at("00:00").do(daily_tasks)
    while True:
        loop.create_task(aioschedule.run_pending())
        await asyncio.sleep(60)


async def daily_tasks():
    print("Performing daily tasks...")
    await draw_jackpot_winner.draw_jackpot_winner()
    await reset_daily_table()


async def init():
    loop.create_task(daily_tasks_scheduler())

draw_jackpot_winner = DrawJackpotWinner()
