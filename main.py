from bs4 import BeautifulSoup
import requests
import aiohttp
import asyncio
import discord
from discord.ext import commands, tasks


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
    role = discord.utils.get(ctx.guild.roles, name="Helm")
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://politicsandwar.com/api/v2/nation-bank-recs/{api_key}/&nation_id=176311&s_only&min_tx_id=62723954') as r:
            json_obj = await r.json()
            transanction = json_obj["data"][0]
            embed = discord.Embed(title=f'{role.mention} Markovia made a deposit into Arrgh bank.', description=f'''
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
            await ctx.send(embed=embed)









client.run(token)