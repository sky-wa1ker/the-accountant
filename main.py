from pydoc import cli
import re
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

intents = discord.Intents.all()

client = discord.Bot(command_prefix=commands.when_mentioned_or('~'), intents = intents)

@client.event
async def on_ready():
    game = discord.Game("lewd games with ur mom.")
    await client.change_presence(status=discord.Status.online, activity=game)
    print('Online as {0.user}'.format(client))



@client.slash_command()
async def hello(ctx):
    await ctx.respond("Hello!", ephemeral=True)





client.run(token)