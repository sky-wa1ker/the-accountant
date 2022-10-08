import os
import aiohttp
import asyncio
import discord
import pymongo
import re
import csv
from datetime import datetime
from discord.ext import commands, tasks
from pymongo import MongoClient


token = os.environ['token']
api_key = os.environ['api_key']
db_client = MongoClient(os.environ['db_access_url'])
db = db_client.get_database('the_accountant_db')
graphql = f"https://api.politicsandwar.com/graphql?api_key={api_key}"

intents = discord.Intents.all()

client = discord.Bot(intents = intents)

@client.event
async def on_ready():
    game = discord.Game("with pirate coins.")
    await client.change_presence(status=discord.Status.online, activity=game)
    #csvexport.start()
    print('Online as {0.user}'.format(client))






@client.slash_command(description="Check your balance in Arrgh bank. Helm can check anyone else's balance by entering their nation_id.")
async def balance(ctx, nation_id:int=None):
    if nation_id:
        role = discord.utils.get(ctx.guild.roles, name="Helm")
        if role in ctx.author.roles:
            account = db.accounts.find_one({'_id':nation_id})
            if account:
                balance = account["balance"]
                if account["account_type"] == 'active':
                    color = discord.Colour.green()
                elif account["account_type"] == 'inactive':
                    color = discord.Colour.red()
                embed = discord.Embed(title=f"{account['nation_name']}\'s account balance.", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {balance["food"]}
Coal : {balance["coal"]}
Oil : {balance["oil"]}
Uranium : {balance["uranium"]}
Lead : {balance["lead"]}
Iron : {balance["iron"]}
Bauxite : {balance["bauxite"]}
Gasoline : {balance["gasoline"]}
Munitions : {balance["munitions"]}
Steel : {balance["steel"]}
Aluminum : {balance["aluminum"]}
                ''',
                color=color)
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                await ctx.respond('I could not find this nation.', ephemeral=True)
        else:
            await ctx.respond('Only Helm is allowed to see balance with nation_id.')
    else:
        cap_role = discord.utils.get(ctx.guild.roles, name="Captain")
        retir_role = discord.utils.get(ctx.guild.roles, name="Retired")
        if cap_role in ctx.author.roles or retir_role in ctx.author.roles:
            account = db.accounts.find_one({"discord_id":ctx.author.id})
            if account:
                balance = account["balance"]
                if account["account_type"] == 'active':
                    color = discord.Colour.green()
                elif account["account_type"] == 'inactive':
                    color = discord.Colour.red()
                embed = discord.Embed(title=f"{account['nation_name']}\'s account balance.", description=f'''
Money : {"${:,.2f}".format(balance["money"])}
Food : {balance["food"]}
Coal : {balance["coal"]}
Oil : {balance["oil"]}
Uranium : {balance["uranium"]}
Lead : {balance["lead"]}
Iron : {balance["iron"]}
Bauxite : {balance["bauxite"]}
Gasoline : {balance["gasoline"]}
Munitions : {balance["munitions"]}
Steel : {balance["steel"]}
Aluminum : {balance["aluminum"]}
                ''',
                color=color)
                await ctx.respond(embed=embed, ephemeral=True)
            else:
                await ctx.respond('You either do not have an account or your discord is not connected to your account yet.')
        else:
            await ctx.respond('I don\'t serve landlubbers.')




@client.slash_command(description='Helm uses this command to open a new account in database, discord not required.')
async def adduser(ctx, nation_id:int, user:discord.User=None):
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


@client.slash_command(description="Helm uses this command to add a discord account to an existing arrgh account.")
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





@client.slash_command(description="Helm uses this to manually add something to accounts, use carefully and write clear note.")
async def addbalance(ctx, nation_id:int, money:str, food:str, coal:str, oil:str, uranium:str, lead:str, iron:str, bauxite:str, gasoline:str, munitions:str, steel:str, aluminum:str,*, note):
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
                    contents = f"money: {money}, food: {food}, coal: {coal}, oil: {oil}, uranium: {uranium}, lead: {lead}, iron: {iron}, bauxite: {bauxite}, gasoline: {gasoline}, munitions: {munitions}, steel: {steel}, aluminum: {aluminum}"
                    last_tx = db.v_transactions.find().sort([('_id', -1)]).limit(1)
                    last_tx_id = dict(last_tx[0])["_id"] + 1
                    db.v_transactions.insert_one({"_id":last_tx_id, "timestamp":str({datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}), "account":nation_id, "type":"Deposit", "contents":contents, "banker":f'{ctx.author.display_name} ({ctx.author.name}),', "note":note})
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






@client.slash_command(description="Helm uses this to manually deduct something from accounts, use carefully and write clear note.")
async def deductbalance(ctx, nation_id:int, money:str, food:str, coal:str, oil:str, uranium:str, lead:str, iron:str, bauxite:str, gasoline:str, munitions:str, steel:str, aluminum:str,*, note):
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
                    contents = f"money: {money}, food: {food}, coal: {coal}, oil: {oil}, uranium: {uranium}, lead: {lead}, iron: {iron}, bauxite: {bauxite}, gasoline: {gasoline}, munitions: {munitions}, steel: {steel}, aluminum: {aluminum}"
                    last_tx = db.v_transactions.find().sort([('_id', -1)]).limit(1)
                    last_tx_id = dict(last_tx[0])["_id"] + 1
                    db.v_transactions.insert_one({"_id":last_tx_id, "timestamp":str({datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}), "account":nation_id, "type":"Withdrawal", "contents":contents, "banker":f'{ctx.author.display_name} ({ctx.author.name}),', "note":note})
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




@client.slash_command(description="Helm uses this command to set an account active.")
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




@client.slash_command(description="Helm uses this to set an account active.")
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





@tasks.loop(hours=3)
async def csvexport():
    channel = client.get_channel(312420656312614912)
    acc = db.accounts.find({})
    accounts = []
    for x in acc:
        accounts.append(x)
    keys = keys = accounts[0].keys()
    with open(f'arrgh_bank_{str(datetime.utcnow().strftime("%m_%d_%Y_%H_%M"))}.csv', 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(accounts)
        await channel.send(file=discord.File((f'arrgh_bank_{str(datetime.utcnow().strftime("%m_%d_%Y_%H_%M"))}.csv')))
        await asyncio.sleep(3)
    directory = "./"
    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(".csv")]
    for file in filtered_files:
        path_to_file = os.path.join(directory, file)
        os.remove(path_to_file)


@client.slash_command(description="Mark an account as due for audit.")
async def audit_flag(ctx, nation_id:int):
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




@client.slash_command(description="Mark an account as not due for audit.")
async def audit_clear(ctx, nation_id:int):
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






@tasks.loop(minutes=3)
async def transaction_scanner():
    role = discord.utils.get(client.get_guild(220361410616492033).roles, id=576711598912045056)
    channel = client.get_channel(798609356715196424)
    members = db.accounts.find({'account_type':'active'})
    for x in members:
        async with aiohttp.ClientSession() as session:
            if x["last_transaction_id"]:
                url = f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id={x["_id"]}&min_tx_id={x["last_transaction_id"]}'
            else:
                url = f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id={x["_id"]}'
            async with session.get(url) as r:
                transactions = await r.json()
                query = transactions['api_request']
                if query['success']:
                    for transaction in transactions['data']:
                        if transaction['sender_id'] == 913 or transaction['receiver_id'] == 913:
                            if transaction['sender_id'] == 913:
                                header_message = f'{x["nation_name"]} made a withdrawal from Arrgh bank.'
                                dcolor = 15158332
                                tx_type = 'withdrawal'
                            elif transaction['receiver_id'] == 913:
                                header_message = f'{x["nation_name"]} made a deposit into Arrgh bank.'
                                dcolor = 3066993
                                tx_type = 'deposit'
                            else:
                                header_message = 'Bruh, what kind of transaction is it?'
                                dcolor = discord.Color.default()
                                tx_type = 'unknown'
                            transaction['transaction_type'] = tx_type
                            transaction['processed'] = False
                            transaction['pushed_to_db'] = str({datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')})
                            embed = discord.Embed(title=header_message, description=f'''
    Transanction ID : **{transaction['tx_id']}**
    Date and time : {transaction['tx_datetime']}
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
                            m = await channel.send(embed=embed)
                            try:
                                if transaction['transaction_type'] == 'deposit':
                                    account = db.accounts.find_one({'_id':transaction["sender_id"]})
                                    old_bal = account["balance"]
                                    new_bal = {"money":(old_bal["money"] + transaction["money"]),"coal":(old_bal["coal"] + transaction["coal"]),"oil":(old_bal["oil"] + transaction["oil"]),"uranium":(old_bal["uranium"] + transaction["uranium"]),"iron":(old_bal["iron"] + transaction["iron"]),"bauxite":(old_bal["bauxite"] + transaction["bauxite"]),"lead":(old_bal["lead"] + transaction["lead"]),"gasoline":(old_bal["gasoline"] + transaction["gasoline"]),"munitions":(old_bal["munitions"] + transaction["munitions"]),"steel":(old_bal["steel"] + transaction["steel"]),"aluminum":(old_bal["aluminum"] + transaction["aluminum"]),"food":(old_bal["food"] + transaction["food"])}
                                    db.accounts.update_one(account, {"$set": {'balance':new_bal}})
                                    transaction['processed'] = True
                                    await m.add_reaction('✅')
                                    last_transaction = (transactions['data'][-1]['tx_id']) + 1
                                    db.accounts.update_one({'_id':x["_id"]}, {"$set": {'last_transaction_id':last_transaction}})
                                elif transaction['transaction_type'] == 'withdrawal':
                                    account = db.accounts.find_one({'_id':transaction["receiver_id"]})
                                    old_bal = account["balance"]
                                    new_bal = {"money":(old_bal["money"] - transaction["money"]),"coal":(old_bal["coal"] - transaction["coal"]),"oil":(old_bal["oil"] - transaction["oil"]),"uranium":(old_bal["uranium"] - transaction["uranium"]),"iron":(old_bal["iron"] - transaction["iron"]),"bauxite":(old_bal["bauxite"] - transaction["bauxite"]),"lead":(old_bal["lead"] - transaction["lead"]),"gasoline":(old_bal["gasoline"] - transaction["gasoline"]),"munitions":(old_bal["munitions"] - transaction["munitions"]),"steel":(old_bal["steel"] - transaction["steel"]),"aluminum":(old_bal["aluminum"] - transaction["aluminum"]),"food":(old_bal["food"] - transaction["food"])}
                                    db.accounts.update_one(account, {"$set": {'balance':new_bal}})
                                    transaction['processed'] = True
                                    await m.add_reaction('✅')
                                    last_transaction = (transactions['data'][-1]['tx_id']) + 1
                                    db.accounts.update_one({'_id':x["_id"]}, {"$set": {'last_transaction_id':last_transaction}})
                                db.transactions.insert_one(transaction)
                            except:
                                await channel.send(f"Could not precess this one. {role.mention} | <@343397899369054219>")
                                await channel.send(f'UTC timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} \n https://dashboard.heroku.com/apps/the-arrgh-ccountant/logs')
                    await asyncio.sleep(2)




'''
@tasks.loop()
async def transaction_scanner():
    role = discord.utils.get(client.get_guild(220361410616492033).roles, id=576711598912045056)
    channel = client.get_channel(798609356715196424)
    min_tax_id = "add this bit in query and remove first"
    async with aiohttp.ClientSession() as session:
        async with session.post(graphql, json={'query':f"{{bankrecs(or_id:913, first:50){{data{{id date sender_id sender_type receiver_id receiver_type banker_id note money coal oil uranium iron bauxite lead gasoline munitions steel aluminum food}}}}}}"}) as query:
            json_obj = query.json()
            transactions = json_obj["data"]["bankrecs"]["data"]
            for transaction in transactions:
                if '''
                    








client.run(token)