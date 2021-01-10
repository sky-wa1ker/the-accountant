from bs4 import BeautifulSoup
import requests
import aiohttp
import asyncio
import discord
import pymongo
from discord.ext import commands, tasks
from pymongo import MongoClient


'''
token = os.environ['token']
api_key = os.environ['api_key']
db_client = MongoClient('os.environ["db_access_url"]')
'''

db_client = MongoClient('mongodb+srv://bot:bot123@discord.yal7c.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = db_client.get_database('the_accountant_db')

token = 'Nzk1NjkwNzAxMTYxNjI3NjQ5.X_NCtg._uZ8nCcut6m-3dQAF5Ywi2kH7PA'
api_key = 'fe9ac05fb01f89'

client = commands.Bot(command_prefix = '-')
client.remove_command('help')




@client.event
async def on_ready():
    game = discord.Game("with pirate coins.")
    await client.change_presence(status=discord.Status.online, activity=game)
    transaction_scanner.start()
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
        await ctx.send('There was some error, see if you\'re using the command right. (!b help).')



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
                                    last_transaction = (transanctions[-1]['tx_id']) + 1
                                    db.accounts.insert_one({'_id':int(nation_id), 'nation_name':nation_dict['name'], 'discord_id':user.id, 'balance':{'money':0, 'coal':0.0, 'oil':0.0, 'iron':0.0, 'bauxite':0.0, 'lead':0.0, 'gasoline':0.0, 'munitions':0.0, 'steel':0.0, 'aluminum':0.0, 'food':0.0}, 'last_transaction_id':last_transaction})
                                    await ctx.send(f'New account added for the nation {nation_dict["name"]} and user {user.name}!')
                        else:
                            async with session.get(f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id={nation_id}') as query:
                                json_obj = await query.json()
                                transanctions = json_obj['data']
                                last_transaction = (transanctions[-1]['tx_id']) + 1
                                db.accounts.insert_one({'_id':int(nation_id), 'nation_name':nation_dict['name'], 'balance':{'money':0, 'coal':0.0, 'oil':0.0, 'iron':0.0, 'bauxite':0.0, 'lead':0.0, 'gasoline':0.0, 'munitions':0.0, 'steel':0.0, 'aluminum':0.0, 'food':0.0}, 'last_transaction_id':last_transaction})
                                await ctx.send(f'New account added for {nation_dict["name"]}!')
                    else:
                        await ctx.send('Could not find this nation.')
    else:
        await ctx.send('You\'re not allowed to use this command, contact Helm if you want an account for yourself.')



@tasks.loop(minutes=1)
async def transaction_scanner():
    role = discord.utils.get(client.get_guild(220361410616492033).roles, id=788453390081720331)
    channel = client.get_channel(520567638779232256)
    members = db.accounts.find({})
    for x in members:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id={x["_id"]}&min_tx_id={x["last_transaction_id"]}') as r:
                transactions = await r.json()
                query = transactions['api_request']
                if query['success']:
                    for transaction in transactions['data']:
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

    

                    
@client.command()
async def process(ctx, tx_id:int):
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    if role in ctx.author.roles:
        transaction = db.transactions.find_one({'_id':tx_id})
        if transaction['proccesed']:
            await ctx.send('This transaction has already been processed.')
        else:
    else:
        await ctx.send('Only Helm is allowed to process bank transactions.')

            







client.run(token)