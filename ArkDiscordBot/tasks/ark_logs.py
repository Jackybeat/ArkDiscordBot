# -*- coding: utf-8 -*-
'''
Created on 6 mars 2017

@author: Jacky
'''

import asyncio
import logging

from django.conf import settings

from ArkDiscordBot.apps import bot, ark_connection


logger = logging.getLogger('BOT.{}'.format(__name__))

ARK_LOG_CHANNEL = getattr(settings, 'ARK_LOG_CHANNEL')
ARK_LOG_REFRESH = int(getattr(settings, 'ARK_LOG_REFRESH'))

        
def find_channels():
    '''
    Retrieve log channel on all servers.
        return: The list of log channels.
    '''
    channels = {}
    for server in bot.servers:        
        for channel in server.channels:
            if str(channel) == ARK_LOG_CHANNEL:
                channels[server] = channel
    return channels

    
async def receive_logs():
    
    # Waiting for bot alive
    while not bot or bot.is_alive: 
        await asyncio.sleep(5)  
    
    channels = find_channels()
    
    while True:
        
        # Waiting for bot alive
        while not bot or bot.is_alive: 
            await asyncio.sleep(5)        
        
        try:
            # Get ark logs through Rcon
            text = ark_connection.rcon('GetGameLog')
        except:
            logger.exception('Ark Logs Task RCON error !')
            continue
        
        # Check if response is available
        if not text.startswith('Server received, But no response!!'):
            # Send logs text to log channel on all servers
            for server, channel in channels.items():        
                await bot.append_last_message(server, channel, text)
        
        await asyncio.sleep(ARK_LOG_REFRESH)

# Register the receive_log loop to be executed.
asyncio.ensure_future(receive_logs())