import os
import aiohttp
import asyncio
import discord
import pymongo
import re
import csv
from datetime import datetime, timezone
from discord.ext import commands, tasks
from pymongo import MongoClient


token = os.environ['TOKEN']
api_key = os.environ['API_KEY']
db_client = MongoClient(os.environ['DB_ACCESS_URL'])
db = db_client.get_database('the_accountant_db')
graphql = f"https://api.politicsandwar.com/graphql?api_key={api_key}"
sam_api_key = os.environ['SAM_API_KEY']
potato_api_key = os.environ['POTATO_API_KEY']
bank_bot_key = os.environ['X_BOT_KEY']
potato_graphql = f"https://api.politicsandwar.com/graphql?api_key={potato_api_key}"
headers = {
    "X-Bot-Key": bank_bot_key,
    "X-Api-Key": sam_api_key
}



intents = discord.Intents.all()

client = discord.Bot(intents = intents)

@client.event
async def on_ready():
    game = discord.Game("with pirate coins.")
    await client.change_presence(status=discord.Status.online, activity=game)
    if not csvexport.is_running():
        csvexport.start()
    if not transaction_scanner.is_running():
        transaction_scanner.start()
    if not name_update.is_running():
        name_update.start()
    print('Online as {0.user}'.format(client))





balance = discord.SlashCommandGroup("balance", "Balance related commands")

@balance.command(description="Check your balance in Arrgh bank.")
async def check(ctx,
                  copy_in_dm:discord.Option(bool, "Sends a copy in your DM if set to True", default=False),
                  nation_id:discord.Option(int, "Helm can check balance for any nation with this", required=False),
                  user:discord.Option(discord.User, "Helm can check balance for any user", required=False),
                  bank_value:discord.Option(bool, "Shows the total value of your bank if set to True", required=False)):
    
    helm = discord.utils.get(ctx.guild.roles, name="Helm")
    bank_total_value = 'not opted to check.'
    if nation_id:
        if helm in ctx.author.roles:
            account = db.accounts.find_one({'_id':nation_id})
            if account:
                balance = account["balance"]
                if bank_value:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(graphql, json={'query':"{tradeprices(first:1){data{coal oil uranium iron bauxite lead gasoline munitions steel aluminum food}}}"}) as query:
                            json_obj = await query.json()
                            prices = json_obj["data"]["tradeprices"]["data"][0]
                            bank_total_value_float = (balance["money"]) + (balance["food"]*prices["food"]) + (balance["coal"]*prices["coal"]) + (balance["oil"]*prices["oil"]) + (balance["uranium"]*prices["uranium"]) + (balance["lead"]*prices["lead"]) + (balance["iron"]*prices["iron"]) + (balance["bauxite"]*prices["bauxite"]) + (balance["gasoline"]*prices["gasoline"]) + (balance["munitions"]*prices["munitions"]) + (balance["steel"]*prices["steel"]) + (balance["aluminum"]*prices["aluminum"])
                            bank_total_value = "${:,.2f}".format(bank_total_value_float)
                if account["account_type"] == 'active':
                    color = discord.Colour.green()
                elif account["account_type"] == 'inactive':
                    color = discord.Colour.red()
                embed = discord.Embed(title=f"{account['nation_name']}\'s account balance.", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {"{:,.2f}".format(balance["food"])}
Coal : {"{:,.2f}".format(balance["coal"])}
Oil : {"{:,.2f}".format(balance["oil"])}
Uranium : {"{:,.2f}".format(balance["uranium"])}
Lead : {"{:,.2f}".format(balance["lead"])}
Iron : {"{:,.2f}".format(balance["iron"])}
Bauxite : {"{:,.2f}".format(balance["bauxite"])}
Gasoline : {"{:,.2f}".format(balance["gasoline"])}
Munitions : {"{:,.2f}".format(balance["munitions"])}
Steel : {"{:,.2f}".format(balance["steel"])}
Aluminum : {"{:,.2f}".format(balance["aluminum"])}

Total Bank Value : **{bank_total_value}**
                ''',
                color=color)
                await ctx.respond(embed=embed, ephemeral=True)
                if copy_in_dm:
                    await ctx.author.send(embed=embed)
            else:
                await ctx.respond('I could not find this nation.', ephemeral=True)
        else:
            await ctx.respond('Only Helm is allowed to see balance with nation_id.')
    else:
        cap_role = discord.utils.get(ctx.guild.roles, name="Captain")
        retir_role = discord.utils.get(ctx.guild.roles, name="Retired")
        if cap_role in ctx.author.roles or retir_role in ctx.author.roles:
            if user and helm in ctx.author.roles:
                pass
            else:
                user = ctx.author
            account = db.accounts.find_one({"discord_id":user.id})
            if account:
                balance = account["balance"]
                if bank_value:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(graphql, json={'query':"{tradeprices(first:1){data{coal oil uranium iron bauxite lead gasoline munitions steel aluminum food}}}"}) as query:
                            json_obj = await query.json()
                            prices = json_obj["data"]["tradeprices"]["data"][0]
                            bank_total_value_float = (balance["money"]) + (balance["food"]*prices["food"]) + (balance["coal"]*prices["coal"]) + (balance["oil"]*prices["oil"]) + (balance["uranium"]*prices["uranium"]) + (balance["lead"]*prices["lead"]) + (balance["iron"]*prices["iron"]) + (balance["bauxite"]*prices["bauxite"]) + (balance["gasoline"]*prices["gasoline"]) + (balance["munitions"]*prices["munitions"]) + (balance["steel"]*prices["steel"]) + (balance["aluminum"]*prices["aluminum"])
                            bank_total_value = "${:,.2f}".format(bank_total_value_float)
                if account["account_type"] == 'active':
                    color = discord.Colour.green()
                elif account["account_type"] == 'inactive':
                    color = discord.Colour.red()
                embed = discord.Embed(title=f"{account['nation_name']}\'s account balance.", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {"{:,.2f}".format(balance["food"])}
Coal : {"{:,.2f}".format(balance["coal"])}
Oil : {"{:,.2f}".format(balance["oil"])}
Uranium : {"{:,.2f}".format(balance["uranium"])}
Lead : {"{:,.2f}".format(balance["lead"])}
Iron : {"{:,.2f}".format(balance["iron"])}
Bauxite : {"{:,.2f}".format(balance["bauxite"])}
Gasoline : {"{:,.2f}".format(balance["gasoline"])}
Munitions : {"{:,.2f}".format(balance["munitions"])}
Steel : {"{:,.2f}".format(balance["steel"])}
Aluminum : {"{:,.2f}".format(balance["aluminum"])}

Total Bank Value : **{bank_total_value}**
                ''',
                color=color)
                await ctx.respond(embed=embed, ephemeral=True)
                if copy_in_dm:
                    await ctx.author.send(embed=embed)
            else:
                await ctx.respond('This user either does not have an account or their discord is not connected to their account yet.')
        else:
            await ctx.respond('I don\'t serve landlubbers.')




@balance.command(description="Helm uses this to add money to an account")
async def add(ctx, nation_id:int, money:str, food:str, coal:str, oil:str, uranium:str, lead:str, iron:str, bauxite:str, gasoline:str, munitions:str, steel:str, aluminum:str,*, note):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    channel = client.get_channel(542384682818600971)
    if ctx.channel == channel:
        if role in ctx.author.roles:
            account = db.accounts.find_one({'_id':nation_id})
            if account:
                try:
                    money = float(re.sub('\$|\,', '', money))
                    food = float(food.replace(',', ''))
                    coal = float(coal.replace(',', ''))
                    oil = float(oil.replace(',', ''))
                    uranium = float(uranium.replace(',', ''))
                    lead = float(lead.replace(',', ''))
                    iron = float(iron.replace(',', ''))
                    bauxite = float(bauxite.replace(',', ''))
                    gasoline = float(gasoline.replace(',', ''))
                    munitions = float(munitions.replace(',', ''))
                    steel = float(steel.replace(',', ''))
                    aluminum = float(aluminum.replace(',', ''))
                    old_bal = account["balance"]
                    new_bal = {"money":(old_bal["money"] + money), "coal":(old_bal["coal"] + coal), "oil":(old_bal["oil"] + oil), "uranium":(old_bal["uranium"] + uranium), "iron":(old_bal["iron"] + iron), "bauxite":(old_bal["bauxite"] + bauxite), "lead":(old_bal["lead"] + lead), "gasoline":(old_bal["gasoline"] + gasoline), "munitions":(old_bal["munitions"] + munitions) ,"steel":(old_bal["steel"] + steel) ,"aluminum":(old_bal["aluminum"] + aluminum) ,"food":(old_bal["food"] + food)}
                    db.accounts.update_one(account, {"$set": {'balance':new_bal}})
                    contents = {"money": money, "food": food, "coal": coal, "oil": oil, "uranium": uranium, "lead": lead, "iron": iron, "bauxite": bauxite, "gasoline": gasoline, "munitions": munitions, "steel": steel, "aluminum": aluminum}
                    last_tx = db.v_transactions.find().sort([('_id', -1)]).limit(1)
                    last_tx_id = dict(last_tx[0])["_id"] + 1
                    db.v_transactions.insert_one({"_id":last_tx_id, "timestamp":str({datetime.now(timezone.utc).strftime('%B %d %Y - %H:%M:%S')}), "account":nation_id, "type":"Deposit", "contents":contents, "banker":f'{ctx.author.display_name} ({ctx.author.name}),', "note":note})
                    await ctx.respond(f'''
{ctx.author.name} added ``${money:,} cash, {food:,} food, {coal:,} coal, {oil:,} oil, {uranium:,} uranium, {lead:,} lead, {iron:,} iron, {bauxite:,} bauxite, {gasoline:,} gasoline, {munitions:,} munitions, {steel:,} steel, {aluminum:,} aluminum`` 
to ``account: {nation_id}``
note : ``{note}``
Virtual transaction ID is : ``{last_tx_id}``
    ''')
                except:
                    await ctx.respond('There was an error, check your arguments.', ephemeral=True)
            else:
                await ctx.respond('Could not find that account.', ephemeral=True)
        else:
            await ctx.respond('Only Helm can do manual transactions.', ephemeral=True)
    else:
        await ctx.respond(f'This command can only be used in {channel.mention}.', ephemeral=True)






@balance.command(description="Helm uses this to deduct money from an account")
async def deduct(ctx, nation_id:int, money:str, food:str, coal:str, oil:str, uranium:str, lead:str, iron:str, bauxite:str, gasoline:str, munitions:str, steel:str, aluminum:str,*, note):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    channel = client.get_channel(542384682818600971)
    if ctx.channel == channel:
        if role in ctx.author.roles:
            account = db.accounts.find_one({'_id':nation_id})
            if account:
                try:
                    money = float(re.sub('\$|\,', '', money))
                    food = float(food.replace(',', ''))
                    coal = float(coal.replace(',', ''))
                    oil = float(oil.replace(',', ''))
                    uranium = float(uranium.replace(',', ''))
                    lead = float(lead.replace(',', ''))
                    iron = float(iron.replace(',', ''))
                    bauxite = float(bauxite.replace(',', ''))
                    gasoline = float(gasoline.replace(',', ''))
                    munitions = float(munitions.replace(',', ''))
                    steel = float(steel.replace(',', ''))
                    aluminum = float(aluminum.replace(',', ''))
                    old_bal = account["balance"]
                    new_bal = {"money":(old_bal["money"] - money), "coal":(old_bal["coal"] - coal), "oil":(old_bal["oil"] - oil), "uranium":(old_bal["uranium"] - uranium), "iron":(old_bal["iron"] - iron), "bauxite":(old_bal["bauxite"] - bauxite), "lead":(old_bal["lead"] - lead), "gasoline":(old_bal["gasoline"] - gasoline), "munitions":(old_bal["munitions"] - munitions) ,"steel":(old_bal["steel"] - steel) ,"aluminum":(old_bal["aluminum"] - aluminum) ,"food":(old_bal["food"] - food)}
                    db.accounts.update_one(account, {"$set": {'balance':new_bal}})
                    contents = {"money": money, "food": food, "coal": coal, "oil": oil, "uranium": uranium, "lead": lead, "iron": iron, "bauxite": bauxite, "gasoline": gasoline, "munitions": munitions, "steel": steel, "aluminum": aluminum}
                    last_tx = db.v_transactions.find().sort([('_id', -1)]).limit(1)
                    last_tx_id = dict(last_tx[0])["_id"] + 1
                    db.v_transactions.insert_one({"_id":last_tx_id, "timestamp":str({datetime.now(timezone.utc).strftime('%B %d %Y - %H:%M:%S')}), "account":nation_id, "type":"Withdrawal", "contents":contents, "banker":f'{ctx.author.display_name} ({ctx.author.name}),', "note":note})
                    await ctx.respond(f'''
{ctx.author.name} deducted ``${money:,} cash, {food:,} food, {coal:,} coal, {oil:,} oil, {uranium:,} uranium, {lead:,} lead, {iron:,} iron, {bauxite:,} bauxite, {gasoline:,} gasoline, {munitions:,} munitions, {steel:,} steel, {aluminum:,} aluminum`` 
from ``account: {nation_id}``
note : ``{note}``
Virtual transaction ID is : ``{last_tx_id}``
    ''')
                except:
                    await ctx.respond('There was an error, check your arguments.', ephemeral=True)
            else:
                await ctx.respond('Could not find that account.', ephemeral=True)
        else:
            await ctx.respond('Only Helm can do manual transactions.', ephemeral=True)
    else:
        await ctx.respond(f'This command can only be used in {channel.mention}.', ephemeral=True)

client.add_application_command(balance)




@client.slash_command(description="Request a withdrawal from arrgh bank.")
async def withdraw(ctx, ping:bool=True, money:str='0', food:str='0', coal:str='0', oil:str='0', uranium:str='0', lead:str='0', iron:str='0', bauxite:str='0', gasoline:str='0', munitions:str='0', steel:str='0', aluminum:str='0'):
    role = discord.utils.get(ctx.guild.roles, name="Captain")
    helm = discord.utils.get(ctx.guild.roles, name="Helm")
    misc = db.misc.find_one({'_id':True})
    current_offshore = misc['current_offshore']
    channel = client.get_channel(400427307334107158)
    if role in ctx.author.roles:
        if ctx.channel == channel:
            account = db.accounts.find_one({"discord_id":ctx.author.id})
            if account:
                try:
                    money = float(re.sub('\$|\,', '', money))
                    food = float(food.replace(',', ''))
                    coal = float(coal.replace(',', ''))
                    oil = float(oil.replace(',', ''))
                    uranium = float(uranium.replace(',', ''))
                    lead = float(lead.replace(',', ''))
                    iron = float(iron.replace(',', ''))
                    bauxite = float(bauxite.replace(',', ''))
                    gasoline = float(gasoline.replace(',', ''))
                    munitions = float(munitions.replace(',', ''))
                    steel = float(steel.replace(',', ''))
                    aluminum = float(aluminum.replace(',', ''))
                    bal = account["balance"]
                    bal_check = [
                        bal["money"] >= money,
                        bal["food"] >= food,
                        bal["coal"] >= coal,
                        bal["oil"] >= oil,
                        bal["uranium"] >= uranium,
                        bal["lead"] >= lead,
                        bal["iron"] >= iron,
                        bal["bauxite"] >= bauxite,
                        bal["gasoline"] >= gasoline,
                        bal["munitions"] >= munitions,
                        bal["steel"] >= steel,
                        bal["aluminum"] >= aluminum
                    ]
                    if all(bal_check):
                        resources = {"money":money, "food":food, "coal":coal, "oil":oil, "uranium":uranium, "lead":lead, "iron":iron, "bauxite":bauxite, "gasoline":gasoline, "munitions":munitions, "steel":steel, "aluminum":aluminum}
                        url_str = ""
                        for resource in resources:
                            if resources[resource] > 0:
                                url_str += f"&w_{resource}={int(resources[resource])}"
                        embed = discord.Embed(
                            title=f"``{account['nation_name']}``'s withdrawal request.",
                            description=f'''
*double check nation name*^
Nation/Account ID : {account['_id']}

Money : {"${:,.2f}".format(money)}
Food : {"{:,.2f}".format(food)}
Coal : {"{:,.2f}".format(coal)}
Oil : {"{:,.2f}".format(oil)}
Uranium : {"{:,.2f}".format(uranium)}
Lead : {"{:,.2f}".format(lead)}
Iron : {"{:,.2f}".format(iron)}
Bauxite : {"{:,.2f}".format(bauxite)}
Gasoline : {"{:,.2f}".format(gasoline)}
Munitions : {"{:,.2f}".format(munitions)}
Steel : {"{:,.2f}".format(steel)}
Aluminum : {"{:,.2f}".format(aluminum)}
[Withdrawal link for Helm.](https://politicsandwar.com/alliance/id=913&display=bank{url_str}&w_type=nation&w_recipient={(account['nation_name']).replace(" ", "+")})
[Withdrawal link for Yarr.](https://politicsandwar.com/alliance/id={current_offshore}&display=bank{url_str}&w_type=alliance&w_recipient=Arrgh)
                            ''',
                            colour=discord.Colour.dark_green())
                        await ctx.respond(embed=embed)
                        if ping:
                            await ctx.send(helm.mention)
                    else:
                        await ctx.respond('You are requesting more than you have in arrgh bank.', ephemeral=True)
                except:
                    await ctx.respond('There was an error, check your arguments.', ephemeral=True)
            else:
                await ctx.respond('You either do not have an account or your discord is not connected to your account yet.', ephemeral=True)
        else:
            await ctx.respond(f'This command can only be used in {channel.mention}.', ephemeral=True)
    else:
        await ctx.respond('I don\'t serve landlubbers.')



bank = discord.SlashCommandGroup("bank", "Commands for Arrgh bank, for Helm use only.")


@bank.command(description="Check contents of Arrgh bank.")
async def balance(ctx,
                  select_bank:discord.Option(str, "Check balance for Arrgh bank", choices=["Arrgh Bank", "Potato Bank"]),):
    await ctx.defer(ephemeral=True)
    helm = discord.utils.get(ctx.guild.roles, name="Helm")
    if helm not in ctx.author.roles:
        await ctx.respond("You do not have permission to use this command.")
        return
    if select_bank == "Arrgh Bank":
        async with aiohttp.ClientSession() as session:
            async with session.post(graphql, json={'query':"query{alliances(id:913){data{money coal oil uranium lead iron bauxite gasoline munitions steel aluminum food}}}"}) as query:        
                result = await query.json()
                balance = result['data']['alliances']['data'][0]
                embed = discord.Embed(title="Arrgh Bank Balance", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {"{:,.2f}".format(balance["food"])}
Coal : {"{:,.2f}".format(balance["coal"])}
Oil : {"{:,.2f}".format(balance["oil"])}
Uranium : {"{:,.2f}".format(balance["uranium"])}
Lead : {"{:,.2f}".format(balance["lead"])}
Iron : {"{:,.2f}".format(balance["iron"])}
Bauxite : {"{:,.2f}".format(balance["bauxite"])}
Gasoline : {"{:,.2f}".format(balance["gasoline"])}
Munitions : {"{:,.2f}".format(balance["munitions"])}
Steel : {"{:,.2f}".format(balance["steel"])}
Aluminum : {"{:,.2f}".format(balance["aluminum"])}
                                      ''')
                await ctx.respond(embed=embed)
    elif select_bank == "Potato Bank":
        async with aiohttp.ClientSession() as session:
            async with session.post(potato_graphql, json={'query':"query{alliances(id:13633){data{money coal oil uranium lead iron bauxite gasoline munitions steel aluminum food}}}"}) as query:        
                result = await query.json()
                balance = result['data']['alliances']['data'][0]
                embed = discord.Embed(title="Potato Bank Balance", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {"{:,.2f}".format(balance["food"])}
Coal : {"{:,.2f}".format(balance["coal"])}
Oil : {"{:,.2f}".format(balance["oil"])}
Uranium : {"{:,.2f}".format(balance["uranium"])}
Lead : {"{:,.2f}".format(balance["lead"])}
Iron : {"{:,.2f}".format(balance["iron"])}
Bauxite : {"{:,.2f}".format(balance["bauxite"])}
Gasoline : {"{:,.2f}".format(balance["gasoline"])}
Munitions : {"{:,.2f}".format(balance["munitions"])}
Steel : {"{:,.2f}".format(balance["steel"])}
Aluminum : {"{:,.2f}".format(balance["aluminum"])}
                                      ''')
                await ctx.respond(embed=embed)


@bank.command(description="Transfer ALL contents of Arrgh bank to Yarr or Potato bank")
async def flush(ctx,
                  select_bank:discord.Option(str, "Flush balance to Yarr or Potato bank", choices=["Yarr Bank", "Potato Bank", "Custom"]),
                  custom_aa_id:discord.Option(int, "If custom, enter alliance ID here", required=False),
                  note:discord.Option(str, "Optional note", required=False, default="I am bot.")):
    await ctx.defer()
    
    helm = discord.utils.get(ctx.guild.roles, name="Helm")
    if helm not in ctx.author.roles:
        await ctx.respond("You do not have permission to use this command.")
        return
    
    channel = client.get_channel(400427307334107158)
    if ctx.channel != channel:
        await ctx.respond(f"This command can only be used in {channel.mention}.")
        return
    
    if select_bank == "Yarr Bank":
        async with aiohttp.ClientSession() as session:
            async with session.post(graphql, json={'query':"query{alliances(id:913){data{money food coal oil uranium lead iron bauxite gasoline munitions steel aluminum}}}"}) as query:        
                result = await query.json()
                balance = result['data']['alliances']['data'][0]
                if balance['money'] < 1 and balance['food'] < 1 and balance['coal'] < 1 and balance['oil'] < 1 and balance['uranium'] < 1 and balance['lead'] < 1 and balance['iron'] < 1 and balance['bauxite'] < 1 and balance['gasoline'] < 1 and balance['munitions'] < 1 and balance['steel'] < 1 and balance['aluminum'] < 1:
                    await ctx.respond("Arrgh bank is empty, nothing to flush.")
                    return
                embed = discord.Embed(title="Arrgh Bank Balance", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {"{:,.2f}".format(balance["food"])}
Coal : {"{:,.2f}".format(balance["coal"])}
Oil : {"{:,.2f}".format(balance["oil"])}
Uranium : {"{:,.2f}".format(balance["uranium"])}
Lead : {"{:,.2f}".format(balance["lead"])}
Iron : {"{:,.2f}".format(balance["iron"])}
Bauxite : {"{:,.2f}".format(balance["bauxite"])}
Gasoline : {"{:,.2f}".format(balance["gasoline"])}
Munitions : {"{:,.2f}".format(balance["munitions"])}
Steel : {"{:,.2f}".format(balance["steel"])}
Aluminum : {"{:,.2f}".format(balance["aluminum"])}

All this will be transferred to Yarr bank.
React with 👍 to confirm transfer, or 👎 to cancel.
''')
                message = await ctx.respond(embed=embed)
                await message.add_reaction("👍")
                await message.add_reaction("👎")
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["👍", "👎"] and reaction.message.id == message.id
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.respond('👎 Transfer timed out.')
                    await message.delete()
                    return
                
                if str(reaction.emoji) == "👎":
                    await ctx.respond('👎 Transfer cancelled.')
                    await message.delete()
                    return
                elif str(reaction.emoji) == "👍":
                    try:
                        async with session.post(graphql, headers=headers, json={'query':f'mutation{{bankWithdraw(note:"{ctx.author.display_name} says {note}" receiver:4150 receiver_type:2 money:{balance["money"]} food:{balance["food"]} coal:{balance["coal"]} oil:{balance["oil"]} uranium:{balance["uranium"]} lead:{balance["lead"]} iron:{balance["iron"]} bauxite:{balance["bauxite"]} gasoline:{balance["gasoline"]} munitions:{balance["munitions"]} steel:{balance["steel"]} aluminum:{balance["aluminum"]} ) {{id}}}}'}) as query:
                            result = await query.json()
                            if query.status != 200:
                                await ctx.respond(f"Connection Error: {query.status}")
                                await message.delete()
                                return
                    except Exception as e:
                        await ctx.respond(f"Error making this transaction: {e}")
                        await message.delete()
                        return
                    await message.delete()
                    if 'errors' in result:
                        await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                        return
                    await ctx.respond(f"Flushed all assets to Yarr bank with transaction ID: {result['data']['bankWithdraw']['id']}")

    elif select_bank == "Potato Bank":
        async with aiohttp.ClientSession() as session:
            async with session.post(graphql, json={'query':"query{alliances(id:913){data{money food coal oil uranium lead iron bauxite gasoline munitions steel aluminum}}}"}) as query:        
                result = await query.json()
                balance = result['data']['alliances']['data'][0]
                if balance['money'] < 1 and balance['food'] < 1 and balance['coal'] < 1 and balance['oil'] < 1 and balance['uranium'] < 1 and balance['lead'] < 1 and balance['iron'] < 1 and balance['bauxite'] < 1 and balance['gasoline'] < 1 and balance['munitions'] < 1 and balance['steel'] < 1 and balance['aluminum'] < 1:
                    await ctx.respond("Arrgh bank is empty, nothing to flush.")
                    return
                embed = discord.Embed(title="Arrgh Bank Balance", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {"{:,.2f}".format(balance["food"])}
Coal : {"{:,.2f}".format(balance["coal"])}
Oil : {"{:,.2f}".format(balance["oil"])}
Uranium : {"{:,.2f}".format(balance["uranium"])}
Lead : {"{:,.2f}".format(balance["lead"])}
Iron : {"{:,.2f}".format(balance["iron"])}
Bauxite : {"{:,.2f}".format(balance["bauxite"])}
Gasoline : {"{:,.2f}".format(balance["gasoline"])}
Munitions : {"{:,.2f}".format(balance["munitions"])}
Steel : {"{:,.2f}".format(balance["steel"])}
Aluminum : {"{:,.2f}".format(balance["aluminum"])}

All this will be transferred to Potato bank.
React with 👍 to confirm transfer, or 👎 to cancel.
''')
                message = await ctx.respond(embed=embed)
                await message.add_reaction("👍")
                await message.add_reaction("👎")
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["👍", "👎"] and reaction.message.id == message.id
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=20.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.respond('👎 Transfer timed out.')
                    await message.delete()
                    return
                if str(reaction.emoji) == "👎":
                    await ctx.respond('👎 Transfer cancelled.')
                    await message.delete()
                    return
                elif str(reaction.emoji) == "👍":
                    try:
                        async with session.post(graphql, headers=headers, json={'query':f'mutation{{bankWithdraw(note:"{ctx.author.display_name} says {note}" receiver:13633 receiver_type:2 money:{balance["money"]} food:{balance["food"]} coal:{balance["coal"]} oil:{balance["oil"]} uranium:{balance["uranium"]} lead:{balance["lead"]} iron:{balance["iron"]} bauxite:{balance["bauxite"]} gasoline:{balance["gasoline"]} munitions:{balance["munitions"]} steel:{balance["steel"]} aluminum:{balance["aluminum"]} ) {{id}}}}'}) as query:
                            result = await query.json()
                            if query.status != 200:
                                await ctx.respond(f"Connection Error: {query.status}")
                                await message.delete()
                                return
                    except Exception as e:
                        await ctx.respond(f"Error making this transaction: {e}")
                        await message.delete()
                        return
                    await message.delete()
                    if 'errors' in result:
                        await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                        return
                    await ctx.respond(f"Flushed all assets to Potato bank with transaction ID: {result['data']['bankWithdraw']['id']}")

    
    
    elif select_bank == "Custom":
        if custom_aa_id is None:
            await ctx.respond("You must enter a custom alliance ID if you select Custom.")
            return
        async with aiohttp.ClientSession() as session:
            async with session.post(graphql, json={'query':"query{alliances(id:913){data{money food coal oil uranium lead iron bauxite gasoline munitions steel aluminum}}}"}) as query:        
                result = await query.json()
                balance = result['data']['alliances']['data'][0]
                if balance['money'] < 1 and balance['food'] < 1 and balance['coal'] < 1 and balance['oil'] < 1 and balance['uranium'] < 1 and balance['lead'] < 1 and balance['iron'] < 1 and balance['bauxite'] < 1 and balance['gasoline'] < 1 and balance['munitions'] < 1 and balance['steel'] < 1 and balance['aluminum'] < 1:
                    await ctx.respond("Arrgh bank is empty, nothing to flush.")
                    return
                embed = discord.Embed(title="Arrgh Bank Balance", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {"{:,.2f}".format(balance["food"])}
Coal : {"{:,.2f}".format(balance["coal"])}
Oil : {"{:,.2f}".format(balance["oil"])}
Uranium : {"{:,.2f}".format(balance["uranium"])}
Lead : {"{:,.2f}".format(balance["lead"])}
Iron : {"{:,.2f}".format(balance["iron"])}
Bauxite : {"{:,.2f}".format(balance["bauxite"])}
Gasoline : {"{:,.2f}".format(balance["gasoline"])}
Munitions : {"{:,.2f}".format(balance["munitions"])}
Steel : {"{:,.2f}".format(balance["steel"])}
Aluminum : {"{:,.2f}".format(balance["aluminum"])}

All this will be transferred to alliance ID {custom_aa_id}.
React with 👍 to confirm transfer, or 👎 to cancel.
''')
                message = await ctx.respond(embed=embed)
                await message.add_reaction("👍")
                await message.add_reaction("👎")
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["👍", "👎"] and reaction.message.id == message.id
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.respond('👎 Transfer timed out.')
                    await message.delete()
                    return
                if str(reaction.emoji) == "👎":
                    await ctx.respond('👎 Transfer cancelled.')
                    await message.delete()
                    return
                elif str(reaction.emoji) == "👍":
                    try:
                        async with session.post(graphql, headers=headers, json={'query':f'mutation{{bankWithdraw(note:"{ctx.author.display_name} says {note}" receiver:{custom_aa_id} receiver_type:2 money:{balance["money"]} food:{balance["food"]} coal:{balance["coal"]} oil:{balance["oil"]} uranium:{balance["uranium"]} lead:{balance["lead"]} iron:{balance["iron"]} bauxite:{balance["bauxite"]} gasoline:{balance["gasoline"]} munitions:{balance["munitions"]} steel:{balance["steel"]} aluminum:{balance["aluminum"]} ) {{id}}}}'}) as query:
                            result = await query.json()
                            if query.status != 200:
                                await ctx.respond(f"Connection Error: {query.status}")
                                await message.delete()
                                return
                    except Exception as e:
                        await ctx.respond(f"Error making this transaction: {e}")
                        await message.delete()
                        return
                    await message.delete()
                    if 'errors' in result:
                        await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                        return
                    await ctx.respond(f"Flushed all assets to alliance ID {custom_aa_id} with transaction ID: {result['data']['bankWithdraw']['id']}")



@bank.command(description="ONLY for third party transfers from Arrgh bank. Use other commands for anything else.")
async def transfer(ctx,
                   from_bank:discord.Option(str, "Choose the bank to send it from.", choices=["Arrgh Bank", "Potato Bank"]),
                   receiver_type:discord.Option(str, "Choose receiver type.", choices=["Alliance", "Nation"]),
                   receiver_id:int,
                   note:discord.Option(str, "Mandatory note", required=True),
                   money:int=0, food:int=0, coal:int=0, oil:int=0, uranium:int=0, lead:int=0, iron:int=0, bauxite:int=0, gasoline:int=0, munitions:int=0, steel:int=0, aluminum:int=0):
    await ctx.defer()

    helm = discord.utils.get(ctx.guild.roles, name="Helm")
    if helm not in ctx.author.roles:
        await ctx.respond("You do not have permission to use this command.")
        return

    
    url = graphql if from_bank == "Arrgh Bank" else potato_graphql
    r_type = 2 if receiver_type == "Alliance" else 1

    receiver = None
    if r_type == 2:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'query':f"query{{alliances(id:{receiver_id}){{data{{name id}}}}}}"}) as query:
                result = await query.json()
                if 'errors' in result:
                    await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                    return
                if result['data']['alliances']['data'] == []:
                    await ctx.respond(f"Alliance ID {receiver_id} not found.")
                    return
                receiver = result['data']['alliances']['data'][0]['name']
    else:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'query':f"query{{nations(id:{receiver_id}){{data{{nation_name id}}}}}}"}) as query:
                result = await query.json()
                if 'errors' in result:
                    await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                    return
                if result['data']['nations']['data'] == []:
                    await ctx.respond(f"Nation ID {receiver_id} not found.")
                    return
                receiver = result['data']['nations']['data'][0]['nation_name']
    if receiver is None:
        await ctx.respond("Error finding receiver.")
        return

    embed = discord.Embed(title="Confirm Transfer", description=f'''
Transferring the following from {from_bank} to ({receiver_id}) {receiver}

Money : {"${:,.2f}".format(money)}
Food : {"{:,.2f}".format(food)}
Coal : {"{:,.2f}".format(coal)}
Oil : {"{:,.2f}".format(oil)}
Uranium : {"{:,.2f}".format(uranium)}
Lead : {"{:,.2f}".format(lead)}
Iron : {"{:,.2f}".format(iron)}
Bauxite : {"{:,.2f}".format(bauxite)}
Gasoline : {"{:,.2f}".format(gasoline)}
Munitions : {"{:,.2f}".format(munitions)}
Steel : {"{:,.2f}".format(steel)}
Aluminum : {"{:,.2f}".format(aluminum)}

In 60 seconds react with 👍 to confirm or 👎 to cancel.
''')
    message = await ctx.respond(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["👍", "👎"] and reaction.message.id == message.id
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.respond('👎 Transfer timed out.')
        await message.delete()
        return
    if str(reaction.emoji) == "👎":
        await ctx.respond('👎 Transfer cancelled.')
        await message.delete()
        return
    elif str(reaction.emoji) == "👍":
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json={'query':f'mutation{{bankWithdraw(note:"{ctx.author.display_name} says {note}" receiver:{receiver_id} receiver_type:{r_type} money:{money} food:{food} coal:{coal} oil:{oil} uranium:{uranium} lead:{lead} iron:{iron} bauxite:{bauxite} gasoline:{gasoline} munitions:{munitions} steel:{steel} aluminum:{aluminum} ) {{id}}}}'}) as query:
                    result = await query.json()
                    if query.status != 200:
                        await ctx.respond(f"Connection Error: {query.status}")
                        await message.delete()
                        return
            except Exception as e:
                await ctx.respond(f"Error making this transaction: {e}")
                await message.delete()
                return
            if 'errors' in result:
                await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                await message.delete()
                return
            await message.delete()
            await ctx.respond(f'''
Transferred following from {from_bank} to ({receiver_id}) {receiver} with transaction ID: {result['data']['bankWithdraw']['id']}
```Money : {"${:,.2f}".format(money)}, Food : {"{:,.2f}".format(food)}, Coal : {"{:,.2f}".format(coal)}, Oil : {"{:,.2f}".format(oil)}, Uranium : {"{:,.2f}".format(uranium)}, Lead : {"{:,.2f}".format(lead)}, Iron : {"{:,.2f}".format(iron)}, Bauxite : {"{:,.2f}".format(bauxite)}, Gasoline : {"{:,.2f}".format(gasoline)}, Munitions : {"{:,.2f}".format(munitions)}, Steel : {"{:,.2f}".format(steel)}, Aluminum : {"{:,.2f}".format(aluminum)}```
''')
            



@bank.command(description="Make a withdrawal from Arrgh bank. For Helm use only.")
async def withdraw(ctx,
                   from_bank:discord.Option(str, "Choose the bank to withdraw from.", choices=["Arrgh Bank", "Potato Bank"]),
                   captain_id:discord.Option(int, "Enter the captain's nation ID to withdraw to."),
                   note:discord.Option(str, "Optional note", required=False, default="I am bot."),
                   money:int=0, food:int=0, coal:int=0, oil:int=0, uranium:int=0, lead:int=0, iron:int=0, bauxite:int=0, gasoline:int=0, munitions:int=0, steel:int=0, aluminum:int=0,
                   ):
    await ctx.defer()

    helm = discord.utils.get(ctx.guild.roles, name="Helm")
    if helm not in ctx.author.roles:
        await ctx.respond("You do not have permission to use this command. If you are a captain needing a withdrawal, use the ``/withdrawal`` command instead.")
        return
    
    channel = client.get_channel(400427307334107158)
    if ctx.channel != channel:
        await ctx.respond(f"This command can only be used in {channel.mention}.")
        return

    if money < 1 and food < 1 and coal < 1 and oil < 1 and uranium < 1 and lead < 1 and iron < 1 and bauxite < 1 and gasoline < 1 and munitions < 1 and steel < 1 and aluminum < 1:
        await ctx.respond("You must withdraw at least something.")
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(graphql, json={'query':f"query{{nations(id:{captain_id}){{data{{nation_name id alliance_id}}}}}}"}) as query:
            result = await query.json()
            if 'errors' in result:
                await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                return
            if result['data']['nations']['data'] == []:
                await ctx.respond(f"Nation ID {captain_id} not found.")
                return
            if result['data']['nations']['data'][0]['alliance_id'] != '913':
                await ctx.respond(f"Nation ID {captain_id} is not in Arrgh alliance. Use transfer command instead. {result}")
                return
            captain = result['data']['nations']['data'][0]['nation_name']

    embed = discord.Embed(title="Confirm Withdrawal", description=f'''
Withdrawing the following from {from_bank} to ({captain_id}) {captain}

Money : {"${:,.2f}".format(money)}
Food : {"{:,.2f}".format(food)}
Coal : {"{:,.2f}".format(coal)}
Oil : {"{:,.2f}".format(oil)}
Uranium : {"{:,.2f}".format(uranium)}
Lead : {"{:,.2f}".format(lead)}
Iron : {"{:,.2f}".format(iron)}
Bauxite : {"{:,.2f}".format(bauxite)}
Gasoline : {"{:,.2f}".format(gasoline)}
Munitions : {"{:,.2f}".format(munitions)}
Steel : {"{:,.2f}".format(steel)}
Aluminum : {"{:,.2f}".format(aluminum)}

In 60 seconds, react with 👍 to confirm or 👎 to cancel.
''')
    message = await ctx.respond(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["👍", "👎"] and reaction.message.id == message.id
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.respond('👎 Withdrawal timed out.')
        await message.delete()
        return
    
    if str(reaction.emoji) == "👎":
        await ctx.respond('👎 Withdrawal cancelled.')
        await message.delete()
        return
    elif str(reaction.emoji) == "👍":
        if from_bank == "Arrgh Bank":
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(graphql, headers=headers, json={'query':f'mutation{{bankWithdraw(note:"{ctx.author.display_name} says {note}" receiver:{captain_id} receiver_type:1 money:{money} food:{food} coal:{coal} oil:{oil} uranium:{uranium} lead:{lead} iron:{iron} bauxite:{bauxite} gasoline:{gasoline} munitions:{munitions} steel:{steel} aluminum:{aluminum} ) {{id}}}}'}) as query:
                        result = await query.json()
                        if query.status != 200:
                            await message.delete()
                            await ctx.respond(f"Connection Error: {query.status}")
                            return
                except Exception as e:
                    await message.delete()
                    await ctx.respond(f"Error making this transaction: {e}")
                    return
                if 'errors' in result:
                    await message.delete()
                    await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                    return
                await message.delete()
                await ctx.respond(f'''Sent following from Arrgh Bank to ({captain_id}) {captain} with transaction ID: {result['data']['bankWithdraw']['id']}
```Money : {"${:,.2f}".format(money)}, Food : {"{:,.2f}".format(food)}, Coal : {"{:,.2f}".format(coal)}, Oil : {"{:,.2f}".format(oil)}, Uranium : {"{:,.2f}".format(uranium)}, Lead : {"{:,.2f}".format(lead)}, Iron : {"{:,.2f}".format(iron)}, Bauxite : {"{:,.2f}".format(bauxite)}, Gasoline : {"{:,.2f}".format(gasoline)}, Munitions : {"{:,.2f}".format(munitions)}, Steel : {"{:,.2f}".format(steel)}, Aluminum : {"{:,.2f}".format(aluminum)}```
''')


        else:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(potato_graphql, headers=headers, json={'query':f'mutation{{bankWithdraw(note:"{ctx.author.display_name} doing transfer to Arrgh bank for withdrawal." receiver:913 receiver_type:2 money:{money} food:{food} coal:{coal} oil:{oil} uranium:{uranium} lead:{lead} iron:{iron} bauxite:{bauxite} gasoline:{gasoline} munitions:{munitions} steel:{steel} aluminum:{aluminum} ) {{id}}}}'}) as query:
                        result = await query.json()
                        if query.status != 200:
                            await message.delete()
                            await ctx.respond(f"Connection Error: {query.status}")
                            return
                except Exception as e:
                    await message.delete()
                    await ctx.respond(f"Error making this transaction: {e}")
                    return
                if 'errors' in result:
                    await message.delete()
                    await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                    return
                
            await asyncio.sleep(2)
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(graphql, headers=headers, json={'query':f'mutation{{bankWithdraw(note:"{ctx.author.display_name} says {note}" receiver:{captain_id} receiver_type:1 money:{money} food:{food} coal:{coal} oil:{oil} uranium:{uranium} lead:{lead} iron:{iron} bauxite:{bauxite} gasoline:{gasoline} munitions:{munitions} steel:{steel} aluminum:{aluminum} ) {{id}}}}'}) as query:
                        result = await query.json()
                        if query.status != 200:
                            await message.delete()
                            await ctx.respond(f"Connection Error: {query.status}")
                            return
                except Exception as e:
                    await message.delete()
                    await ctx.respond(f"Error making this transaction: {e}")
                    return
                if 'errors' in result:
                    await message.delete()
                    await ctx.respond(f"Error from server: {result['errors'][0]['message']}")
                    return
                await message.delete()
                await ctx.respond(f'''Sent following from Potato Bank to ({captain_id}) {captain} with transaction ID: {result['data']['bankWithdraw']['id']}
```Money : {"${:,.2f}".format(money)}, Food : {"{:,.2f}".format(food)}, Coal : {"{:,.2f}".format(coal)}, Oil : {"{:,.2f}".format(oil)}, Uranium : {"{:,.2f}".format(uranium)}, Lead : {"{:,.2f}".format(lead)}, Iron : {"{:,.2f}".format(iron)}, Bauxite : {"{:,.2f}".format(bauxite)}, Gasoline : {"{:,.2f}".format(gasoline)}, Munitions : {"{:,.2f}".format(munitions)}, Steel : {"{:,.2f}".format(steel)}, Aluminum : {"{:,.2f}".format(aluminum)}```
''')


client.add_application_command(bank)




account = discord.SlashCommandGroup("account", "Account related commands")

@account.command(description="Create a new account in arrgh bank, only for Helm")
async def create(ctx, nation_id:int, user:discord.User=None):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role not in ctx.author.roles:
        await ctx.respond('You\'re not allowed to use this command, contact Helm if you want an account for yourself.')
    else:
        if type(db.accounts.find_one({'_id':nation_id})) is dict:
            account = db.accounts.find_one({'_id':nation_id})
            await ctx.respond(f'This nation already has an {account["account_type"]} account.')
        else:
            await ctx.defer()
            async with aiohttp.ClientSession() as session:
                async with session.post(graphql, json={'query':f'{{nations(id: {nation_id}, first: 1) {{data {{id nation_name}}}} bankrecs(or_id:{nation_id}, first: 1){{data{{id}}}}}}'}) as query:
                    json_obj = await query.json()
                    nations = json_obj["data"]["nations"]["data"]
                    bankrecs = json_obj["data"]["bankrecs"]["data"]
                    if len(nations) == 0:
                        await ctx.followup.send('Could not find this nation.')
                    else:
                        if len(bankrecs) == 1:
                            last_transaction = int(bankrecs[0]["id"]) + 1
                        else:
                            last_transaction = None
                        if user:
                            if type(db.accounts.find_one({'discord_id':user.id})) is dict:
                                await ctx.followup.send('This user has an active account with a different nation.')
                            else:
                                global discord_id
                                discord_id = user.id
                        else:
                            discord_id = None
                        db.accounts.insert_one({'_id':int(nation_id), 'nation_name':nations[0]['nation_name'], 'discord_id':discord_id, 'account_type':'active', 'balance':{'money':0.0, 'coal':0.0, 'oil':0.0, 'uranium':0.0, 'iron':0.0, 'bauxite':0.0, 'lead':0.0, 'gasoline':0.0, 'munitions':0.0, 'steel':0.0, 'aluminum':0.0, 'food':0.0}, 'last_transaction_id':last_transaction, 'audit_needed':False})
                        await ctx.followup.send(f'New account added for the nation {nations[0]["nation_name"]} and user {user.name}! last transacion is {last_transaction}.')


@account.command(description="Add discord to an account, only for Helm")

async def adddiscord(ctx, nation_id:int, user:discord.User):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        account = db.accounts.find_one({'_id':nation_id})
        if account:
            discord_id = account['discord_id']
            if discord_id:
                await ctx.respond('Nation already has a discord id.')
            else:
                db.accounts.update_one(account, {'$set': {"discord_id":user.id}})
                await ctx.respond(f'Added {user.name}\'s discord to nation {account["nation_name"]}')
        else:
            await ctx.respond('Could not find that nation.')
    else:
        await ctx.respond('You can\'t use this command, ask Helm.')




@account.command(description="Get last 5 transactions of your nation.")
async def transactions(ctx, nation_id:discord.Option(int, "Only Helm can use this.", required=False)): # type: ignore
    await ctx.defer()
    helm = discord.utils.get(ctx.guild.roles, name="Helm")
    if nation_id and helm in ctx.author.roles:
        pass
    else:
        try:
            nation_id = db.accounts.find_one({"discord_id":ctx.user.id})['_id']
        except:
            await ctx.respond("Can't find your account.", ephemeral=True)
    transactions = [transaction for transaction in db.transactions.find({ '$or': [{'sender_id':nation_id}, {'receiver_id':nation_id}] }).sort({"tx_id": -1}).limit(5)]
    if len(transactions) < 5:
        await ctx.respond('You have less than 5 transactions, try again when you have more.')
    else:
        embed = discord.Embed(title=f"Last 5 transactions of {nation_id}", description=f'''
```json
Type: {transactions[0]['transaction_type']}
Money: {"${:,.2f}".format(transactions[0]["money"])}, Food: {"{:,.2f}".format(transactions[0]['food'])}, Coal: {"{:,.2f}".format(transactions[0]['coal'])}, Oil: {"{:,.2f}".format(transactions[0]['oil'])}, Uranium: {"{:,.2f}".format(transactions[0]['uranium'])}, Iron : {"{:,.2f}".format(transactions[0]['iron'])}, Bauxite: {"{:,.2f}".format(transactions[0]['bauxite'])}, Lead: {"{:,.2f}".format(transactions[0]['lead'])}, Gasoline: {"{:,.2f}".format(transactions[0]['gasoline'])}, Steel: {"{:,.2f}".format(transactions[0]['steel'])}, Aluminum: {"{:,.2f}".format(transactions[0]['aluminum'])}
```
```json
Type: {transactions[1]['transaction_type']}
Money: {"${:,.2f}".format(transactions[1]["money"])}, Food: {"{:,.2f}".format(transactions[1]['food'])}, Coal: {"{:,.2f}".format(transactions[1]['coal'])}, Oil: {"{:,.2f}".format(transactions[1]['oil'])}, Uranium: {"{:,.2f}".format(transactions[1]['uranium'])}, Iron : {"{:,.2f}".format(transactions[1]['iron'])}, Bauxite: {"{:,.2f}".format(transactions[1]['bauxite'])}, Lead: {"{:,.2f}".format(transactions[1]['lead'])}, Gasoline: {"{:,.2f}".format(transactions[1]['gasoline'])}, Steel: {"{:,.2f}".format(transactions[1]['steel'])}, Aluminum: {"{:,.2f}".format(transactions[1]['aluminum'])}
```
```json
Type: {transactions[2]['transaction_type']}
Money: {"${:,.2f}".format(transactions[2]["money"])}, Food: {"{:,.2f}".format(transactions[2]['food'])}, Coal: {"{:,.2f}".format(transactions[2]['coal'])}, Oil: {"{:,.2f}".format(transactions[2]['oil'])}, Uranium: {"{:,.2f}".format(transactions[2]['uranium'])}, Iron : {"{:,.2f}".format(transactions[2]['iron'])}, Bauxite: {"{:,.2f}".format(transactions[2]['bauxite'])}, Lead: {"{:,.2f}".format(transactions[2]['lead'])}, Gasoline: {"{:,.2f}".format(transactions[2]['gasoline'])}, Steel: {"{:,.2f}".format(transactions[2]['steel'])}, Aluminum: {"{:,.2f}".format(transactions[2]['aluminum'])}
```
```json
Type: {transactions[3]['transaction_type']}
Money: {"${:,.2f}".format(transactions[3]["money"])}, Food: {"{:,.2f}".format(transactions[3]['food'])}, Coal: {"{:,.2f}".format(transactions[3]['coal'])}, Oil: {"{:,.2f}".format(transactions[3]['oil'])}, Uranium: {"{:,.2f}".format(transactions[3]['uranium'])}, Iron : {"{:,.2f}".format(transactions[3]['iron'])}, Bauxite: {"{:,.2f}".format(transactions[3]['bauxite'])}, Lead: {"{:,.2f}".format(transactions[3]['lead'])}, Gasoline: {"{:,.2f}".format(transactions[3]['gasoline'])}, Steel: {"{:,.2f}".format(transactions[3]['steel'])}, Aluminum: {"{:,.2f}".format(transactions[3]['aluminum'])}
```
```json
Type: {transactions[4]['transaction_type']}
Money: {"${:,.2f}".format(transactions[4]["money"])}, Food: {"{:,.2f}".format(transactions[4]['food'])}, Coal: {"{:,.2f}".format(transactions[4]['coal'])}, Oil: {"{:,.2f}".format(transactions[4]['oil'])}, Uranium: {"{:,.2f}".format(transactions[4]['uranium'])}, Iron : {"{:,.2f}".format(transactions[4]['iron'])}, Bauxite: {"{:,.2f}".format(transactions[4]['bauxite'])}, Lead: {"{:,.2f}".format(transactions[4]['lead'])}, Gasoline: {"{:,.2f}".format(transactions[4]['gasoline'])}, Steel: {"{:,.2f}".format(transactions[4]['steel'])}, Aluminum: {"{:,.2f}".format(transactions[4]['aluminum'])}
```
''')
        await ctx.respond(embed=embed, ephemeral=True)




@account.command(description="Set an account active, only for Helm")
async def active(ctx, nation_id:int):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles: # 1
        await ctx.defer()
        account = db.accounts.find_one({'_id':nation_id})
        if account:
            if account["account_type"] == 'inactive':
                async with aiohttp.ClientSession() as session:
                    async with session.post(graphql, json={'query':f'{{bankrecs(or_id: {nation_id}, first: 1) {{data {{id}}}}}}'}) as query:
                        json_obj = await query.json()
                        transanctions = json_obj['data']['bankrecs']['data']
                        if len(transanctions) > 0:
                            last_transaction = int(transanctions[0]['id']) + 1
                            db.accounts.update_one(account, {"$set": {"account_type": "active", "last_transaction_id": last_transaction}})
                            await ctx.respond("Account status changed from inactive to active.")
                        else:
                            await ctx.respond("epic api fail, help! <@343397899369054219>")
            else:
                await ctx.respond("Account is already active.")
        else:
            await ctx.respond("Could not find this account.")
    else:
        await ctx.respond("You are not Helm.")




@account.command(description="Set an account inactive, only for Helm")
async def inactive(ctx, nation_id:int):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles: # 1
        await ctx.defer()
        account = db.accounts.find_one({'_id':nation_id})
        if account:
            if account["account_type"] == 'active':
                db.accounts.update_one(account, {"$set": {"account_type": "inactive"}})
                await ctx.respond("Account status changed from active to inactive.")
            else:
                await ctx.respond("Account is already inactive.")
        else:
            await ctx.respond("Could not find this account.")
    else:
        await ctx.respond("You are not Helm.")


audit = account.create_subgroup("audit", description="Mark an account as due for audit or not due for audit.")

@audit.command(description="Mark an account as due for audit.")
async def flag(ctx, nation_id:int):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        account = db.accounts.find_one({'_id':nation_id})
        if account:
            if account["audit_needed"] == True:
                await ctx.respond("Account is already flagged for audit.", ephemeral=True)
            else:
                db.accounts.update_one(account, {"$set": {"audit_needed": True}})
                await ctx.respond("Account flagged for audit.", ephemeral=True)
        else:
            await ctx.respond("Could not find this account.", ephemeral=True)
    else:
        await ctx.respond("You are not Helm.", ephemeral=True)




@audit.command(description="Mark an account as not due for audit.")
async def clear(ctx, nation_id:int):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        account = db.accounts.find_one({'_id':nation_id})
        if account:
            if account["audit_needed"] == False:
                await ctx.respond("Account is not flagged for audit.", ephemeral=True)
            else:
                db.accounts.update_one(account, {"$set": {"audit_needed": False}})
                await ctx.respond("Audit flag removed from account.", ephemeral=True)
        else:
            await ctx.respond("Could not find this account.", ephemeral=True)
    else:
        await ctx.respond("You are not Helm.", ephemeral=True)

client.add_application_command(account)




loan = discord.SlashCommandGroup("loan", "Loan related commands")
@loan.command(description="Add a new loan")
async def add(ctx, note:str, nation_id:int, name:str, money:int=0, food:int=0, coal:int=0,
              oil:int=0, uranium:int=0, lead:int=0, iron:int=0, bauxite:int=0,
              gasoline:int=0, munitions:int=0, steel:int=0, aluminum:int=0):
    
    await ctx.defer()
    channel = client.get_channel(542384682818600971)
    admiral = discord.utils.get(ctx.guild.roles, name="Admiral")
    last_loan = db.loans.find().sort([('_id', -1)]).limit(1)
    last_loan_id = dict(last_loan[0])["_id"] + 1


    if not admiral in ctx.author.roles:
        await ctx.respond("Only an admiral can use this command")

    else:
        try:
            if ctx.channel == channel:
                db.loans.insert_one({
                    "_id":last_loan_id,
                    "status":"active",
                    "banker":f"{ctx.author.display_name} ({ctx.author.name})",
                    "note":note,
                    "nation_id":nation_id,
                    "name":name,
                    "money":money,
                    "food":food,
                    "coal":coal,
                    "oil":oil,
                    "uranium":uranium,
                    "lead":lead,
                    "iron":iron,
                    "bauxite":bauxite,
                    "gasoline":gasoline,
                    "munitions":munitions,
                    "steel":steel,
                    "aluminum":aluminum
                })
                await ctx.respond(f'''
{ctx.author.name} granted loan for ``${money:,} cash, {food:,} food, {coal:,} coal, {oil:,} oil, {uranium:,} uranium, {lead:,} lead, {iron:,} iron, {bauxite:,} bauxite, {gasoline:,} gasoline, {munitions:,} munitions, {steel:,} steel, {aluminum:,} aluminum`` 
to ``{name} ({nation_id})``
Loan ID is: ``{last_loan_id}``
Note: ``{note}``
    ''')
            else:
                await ctx.respond(f"This command can only be used in {channel.mention}")
        except:
            await ctx.respond("Could not add loan. Please try again later.")
client.add_application_command(loan)






@tasks.loop(minutes=5)
async def transaction_scanner():
    role = discord.utils.get(client.get_guild(220361410616492033).roles, id=576711598912045056)
    channel = client.get_channel(798609356715196424) 
    opsec_channel = client.get_channel(1031144610417868874)
    logs_channel = client.get_channel(312420656312614912)
    accounts_cursor = db.accounts.find({"account_type":"active"},{"_id":1})
    account_ids = []
    for x in accounts_cursor:
        account_ids.append(x["_id"])
    misc = db.misc.find_one({'_id':True})
    yarr_ids = misc['yarr_ids']
    last_tx_id = misc['last_arrgh_tx']
    async with aiohttp.ClientSession() as session:
        async with session.post(graphql, json={'query':f"{{alliances(id:913){{data{{bankrecs(min_id:{last_tx_id}, orderBy:{{column:ID, order:DESC}}){{id date sender_id sender_type sender{{leader_name nation_name}}receiver_id receiver_type receiver{{leader_name nation_name}}banker_id banker{{leader_name nation_name}} note money coal oil uranium iron bauxite lead gasoline munitions steel aluminum food}}}}}}}}"}) as query:
            json_obj = await query.json()
            try:
                transactions = json_obj["data"]["alliances"]["data"][0]["bankrecs"]
                if len(transactions) > 0:
                    for transaction in transactions:
                        await asyncio.sleep(1)
                        if int(transaction["sender_id"]) in account_ids:
                            header_message = f'{transaction["sender"]["leader_name"]} of {transaction["sender"]["nation_name"]} made a deposit into Arrgh bank.'
                            dcolor = 3066993
                            tx_type = 'deposit'
                        elif int(transaction["receiver_id"]) in account_ids:
                            header_message = f'{transaction["receiver"]["leader_name"]} of {transaction["receiver"]["nation_name"]} made a withdrawal from Arrgh bank.'
                            dcolor = 15158332
                            tx_type = 'withdrawal'
                        elif (transaction["receiver_type"] == 1 and int(transaction["receiver_id"]) not in account_ids) and ((transaction["note"]).endswith("the alliance bank inventory.") == False):
                            header_message = f'{transaction["banker"]["leader_name"]} processed a third party withdrawal for {transaction["receiver"]["nation_name"]}.'
                            dcolor = 15158332
                            tx_type = 'tp_withdrawal'
                        elif (transaction["receiver_type"] == 1 and int(transaction["receiver_id"]) not in account_ids) and ((transaction["note"]).endswith("the alliance bank inventory.")):
                            header_message = f'{transaction["banker"]["leader_name"]} lost a war to {transaction["receiver"]["nation_name"]}.'
                            dcolor = 15158332
                            tx_type = 'bank_loot'
                        elif (transaction["receiver_type"] == 2 and transaction["sender_type"] == 2) and (transaction["sender_id"] == '913'):
                            header_message = f'{transaction["banker"]["leader_name"]} sent following resources to an alliance from Arrgh bank.'
                            dcolor = 15158332
                            tx_type = 'aa_withdrawal'
                        elif (transaction["receiver_type"] == 2 and transaction["sender_type"] == 2) and (transaction["receiver_id"] == '913'):
                            header_message = f'{transaction["banker"]["leader_name"]} sent following resources from their alliance to Arrgh bank.'
                            dcolor = 3066993
                            tx_type = 'aa_deposit'
                        else:
                            tx_type = 'unknown'
                        db_transaction = {
                            'tx_id':int(transaction['id']),
                            'tx_datetime':transaction['date'],
                            'sender_id':int(transaction['sender_id']),
                            'sender_type':transaction['sender_type'],
                            'receiver_id':int(transaction['receiver_id']),
                            'receiver_type':transaction['receiver_type'],
                            'banker_nation_id':int(transaction['banker_id']),
                            'note':transaction['note'],
                            'money':transaction['money'],
                            'coal':transaction['coal'],
                            'oil':transaction['oil'],
                            'uranium':transaction['uranium'],
                            'iron':transaction['iron'],
                            'bauxite':transaction['bauxite'],
                            'lead':transaction['lead'],
                            'gasoline':transaction['gasoline'],
                            'munitions':transaction['munitions'],
                            'steel':transaction['steel'],
                            'aluminum':transaction['aluminum'],
                            'food':transaction['food'],
                            'transaction_type':tx_type,
                            'processed':False,
                            'pushed_to_db':str({datetime.now(timezone.utc).strftime('%B %d %Y - %H:%M:%S')})
                        }

                        embed = discord.Embed(title=header_message, description=f'''
Transanction ID : **{transaction['id']}**
Date and time : {transaction['date']}
Note : {transaction['note']}
**Contents**:
Money : ${transaction['money']}
Coal : {transaction['coal']}
Oil : {transaction['oil']}
Uranium : {transaction['uranium']}
Iron : {transaction['iron']}
Bauxite : {transaction['bauxite']}
Lead : {transaction['lead']}
Gasoline : {transaction['gasoline']}
Munitions : {transaction['munitions']}
Steel : {transaction['steel']}
Aluminum : {transaction['aluminum']}
Food : {transaction['food']}''', color=dcolor)

                        try:
                            if db_transaction['transaction_type'] == 'deposit':
                                if db.transactions.find_one({'tx_id':int(transaction['id'])}) is None:
                                    m = await channel.send(embed=embed)
                                    account = db.accounts.find_one({'_id':int(transaction["sender_id"])})
                                    old_bal = account["balance"]
                                    new_bal = {"money":(old_bal["money"] + transaction["money"]),"coal":(old_bal["coal"] + transaction["coal"]),"oil":(old_bal["oil"] + transaction["oil"]),"uranium":(old_bal["uranium"] + transaction["uranium"]),"iron":(old_bal["iron"] + transaction["iron"]),"bauxite":(old_bal["bauxite"] + transaction["bauxite"]),"lead":(old_bal["lead"] + transaction["lead"]),"gasoline":(old_bal["gasoline"] + transaction["gasoline"]),"munitions":(old_bal["munitions"] + transaction["munitions"]),"steel":(old_bal["steel"] + transaction["steel"]),"aluminum":(old_bal["aluminum"] + transaction["aluminum"]),"food":(old_bal["food"] + transaction["food"])}
                                    db.accounts.update_one(account, {"$set": {'balance':new_bal}})
                                    db_transaction['processed'] = True
                                    await m.add_reaction('✅')
                                    last_transaction = int(transactions[0]['id']) + 1
                                    db.accounts.update_one({'_id':account["_id"]}, {"$set": {'last_transaction_id':last_transaction}})
                                    db.misc.update_one({'_id':True}, {"$set": {'last_arrgh_tx':last_transaction}})
                                    db.transactions.insert_one(db_transaction)

                            elif db_transaction['transaction_type'] == 'withdrawal':
                                if db.transactions.find_one({'tx_id':int(transaction['id'])}) is None:
                                    m = await channel.send(embed=embed)
                                    account = db.accounts.find_one({'_id':int(transaction["receiver_id"])})
                                    old_bal = account["balance"]
                                    new_bal = {"money":(old_bal["money"] - transaction["money"]),"coal":(old_bal["coal"] - transaction["coal"]),"oil":(old_bal["oil"] - transaction["oil"]),"uranium":(old_bal["uranium"] - transaction["uranium"]),"iron":(old_bal["iron"] - transaction["iron"]),"bauxite":(old_bal["bauxite"] - transaction["bauxite"]),"lead":(old_bal["lead"] - transaction["lead"]),"gasoline":(old_bal["gasoline"] - transaction["gasoline"]),"munitions":(old_bal["munitions"] - transaction["munitions"]),"steel":(old_bal["steel"] - transaction["steel"]),"aluminum":(old_bal["aluminum"] - transaction["aluminum"]),"food":(old_bal["food"] - transaction["food"])}
                                    db.accounts.update_one(account, {"$set": {'balance':new_bal}})
                                    db_transaction['processed'] = True
                                    await m.add_reaction('✅')
                                    last_transaction = int(transactions[0]['id']) + 1
                                    db.accounts.update_one({'_id':account["_id"]}, {"$set": {'last_transaction_id':last_transaction}})
                                    db.misc.update_one({'_id':True}, {"$set": {'last_arrgh_tx':last_transaction}})
                                    db.transactions.insert_one(db_transaction)

                            elif db_transaction['transaction_type'] == 'tp_withdrawal':
                                if db.tp_transactions.find_one({'tx_id':int(transaction['id'])}) is None:
                                    await opsec_channel.send(f"{role.mention}")
                                    await opsec_channel.send(embed=embed)
                                    db.tp_transactions.insert_one(db_transaction)
                                    last_transaction = int(transactions[0]['id']) + 1
                                    db.misc.update_one({'_id':True}, {"$set": {'last_arrgh_tx':last_transaction}})
                                
                            elif db_transaction['transaction_type'] == 'bank_loot':
                                await opsec_channel.send(embed=embed)
                                last_transaction = int(transactions[0]['id']) + 1
                                db.misc.update_one({'_id':True}, {"$set": {'last_arrgh_tx':last_transaction}})

                            elif db_transaction['transaction_type'] == 'aa_withdrawal':
                                if db.tp_transactions.find_one({'tx_id':int(transaction['id'])}) is None:
                                    await opsec_channel.send(embed=embed)
                                    db.tp_transactions.insert_one(db_transaction)
                                    last_transaction = int(transactions[0]['id']) + 1
                                    db.misc.update_one({'_id':True}, {"$set": {'last_arrgh_tx':last_transaction}})
                                    if int(transaction["receiver_id"]) in yarr_ids:
                                        await opsec_channel.send("note: looks like Yarr safekeep.")
                                    else:
                                        await opsec_channel.send(f"{role.mention}")

                            elif db_transaction['transaction_type'] == 'aa_deposit':
                                if db.tp_transactions.find_one({'tx_id':int(transaction['id'])}) is None:
                                    await opsec_channel.send(embed=embed)
                                    db.tp_transactions.insert_one(db_transaction)
                                    last_transaction = int(transactions[0]['id']) + 1
                                    db.misc.update_one({'_id':True}, {"$set": {'last_arrgh_tx':last_transaction}})
                                    if int(transaction["sender_id"]) in yarr_ids:
                                        await opsec_channel.send("note: looks like Yarr withdrawal.")
                                    else:
                                        await opsec_channel.send(f"{role.mention}")

                            elif db_transaction['transaction_type'] == 'unknown':
                                await opsec_channel.send(f'{role.mention} unknown type tx_id: {transaction["id"]}')
                        except:
                            await channel.send(f'{role.mention} could not process tx_id: {transaction["id"]}')
            except:
                await logs_channel.send(f'Having trouble fetching transaction. Is the API down?')



@tasks.loop(hours=4)
async def csvexport():
    channel = client.get_channel(312420656312614912)
    acc = db.accounts.find({})
    accounts = [x for x in acc]
    if accounts:
        keys = accounts[0].keys()
        filename = f'arrgh_bank_{datetime.now(timezone.utc).strftime("%m_%d_%Y_%H_%M")}.csv'
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(accounts)
        await channel.send(file=discord.File(filename))
        try:
            os.remove(filename)
        except Exception as e:
            print(f"Failed to delete {filename}: {e}")



@tasks.loop(minutes=360)
async def name_update():
    logs_channel = client.get_channel(312420656312614912)
    accounts_cursor = db.accounts.find()
    accounts = []
    for x in accounts_cursor:
        accounts.append(x['_id'])
    async with aiohttp.ClientSession() as session:
        async with session.post(graphql, json={'query':f"{{nations(first: 500, id:{accounts}){{data{{id nation_name}}}}}}"}) as r:
            json_obj = await r.json()
            nations = json_obj["data"]["nations"]["data"]
            try:
                for nation in nations:
                    if int(nation["id"]) in accounts:
                        db.accounts.update_one({'_id':int(nation["id"])}, {"$set": {'nation_name':nation["nation_name"]}})
            except:
                await logs_channel.send(f'Having trouble fetching nations. Is the API down?')








client.run(token)
