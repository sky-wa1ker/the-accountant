import re
import os
import aiohttp
import asyncio
import discord
import pymongo
from discord.ext import commands, tasks
from pymongo import MongoClient



token = os.environ['token']
api_key = os.environ['api_key']
db_client = MongoClient(os.environ["db_access_url"])

db = db_client.get_database('the_accountant_db')


client = commands.Bot(command_prefix = '$')
client.remove_command('help')




@client.event
async def on_ready():
    game = discord.Game("with pirate coins.")
    await client.change_presence(status=discord.Status.online, activity=game)
    transaction_scanner.start()
    dashboard_update.start()
    print('Online as {0.user}'.format(client))



@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Command is missing one or more required arguments.')
    elif isinstance(error, TypeError):
        await ctx.send('Wrong argument type.')
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'Try again in {round(error.retry_after)} seconds.')
    else:
        await ctx.send('There was some error, see if you\'re using the command right. ($help).')




@client.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency*1000)}ms')



@client.command()
async def adduser(ctx, nation_id:int, user:discord.User=None):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        if type(db.accounts.find_one({'_id':nation_id})) is dict:
            await ctx.send('This nation already has an active account.')
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://politicsandwar.com/api/nation/id={nation_id}&key={api_key}') as r:
                    nation_dict = await r.json()
                    if nation_dict['success']:
                        if user:
                            if type(db.accounts.find_one({'discord_id':user.id})) is dict:
                                await ctx.send('This user has an active account with a different nation.')
                            else:
                                async with session.get(f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id={nation_id}') as query:
                                    json_obj = await query.json()
                                    transanctions = json_obj['data']
                                    if json_obj["error_msg"] == 'No results to display.':
                                        last_transaction = None
                                    else:    
                                        last_transaction = (transanctions[-1]['tx_id']) + 1
                                    db.accounts.insert_one({'_id':int(nation_id), 'nation_name':nation_dict['name'], 'discord_id':user.id, 'account_type':'active', 'balance':{'money':0.0, 'coal':0.0, 'oil':0.0, 'uranium':0.0, 'iron':0.0, 'bauxite':0.0, 'lead':0.0, 'gasoline':0.0, 'munitions':0.0, 'steel':0.0, 'aluminum':0.0, 'food':0.0}, 'last_transaction_id':last_transaction})
                                    await ctx.send(f'New account added for the nation {nation_dict["name"]} and user {user.name}!')
                        else:
                            async with session.get(f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id={nation_id}') as query:
                                json_obj = await query.json()
                                transanctions = json_obj['data']
                                if json_obj["error_msg"] == 'No results to display.':
                                    last_transaction = None
                                else:    
                                    last_transaction = (transanctions[-1]['tx_id']) + 1
                                last_transaction = (transanctions[-1]['tx_id']) + 1
                                db.accounts.insert_one({'_id':int(nation_id), 'nation_name':nation_dict['name'], 'discord_id':None, 'account_type':'active', 'balance':{'money':0.0, 'coal':0.0, 'oil':0.0, 'uranium':0.0, 'iron':0.0, 'bauxite':0.0, 'lead':0.0, 'gasoline':0.0, 'munitions':0.0, 'steel':0.0, 'aluminum':0.0, 'food':0.0}, 'last_transaction_id':last_transaction})
                                await ctx.send(f'New account added for {nation_dict["name"]}!')
                    else:
                        await ctx.send('Could not find this nation.')
    else:
        await ctx.send('You\'re not allowed to use this command, contact Helm if you want an account for yourself.')



@tasks.loop(minutes=30)
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
                            db.transactions.insert_one(transaction)
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
                            await channel.send(f'{role.mention}')
                            await channel.send(embed=embed)
                    last_transaction = (transactions['data'][-1]['tx_id']) + 1
                    db.accounts.update_one({'_id':x["_id"]}, {"$set": {'last_transaction_id':last_transaction}})



@tasks.loop(minutes=15)
async def dashboard_update():
    channel = channel = client.get_channel(798605074477482055)
    await channel.purge()
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://politicsandwar.com/api/alliance-bank/?allianceid=913&key={api_key}') as r:
            json_obj = await r.json()
            balance = json_obj["alliance_bank_contents"][0]
            await channel.send(f' **Arrgh in-game balance:** \n**Money** : {"${:,.2f}".format(balance["money"])}, **Food** : {balance["food"]}, **Coal** : {balance["coal"]}, **Oil** : {balance["oil"]}, **Uranium** : {balance["uranium"]}, **Lead** : {balance["lead"]}, **Iron** : {balance["iron"]}, **Bauxite** : {balance["bauxite"]}, **Gasoline** : {balance["gasoline"]}, **Munitions** : {balance["munitions"]}, **Steel** : {balance["steel"]}, **Aluminum** : {balance["aluminum"]}')
            active_accounts = db.accounts.find({"account_type": 'active'})
            if active_accounts:
                await channel.send("**Active accounts:**")
                for account in active_accounts:
                    balance = account["balance"]
                    embed = discord.Embed(title=f'{account["nation_name"]} | {account["_id"]}', description=f'Money : {"${:,.2f}".format(balance["money"])}, Food : {balance["food"]}, Coal : {balance["coal"]}, Oil : {balance["oil"]}, Uranium : {balance["uranium"]}, Lead : {balance["lead"]}, Iron : {balance["iron"]}, Bauxite : {balance["bauxite"]}, Gasoline : {balance["gasoline"]}, Munitions : {balance["munitions"]}, Steel : {balance["steel"]}, Aluminum : {balance["aluminum"]}')
                    await channel.send(embed=embed)
            inactive_accounts = db.accounts.find({"account_type": 'inactive'})
            if inactive_accounts:
                await channel.send("**Inactive accounts:**")
                for account in inactive_accounts:
                    balance = account["balance"]
                    embed = discord.Embed(title=f'{account["nation_name"]} | {account["_id"]}', description=f'Money : {"${:,.2f}".format(balance["money"])}, Food : {balance["food"]}, Coal : {balance["coal"]}, Oil : {balance["oil"]}, Uranium : {balance["uranium"]}, Lead : {balance["lead"]}, Iron : {balance["iron"]}, Bauxite : {balance["bauxite"]}, Gasoline : {balance["gasoline"]}, Munitions : {balance["munitions"]}, Steel : {balance["steel"]}, Aluminum : {balance["aluminum"]}')
                    await channel.send(embed=embed)


    

                    
@client.command()
async def process(ctx, tx_id:int):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        transaction = db.transactions.find_one({'tx_id':tx_id})
        if transaction:
            if transaction['processed']:
                await ctx.send('This transaction has already been processed.')
            else:
                if transaction['transaction_type'] == 'deposit':
                    account = db.accounts.find_one({'_id':transaction["sender_id"]})
                    old_bal = account["balance"]
                    new_bal = {"money":(old_bal["money"] + transaction["money"]),"coal":(old_bal["coal"] + transaction["coal"]),"oil":(old_bal["oil"] + transaction["oil"]),"uranium":(old_bal["uranium"] + transaction["uranium"]),"iron":(old_bal["iron"] + transaction["iron"]),"bauxite":(old_bal["bauxite"] + transaction["bauxite"]),"lead":(old_bal["lead"] + transaction["lead"]),"gasoline":(old_bal["gasoline"] + transaction["gasoline"]),"munitions":(old_bal["munitions"] + transaction["munitions"]),"steel":(old_bal["steel"] + transaction["steel"]),"aluminum":(old_bal["aluminum"] + transaction["aluminum"]),"food":(old_bal["food"] + transaction["food"])}
                    db.accounts.update_one(account, {"$set": {'balance':new_bal}})
                    db.transactions.update_one(transaction, {"$set": {'processed':True}})
                    await ctx.send('Proccesed! balance updated.')
                elif transaction['transaction_type'] == 'withdrawal':
                    account = db.accounts.find_one({'_id':transaction["receiver_id"]})
                    old_bal = account["balance"]
                    new_bal = {"money":(old_bal["money"] - transaction["money"]),"coal":(old_bal["coal"] - transaction["coal"]),"oil":(old_bal["oil"] - transaction["oil"]),"uranium":(old_bal["uranium"] - transaction["uranium"]),"iron":(old_bal["iron"] - transaction["iron"]),"bauxite":(old_bal["bauxite"] - transaction["bauxite"]),"lead":(old_bal["lead"] - transaction["lead"]),"gasoline":(old_bal["gasoline"] - transaction["gasoline"]),"munitions":(old_bal["munitions"] - transaction["munitions"]),"steel":(old_bal["steel"] - transaction["steel"]),"aluminum":(old_bal["aluminum"] - transaction["aluminum"]),"food":(old_bal["food"] - transaction["food"])}
                    db.accounts.update_one(account, {"$set": {'balance':new_bal}})
                    db.transactions.update_one(transaction, {"$set": {'processed':True}})
                    await ctx.send('Proccesed! balance updated.')
        else:
            await ctx.send('Could not find this transaction.')
    else:
        await ctx.send('Only Helm is allowed to process bank transactions.')




@client.command()
async def balance(ctx, nation_id:int=None):
    if nation_id:
        role = discord.utils.get(ctx.guild.roles, name="Helm")
        if role in ctx.author.roles:
            account = db.accounts.find_one({'_id':nation_id})
            if account:
                balance = account["balance"]
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
                ''')
                await ctx.author.send(embed=embed)
                await ctx.send('Check DMs!')
            else:
                await ctx.send('I could not find this nation.')
        else:
            await ctx.send('Only Helm is allowed to see balance with nation_id.')
    else:
        role = discord.utils.get(ctx.guild.roles, name="Buccaneer")
        if role in ctx.author.roles:
            account = db.accounts.find_one({"discord_id":ctx.author.id})
            if account:
                balance = account["balance"]
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
                ''')
                await ctx.author.send(embed=embed)
                await ctx.send('Check DMs.')
            else:
                await ctx.send('You either do not have an account or your discord is not connected to your account yet.')
        else:
            await ctx.send('I don\'t serve landlubbers.')


@client.command()
async def adddiscord(ctx, nation_id:int, user:discord.User):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        account = db.accounts.find_one({'_id':nation_id})
        if account:
            discord_id = account['discord_id']
            if discord_id:
                await ctx.send('Nation already has a discord id.')
            else:
                db.accounts.update_one(account, {'$set': {"discord_id":user.id}})
                await ctx.send(f'Added {user.name}\' discord to nation {account["nation_name"]}')
        else:
            ctx.send('Could not find that nation.')
    else:
        ctx.send('You can\'t use this command, ask Helm.')
        

            

@client.command()
async def addbalance(ctx, nation_id:int, money:str, food:float, coal:float, oil:float, uranium:float, lead:float, iron:float, bauxite:float, gasoline:float, munitions:float, steel:float, aluminum:float):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        account = db.accounts.find_one({'_id':nation_id})
        if account:
            money = float(re.sub('\$|\,', '', money))
            old_bal = account["balance"]
            new_bal = {"money":(old_bal["money"] + money), "coal":(old_bal["coal"] + coal), "oil":(old_bal["oil"] + oil), "uranium":(old_bal["uranium"] + uranium), "iron":(old_bal["iron"] + iron), "bauxite":(old_bal["bauxite"] + bauxite), "lead":(old_bal["lead"] + lead), "gasoline":(old_bal["gasoline"] + gasoline), "munitions":(old_bal["munitions"] + munitions) ,"steel":(old_bal["steel"] + steel) ,"aluminum":(old_bal["aluminum"] + aluminum) ,"food":(old_bal["food"] + food)}
            db.accounts.update_one(account, {"$set": {'balance':new_bal}})
            await ctx.send('Balance updated')
        else:
            await ctx.send('Could not find that account.')
    else:
        await ctx.send('Only Helm can do manual transactions.')



@client.command()
async def deductbalance(ctx, nation_id:int, money:str, food:str, coal:str, oil:str, uranium:str, lead:str, iron:str, bauxite:str, gasoline:str, munitions:str, steel:str, aluminum:str):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        account = db.accounts.find_one({'_id':nation_id})
        if account:
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
            await ctx.send('Balance updated.')
        else:
            await ctx.send('Could not find that account.')
    else:
        await ctx.send('Only Helm can do manual transactions.')



@client.command()
async def forceprocess(ctx, tx_id:int):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        transaction = db.transactions.find_one({'tx_id':tx_id})
        if transaction:
            if transaction['processed']:
                await ctx.send('The transaction is already marked \"processed\".')
            else:
                db.transactions.update_one(transaction, {"$set":{'processed':True}})
                await ctx.send('The transaction has been marked \"processed\", and no changes to balance were made.')
        else:
            await ctx.send('Could not find that transaction.')
    else:
        await ctx.send('You are not Helm.')



@client.command()
async def activityswitch(ctx, nation_id:int):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        account = db.accounts.find_one({'_id':nation_id})
        if account:
            if account["account_type"] == 'inactive':
                db.accounts.update_one(account, {"$set": {"account_type": "active"}})
                await ctx.send("Account status changed from inactive to active.")
            elif account["account_type"] == 'active':
                db.accounts.update_one(account, {"$set": {"account_type": "inactive"}})
                await ctx.send("Account status changed from active to inactive.")
        else:
            await ctx.send('Could not find this account.')
    else:
        await ctx.send('You are not Helm.')




client.run(token)