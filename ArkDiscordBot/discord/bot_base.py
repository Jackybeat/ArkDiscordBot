# -*- coding: utf-8 -*-
'''
Created on 1 mars 2017

@author: Jacky
'''

import asyncio
import logging

from discord.ext.commands.bot import Bot
from django.conf import settings


logger = logging.getLogger('BOT.{}'.format(__name__))

# Get settings
DISCORD_TOKEN = getattr(settings,'DISCORD_TOKEN')
BOT_COMMAND_PREFIX = getattr(settings,'BOT_COMMAND_PREFIX')

@asyncio.coroutine
def test(ctx, *commands : str):
    """ Test if the bot is alive (useless). """
    bot = ctx.bot
    channel = ctx.message.channel
    author = ctx.message.author
    
    logger.debug('{} send Test command from channel {}.'.format(author, channel))
    yield from bot.send_message(channel, "Ok ok, I'm alive ;)")
    

class DiscordBot(Bot):
    """  
    Base Discord Bot.
    
    
    """
    
    command_prefix = "!"

    def __init__(self, command_prefix=BOT_COMMAND_PREFIX, **kwargs):
        super(DiscordBot, self).__init__(BOT_COMMAND_PREFIX, **kwargs)
        
        self.command_prefix = command_prefix
        self.name = ''
        
        self.test_attrs = kwargs.pop('test_attrs', {})
        self.test_attrs['pass_context'] = True

        if 'name' not in self.help_attrs:
            self.help_attrs['name'] = 'test'
            
        self.command(**self.test_attrs)(test)
    
    @asyncio.coroutine
    def start(self, *args, **kwargs):
        """ 
        Start the bot with the given token.            
        
        """
        if self.is_closed:
            self.http.recreate()
            self._closed.clear()
            
        return super(DiscordBot, self).start(DISCORD_TOKEN)
    
   
    def run(self, **kwargs):
        """ 
        Blocking method to run the bot.            
         
        """   
        try:
            self.loop.run_until_complete(self.start(**kwargs))
        except KeyboardInterrupt:
            #self.loop.run_until_complete(self.logout())
#             pending = asyncio.Task.all_tasks(loop=self.loop)
            #gathered = asyncio.gather(*pending, loop=self.loop)
            try:
                #gathered.cancel()
                #self.loop.run_until_complete(gathered)

                # we want to retrieve any exceptions to make sure that
                # they don't nag us about it being un-retrieved.
                #gathered.exception()
                pass
            except:
                pass
#         self.start()
#         self.wait_until_login()
#         self.wait_until_ready()
#         while self._is_logged_in:
#             sleep(5)
    
    @property
    def is_alive(self):
        return self.http.session.closed or self.is_closed or not self.is_logged_in
    
    @asyncio.coroutine
    def connect(self):
#         self.connection = ConnectionState(self.dispatch, self.request_offline_members,
#                                           self._syncer, self.connection.max_messages, loop=self.loop)

#         self.http = HTTPClient(None, loop=self.loop)
        
        yield from super(DiscordBot, self).connect()
        self._closed.clear()
    
    @asyncio.coroutine
    def on_ready(self):
        """ 
        Executed when bot is connected and ready.
            
        """        
        self.name = '{}#{}'.format(self.user.name, self.user.discriminator)  
        
        logger.info('Logged in as "{}" ({})'.format(self.name, self.user.id))        
        logger.debug('Installed commands are {}'.format(self.commands.keys()))         
    
    @asyncio.coroutine
    def send_message(self, channel, text):
        """
        Send messages to discord channel. The messages can be splitted to 
        many discord messages to respect the limit of 2000 characters.
        The splitting will only be applied on end line characters.
        
            channel: The channel of the serveur to post the messages.
            text: The text to post. 
            
            return: The last discord messages posted.
                
        """
        
        logger.debug('Write to channel "{}" : {}'.format(channel, text))
        
        output = ''
        last_message = False
        for line in text.splitlines(True):
            if len(output) + len(line) > 2000:
                last_message = yield from super(DiscordBot, self).send_message(channel, output)
                output = line
                continue
            else:
                output += line
        
        if output:
            last_message = yield from super(DiscordBot, self).send_message(channel, output)
            
        return last_message
    
    
    async def edit_message(self, message, new_content=None, *args, embed=None, append=False):
        '''
        Edit a message. The message can be splitted to 
        many discord messages to respect the limit of 2000 characters.
        The splitting will only be applied on end line characters.
        
            messages : The message to edit.
            new_content: The new content to replace the message with.
            embed: The new embed to replace the original embed with.
    
            return: The last edited or posted message.   
        '''
        
        logger.debug('Edit message on channel "{}" : {}'.format(message.channel, new_content))
        
        content = '{}\n'.format(message.content) if append else ''      
        last_message = False
        
        for line in new_content.splitlines(True):
            if len(content) + len(line) > 2000:
                if last_message:
                    last_message = await super(DiscordBot, self).send_message(message.channel, content)
                else:
                    last_message = await super(DiscordBot, self).edit_message(message, content, *args, embed=embed)
                    
                content = line
                continue
            else:
                content += line
        
        if content:
            if last_message:
                last_message = await super(DiscordBot, self).send_message(message.channel, content)
            else:
                last_message = await super(DiscordBot, self).edit_message(message, content, *args, embed=embed)
                
        return last_message


    async def ask_confirmation(self, channel, answer_text='**Are you sure ?**', 
                                     canceled_text='Action is canceled.', 
                                     accepted_text='Action is accepted.'):
        '''
        Ask confirmation to the user. The user should answer by sending a reaction 
        to the current messages and use use emoji 👍  or 👎 .
        '''
        
        answer_text = '{}\n*(Confirm by reacting to this messages by 👍  or 👎)*'.format(answer_text)
        
        msg = await self.send_message(channel, answer_text)    
        res = await self.wait_for_reaction(['👍', '👎'], message=msg)
        
        if res.reaction.emoji == '👍':
            await self.edit_message(msg, accepted_text)
            return msg
        else:
            await self.edit_message(msg, canceled_text)
            return False
    

    async def delete_messages(self, messages):
        '''
        Delete the given messages.
        This command can delete more than the limit of the discord API (100).
        
            bot: The bot.
            messages: The array of messages.
        '''    
        length = len(messages)
        
        if length == 1:
                await super(DiscordBot, self).delete_message(messages[0])
        elif length > 1:
            for sub in range(0, length, 100):
#                 recent_messages = []
#                 for msg in messages[sub:sub + 100]:
#                     if msg:
#                         pass
                await super(DiscordBot, self).delete_messages(messages[sub:sub + 100])
                
                
    async def get_last_message_from(self, channel, author, limit=10000):    
        '''
        Get the last messages posted by the given author on the given channel.
        
            return: The last posted messages.
        '''
        last_message = None
        
        async for log in self.logs_from(channel, limit):
        
            if str(log.author) == str(author) and \
                (not last_message or last_message.timestamp < log.timestamp):
                
                last_message = log
                break
        
        return last_message
    
    
    async def delete_last_messages(self, channel, author, n=1): 
        '''
        Delete the n last messages of the given author on the given channel.
        Keep in mind the messages will be deleted one by one.
        
            bot: The bot.
            channel: The channel where delete messages.
            n: The number of messages to delete.    
        '''
        for i in range(n):
            i
            msg_to_delete = await self.get_last_message_from(channel, author)
            
            if msg_to_delete:
                await self.delete_message(msg_to_delete)
                
                
    async def append_last_message(self, server, channel, text):
        '''
        Append text to the last message of the bot.
        If the last message of the channel is not from the bot or
        if the message length not fit on the discord limit, a new
        message will be created. 
        '''
        try:
            last_message = await self.get_last_message_from(channel, self.name, 1)
            if last_message:
                await self.edit_message(last_message, text, append=True)
            else:
                await self.send_message(channel, text)
        except:
            logger.exception('Unable to edit message !')

