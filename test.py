from bs4 import BeautifulSoup
import requests
import aiohttp
import asyncio
import discord
import pymongo
from discord.ext import commands, tasks
from pymongo import MongoClient
from datetime import datetime

db_client = MongoClient('mongodb+srv://bot:bot123@discord.yal7c.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = db_client.get_database('the_accountant_db')




members = db.accounts.find({})

#raw_list = [[sub['nation'], sub['leader']] for sub in nations_v2]

for x in members:
    print(x)