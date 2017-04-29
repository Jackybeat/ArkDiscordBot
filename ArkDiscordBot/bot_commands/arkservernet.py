# -*- coding: utf-8 -*-
'''
Created on 6 mars 2017

@author: Jacky
'''
import logging

from discord.ext import commands
import requests

from ArkDiscordBot import settings
from ArkDiscordBot.apps import bot
from ArkDiscordBot.discord import utils


logger = logging.getLogger('BOT.{}'.format(__name__))

API_KEY = getattr(settings,'ARKSERVERNET_API_KEY')
USER_AGENT = getattr(settings,'USER_AGENT')

class ArkServerNet:
    
    headers = {
        'User-Agent': USER_AGENT, 
        }
    
    top_votes_url = 'https://ark-servers.net/api/?object=servers&element=voters&key={}&month=current&format=json'.format(API_KEY)
    all_votes_url = 'https://ark-servers.net/api/?object=servers&element=votes&key={}&format=json'.format(API_KEY)
    
    @commands.command(pass_context=True, brief='Get top votes from ark-server.net.')
    async def top_votes(self, ctx):
        '''
        Get the list of the top voters of the month from 'ark-servers.net'.
        '''
        
        bot, message, channel, author = utils.parse_context(ctx)
        
        tmp = await bot.send_message(channel, 'Retriving voters ...')
        
        try:            
            r = requests.get(self.top_votes_url, headers=self.headers)
            top_votes = r.json()
                
        except Exception as e:
            logger.exception('Unable to connect to Ark-servers.net!')
            await bot.edit_message(tmp, 'Unable to connect to Ark-servers.net!')
            return
        
        result = ''
        count = 0
        for vote in top_votes['voters']:
            result = '{}{}  {}\n'.format(result, vote['nickname'], vote['votes'])
            count += 1
            
        result = "__**Top voters of the month {} :**__\n```{}\n```".format(count, result)
        
        logger.debug('Get top voters from Ark-servers.net: \n{}'.format(result))
        await bot.edit_message(tmp, result)
    
    
    @commands.command(pass_context=True, brief='Get all dated votes from ark-server.net.')
    async def get_votes(self, ctx):        
        '''
        Get the list of all posted votes of month from 'ark-servers.net'.
        This command provide voter name, steamid and the date of the vote.
        '''
    
        bot, message, channel, author = utils.parse_context(ctx)
        
        tmp = await bot.send_message(channel, 'Retriving votes ...')
        
        try:            
            r = requests.get(self.all_votes_url, headers=self.headers)
            top_votes = r.json()                
        except Exception as e:
            logger.exception('Unable to connect to Ark-servers.net!')
            await bot.edit_message(tmp, 'Unable to connect to Ark-servers.net!')
            return
        
        result = "__**All votes :**__\n"
        
        for vote in top_votes['votes']:
            result = '{}{}: {}  {}\n'.format(result, vote['date'], vote['nickname'], vote['steamid'])
        
        logger.debug('Get all votes from Ark-servers.net: \n{}'.format(result))
        await bot.edit_message(tmp, result)


bot.add_cog(ArkServerNet())
