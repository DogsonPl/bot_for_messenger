from Bot import sql_actions

INSERT_INTO = sql_actions.InsertIntoDatabase()
GET_FROM_DB = sql_actions.GetInfoFromDatabase()
print("placek") # todo po tescie usun


async def get_user_money(person_id):
    try:
        async with GET_FROM_DB as db:
            user_money = await db.fetch_user_money(person_id)
            user_money = user_money[0][0]
    except IndexError:
        user_money = 0
    if user_money is None:
        user_money = 0
    return user_money


async def insert_into_user_money(person_id, money):
    async with INSERT_INTO as db:
        await db.insert_into_user_money(person_id, money)


async def check_daily(person_id):
    try:
        async with GET_FROM_DB as db:
            data = await db.fetch_info_if_user_got_today_daily(person_id)
            got_daily = data[0][0]
            strike = data[0][1]
    except IndexError:
        got_daily = 0
        strike = 1
    return got_daily, strike


async def insert_into_daily(person_id, strike, coins_to_give):
    money = await get_user_money(person_id)
    async with INSERT_INTO as db:
        await db.insert_into_daily(person_id)
        await db.insert_into_daily_strike(person_id, strike + 1)
    await insert_into_user_money(person_id, coins_to_give + money)


async def get_top_three_players():
    try:
        async with GET_FROM_DB as db:
            top_users = await db.fetch_top_three_players()
        return top_users
    except IndexError:
        return []
