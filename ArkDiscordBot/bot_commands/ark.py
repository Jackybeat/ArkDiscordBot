# -*- coding: utf-8 -*-
'''
Created on 2 mars 2017

@author: Jacky
'''

import logging

from discord.ext import commands

from ArkDiscordBot.apps import bot
from ArkDiscordBot.discord.utils import parse_context


logger = logging.getLogger('BOT.{}'.format(__name__))

class Commons:
    
    @commands.command(pass_context=True, name='test2', brief='Test the bot.')
    async def test(self, ctx):
        """
        Test command. Count the number of messages posted by the user on the current channel.
        
        """
        bot, channel, messages, author = parse_context(ctx)
        messages
        counter = 0
        
        tmp = await bot.send_message(channel, 'Calculating messages...')
        
        async for log in bot.logs_from(channel, limit=10000):
            if log.author == author:
                counter += 1
        
        messages = '{}, You have posted {} messages on this channel.'.format(author, counter)
        logger.debug(messages)
        await bot.edit_message(tmp, messages)


bot.add_cog(Commons())
