import asyncio
import aioschedule


async def reset_daily(database):
    print("Daily has been reset...")
    await database.execute("""UPDATE casino_players
                                SET daily_strike = 1 
                                WHERE take_daily = 0;""")
    await database.execute("""UPDATE casino_players
                                SET take_daily = 0;""")


async def restarting_daily_in_db(loop, database):
    aioschedule.every().day.at("00:00").do(reset_daily, database)
    while True:
        loop.create_task(aioschedule.run_pending())
        await asyncio.sleep(60)
