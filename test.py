from bs4 import BeautifulSoup
import requests
import re
import aiohttp
import asyncio
import discord
import pymongo
from discord.ext import commands, tasks
from pymongo import MongoClient
from datetime import datetime

db_client = MongoClient('mongodb+srv://bot:bot123@discord.yal7c.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = db_client.get_database('the_accountant_db')
api_key = 'fe9ac05fb01f89'






#raw_list = [[sub['nation'], sub['leader']] for sub in nations_v2]

amount = '$5,630,577.00'

stripped = re.sub('\$|\,', '', amount)

print(stripped)