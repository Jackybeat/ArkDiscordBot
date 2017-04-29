# -*- coding: utf-8 -*-
'''
Created on 3 mars 2017

@author: Jacky
'''

import logging
from time import sleep

from django.apps import AppConfig   

from ArkDiscordBot.discord.bot_base import DiscordBot
from ark_supervisor.rcon.connection import Rcon


logger = logging.getLogger('BOT.{}'.format(__name__))

ark_connection = Rcon()
bot = DiscordBot(pm_help=True)

# Add all commands
from ArkDiscordBot.bot_commands import *

# Add all tasks
from ArkDiscordBot.tasks import *


class MyAppConfig(AppConfig):
    name = 'ArkDiscordBot'
    verbose_name = "ArkDiscordBot"
    
    def ready(self):
        while True:
                try:
                    bot.run()
                except Exception as e:
                    logger.exception('Discord bot error !')
                    bot.logout()
                    bot.http.recreate()
                    sleep(3)
    