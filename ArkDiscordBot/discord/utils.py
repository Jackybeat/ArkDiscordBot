# -*- coding: utf-8 -*-
'''
Created on 5 mars 2017

@author: Jacky
'''

def parse_context(ctx):
    '''
    Return bot, messages, channel and author from the context.
    '''
    return ctx.bot, ctx.message, ctx.message.channel, ctx.message.author