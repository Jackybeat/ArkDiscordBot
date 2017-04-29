# -*- coding: utf-8 -*-
'''
Created on 2 mars 2017

@author: Jacky
'''

import logging

from discord.ext import commands
from django.conf import settings

from ArkDiscordBot.apps import bot, ark_connection


logger = logging.getLogger('BOT.{}'.format(__name__))
DEBUG = getattr(settings,'DEBUG')

class RCON:
    
    async def send_rcon(self, channel, command, formatter=lambda x: x): 
        
        tmp = await bot.send_message(channel, 'Sending command ...')
        
        try:        
            # Send Command and wait response
            response = formatter(ark_connection.rcon(command))
            
#             logger.debug(response)
            await bot.edit_message(tmp, response)
            
            return response
            
        except:
            logger.exception('Rcon connection error !')
            await bot.edit_message(tmp, 'Rcon connection error !')
            
    
    @commands.group(pass_context=True, brief='Send RCON command. (see !help ark_connection)')
    async def rcon(self, ctx):
        """
        Send RCON command. If the command is unknown, it will be sent as is, only if DEBUG=True.
        Use '!help ark_connection' to know implemented commands.
        """
        
        # If command is not defined in this group => send as is
        if not ctx.invoked_subcommand:
            if DEBUG:
                command = ctx.message.content.split(' ', 1)[1]
                logger.debug('Send unknown RCON command: {}'.format(command))
                await self.send_rcon(ctx.message.channel, command)
            else:
                logger.debug('Unknown RCON command: {}'.format(command))
    
    
    @rcon.command(pass_context=True, brief='List connected players.')
    async def listplayers(self, ctx):    
        """
        Get the list of connected player from RCON connection.
        """
        
        command = ctx.message.content.split(' ', 1)[1]
        
        def player_list_formatter(txt):
            '''
            Format the list of player for discord.
            '''
            result = ''
            count = 0
            
            for line in txt.splitlines(True):
                items = line.split(' ')
                count += 1
                if len(items) > 2:
                    result = '{} {} {}'.format(result, items[1], items[2])
                else:
                    result = '{}{}'.format(result, line)   
                                 
            return "__**Connected Players {} :**__```{}```".format(count, result)
                
        logger.debug('Send RCON command: {}'.format(command))
        await self.send_rcon(ctx.message.channel, command, player_list_formatter)
            
    
bot.add_cog(RCON())
