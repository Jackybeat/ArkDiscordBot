# -*- coding: utf-8 -*-
'''
Created on 6 mars 2017

@author: Jacky
'''
import logging

from django.conf import settings

# from ArkDiscordBot.apps import bot


logger = logging.getLogger('BOT.{}'.format(__name__))

ARK_CHAT_CHANNEL = getattr(settings, 'ARK_CHAT_CHANNEL')
ARK_CHAT_REFRESH = int(getattr(settings, 'ARK_CHAT_REFRESH'))
        
async def receive_chat():
    # TODO It doesn't work with rcon ...
    pass


#asyncio.ensure_future(receive_chat())