# -*- coding: utf-8 -*-
'''
Created on 5 mars 2017

@author: Jacky
'''
import logging

from discord.ext import commands

from ArkDiscordBot.apps import bot
from ArkDiscordBot.discord import utils


logger = logging.getLogger('BOT.{}'.format(__name__))

class Channel:
    
    @commands.group()
    async def messages(self):
        '''
        Commands on channel messages. (see !help messages)
        '''
        pass
    
    @messages.command(pass_context=True, brief='Delete the last message of the bot.')
    async def delete_last(self, ctx):
        '''
        Delete the last message of the bot from the current channel.
        '''
        bot, message, channel, author = utils.parse_context(ctx)
        
        logger.info('{} deleting the last bot messages from channel {}.'.format(author, channel))
        await bot.delete_last_messages(channel, bot.name)
            
    
    @messages.command(pass_context=True, no_pm=True, brief='Delete all messages from the current channel.')
    async def clean(self, ctx):
        '''
        Delete the last 10000 messages from the current channel. 
        To confirm the deletion, react to the bot messages with thumbs up (👍) or thumbs down (👎) emoji.
        '''    
        bot, message, channel, author = utils.parse_context(ctx)
        
        if not await bot.ask_confirmation(channel,
                                            '**Are you sure you want to delete all messages from this channel ?**', 
                                            canceled_text='Deletion aborted.', 
                                            accepted_text='Deleting messages ...'):
            logger.debug('{} abort the deletion of all the messages from channel {}.'.format(author, channel))
            return
        
        messages = []
        
        async for log in bot.logs_from(channel, limit=1000):
            messages.append(log)
        
        length = len(messages)
        logger.info('{} deleting the {} last messages from channel {}.'.format(author, length, channel))
        await bot.delete_messages(messages)
        
        
    @messages.command(pass_context=True, brief='Delete all bot messages from the current channel.')
    async def clean_bot(self, ctx):
        '''
        Delete the last 10000 bot messages from the current channel. 
        To confirm the deletion, react to the bot messages with thumbs up (👍) or thumbs down (👎) emoji.
        '''  
        bot, message, channel, author = utils.parse_context(ctx)
        
        # Confirmation
        if not await bot.ask_confirmation(channel,
                                            '**Are you sure you want to delete all bot messages from this channel ?**', 
                                            canceled_text='Deletion aborted.', 
                                            accepted_text='Deleting messages ...'):
            logger.debug('{} abort the deletion of all bot messages from channel {}.'.format(author, channel))
            return
        
        messages = []
        
        async for log in bot.logs_from(channel, limit=1000):
            if str(log.author) == bot.name:
                messages.append(log)
        
        length = len(messages)
        logger.info('{} deleting the {} last bot messages from channel {}.'.format(author, length, channel))
        await bot.delete_messages(messages)
        
    
    @messages.command(pass_context=True, no_pm=True, brief='Delete all your messages from the current channel.')
    async def clean_user(self, ctx):
        '''
        Delete the last 10000 messages of the current user from the current channel. 
        To confirm the deletion, react to the bot messages with thumbs up (👍) or thumbs down (👎) emoji.
        '''  
        bot, message, channel, author = utils.parse_context(ctx)
        
        # Confirmation
        if not await bot.ask_confirmation(channel,
                                            '**Are you sure you want to delete all your messages from this channel ?**', 
                                            canceled_text='Deletion aborted.', 
                                            accepted_text='Deleting messages ...'):
            logger.info('{} abort the deletion of his messages from channel {}.'.format(author, channel))
            return
        
        # Deletion
        messages = []  
        
        async for log in bot.logs_from(channel, limit=1000):
            if log.author == author:
                messages.append(log)
        
        length = len(messages)
        logger.info('{} deleting his {} last messages from channel {}.'.format(author, length, channel))
        await bot.delete_messages(messages)
    
    @messages.command(pass_context=True, brief='Count your messages posted on the current channel.')
    async def count(self, ctx):
        """
        Count the number of messages posted by the current user on the current channel.
        
        """
        bot, message, channel, author = utils.parse_context(ctx)
        counter = 0
        
        tmp = await bot.send_message(channel, 'Calculating messages...')
        
        async for log in bot.logs_from(channel, limit=1000):
            if log.author == author:
                counter += 1
        
        response = '{}, You have posted {} messages on this channel.'.format(author, counter)
        logger.debug(response)
        await bot.edit_message(tmp, response)
        
    @messages.command(pass_context=True, brief='Count bot messages posted on the current channel.')
    async def count_bot(self, ctx):
        """
        Count the number of messages posted by the bot on the current channel.
        
        """
        bot, message, channel, author = utils.parse_context(ctx)
        counter = 0
        
        tmp = await bot.send_message(channel, 'Calculating messages...')
        
        async for log in bot.logs_from(channel, limit=1000):
            if str(log.author) == bot.name:
                counter += 1
        
        response = 'Bot {} have posted {} messages on this channel.'.format(author, counter)
        logger.debug(response)
        await bot.edit_message(tmp, response)

bot.add_cog(Channel())