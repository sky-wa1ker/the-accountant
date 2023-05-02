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
    if not csvexport.is_running():
        csvexport.start()
    if not transaction_scanner.is_running():
        transaction_scanner.start()
    if not name_update.is_running():
        name_update.start()
    print('Online as {0.user}'.format(client))




@client.slash_command(description="Check your balance in Arrgh bank. Helm can check someone's balance by entering a nation_id or user.")
async def balance(ctx, copy_in_dm:bool=False, nation_id:int=None, user:discord.User=None):
    helm = discord.utils.get(ctx.guild.roles, name="Helm")
    if nation_id:
        if helm in ctx.author.roles:
            account = db.accounts.find_one({'_id':nation_id})
            if account:
                balance = account["balance"]
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
                ''',
                color=color)
                await ctx.respond(embed=embed, ephemeral=True)
                if copy_in_dm:
                    await ctx.author.send(embed=embed)
            else:
                await ctx.respond('This user either does not have an account or their discord is not connected to their account yet.')
        else:
            await ctx.respond('I don\'t serve landlubbers.')





@client.slash_command(description="Request a withdrawal from arrgh bank.")
async def withdraw(ctx, money:str='0', food:str='0', coal:str='0', oil:str='0', uranium:str='0', lead:str='0', iron:str='0', bauxite:str='0', gasoline:str='0', munitions:str='0', steel:str='0', aluminum:str='0'):
    role = discord.utils.get(ctx.guild.roles, name="Captain")
    helm = discord.utils.get(ctx.guild.roles, name="Helm")
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
[Withdrawal link for <@&576711598912045056>](https://politicsandwar.com/alliance/id=913&display=bank{url_str}&w_type=nation&w_recipient={(account['nation_name']).replace(" ", "+")})
[Withdrawal link for Yarr.](https://politicsandwar.com/alliance/id=4150&display=bank{url_str}&w_type=alliance&w_recipient=Arrgh)
                            ''',
                            colour=discord.Colour.dark_green())
                        await ctx.respond(embed=embed)
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
                    contents = {"money": money, "food": food, "coal": coal, "oil": oil, "uranium": uranium, "lead": lead, "iron": iron, "bauxite": bauxite, "gasoline": gasoline, "munitions": munitions, "steel": steel, "aluminum": aluminum}
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
                    contents = {"money": money, "food": food, "coal": coal, "oil": oil, "uranium": uranium, "lead": lead, "iron": iron, "bauxite": bauxite, "gasoline": gasoline, "munitions": munitions, "steel": steel, "aluminum": aluminum}
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



@tasks.loop(minutes=360)
async def name_update():
    accounts_cursor = db.accounts.find()
    accounts = []
    for x in accounts_cursor:
        accounts.append(x['_id'])
    async with aiohttp.ClientSession() as session:
        async with session.post(graphql, json={'query':f"{{nations(first: 500, id:{accounts}){{data{{id nation_name}}}}}}"}) as r:
            json_obj = await r.json()
            nations = json_obj["data"]["nations"]["data"]
            for nation in nations:
                if int(nation["id"]) in accounts:
                    db.accounts.update_one({'_id':int(nation["id"])}, {"$set": {'nation_name':nation["nation_name"]}})




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






@tasks.loop(minutes=2)
async def transaction_scanner():
    role = discord.utils.get(client.get_guild(220361410616492033).roles, id=576711598912045056)
    channel = client.get_channel(798609356715196424) 
    opsec_channel = client.get_channel(1031144610417868874)
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
                        'pushed_to_db':str({datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')})
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






client.run(token)