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
    print('Online as {0.user}'.format(client))


'''
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
'''


@client.command()
@commands.cooldown(1, 120, commands.BucketType.user)
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency*1000)}ms')



@client.command()
async def test(ctx):
    role = discord.utils.get(ctx.guild.roles, id=788453390081720331)
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id=176311&s_only&min_tx_id=62723954') as r:
            json_obj = await r.json()
            transanction = json_obj["data"][0]
            embed = discord.Embed(title='Markovia made a deposit into Arrgh bank.', description=f'''
Transanction ID : **{transanction['tx_id']}**
Date and time : {transanction['tx_datetime']}
Note : {transanction['note']}

**Contents**:
    Money : ${transanction['money']}
    Coal : {transanction['coal']}
    Oil : {transanction['oil']}
    Iron : {transanction['iron']}
    Bauxite : {transanction['bauxite']}
    Lead : {transanction['lead']}
    Gasoline : {transanction['gasoline']}
    Munitions : {transanction['munitions']}
    Steel : {transanction['steel']}
    Aluminum : {transanction['aluminum']}
    Food : {transanction['food']}
            ''')
            await ctx.send(f'{role.mention}')
            await ctx.send(embed=embed)


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



@tasks.loop(minutes=5)
async def transaction_scanner():
    members = db.accounts.find({})
    for x in members:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id={x["_id"]}&min_tx_id={x["last_transaction_id"]}') as r:
                transactions = r.json()
                query = transactions['api_request']
                if query['success']:
                    for transaction in transactions['data']:
                        transaction['processed'] = False
                        db.transactions.insert_one(transaction)
                        if transaction['sender_id'] == 913:
                            header_message = f'{x['nation_name']} made a withdrawal from Arrgh bank.'
                            dcolor = 15158332
                        elif transaction['receiver_id'] == 913:
                            header_message = f'{x['nation_name']} made a deposit into Arrgh bank.'
                            dcolor = 3066993
                        else:
                            dcolor = discord.Color.default()
                        embed = discord.Embed(title=header_message, description=f'''
Transanction ID : **{transanction['tx_id']}**
Date and time : {transanction['tx_datetime']}
Note : {transanction['note']}

**Contents**:
    Money : ${transanction['money']}
    Coal : {transanction['coal']}
    Oil : {transanction['oil']}
    Iron : {transanction['iron']}
    Bauxite : {transanction['bauxite']}
    Lead : {transanction['lead']}
    Gasoline : {transanction['gasoline']}
    Munitions : {transanction['munitions']}
    Steel : {transanction['steel']}
    Aluminum : {transanction['aluminum']}
    Food : {transanction['food']}''', color=dcolor)
                        await ctx.send


            







client.run(token)