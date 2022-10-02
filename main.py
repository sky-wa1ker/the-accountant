import os
import aiohttp
import asyncio
import discord
import pymongo
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

        

client.run(token)