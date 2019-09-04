#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import logging
import random
import botConfig

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def loadTextFile(textFileName):
    r=dict();
    try:
        r['status']='ok'
        r['text']=[line.rstrip('\n') for line in open(textFileName)]
    except Exception as e:
        r={'status':'error', 'text':str(e)}
    return r

def getHelp():
    return loadTextFile(botConfig.helpTextFile)

def getCongrats():
    return loadTextFile(botConfig.congratsTextFile)

bot=telebot.TeleBot(botConfig.token)

@bot.message_handler(commands=['start','help'])
def reply_help(message):
    helpText=getHelp()
    if helpText['status']=='error':
        logging.error("Cannot show help. {}".format(helpText['text']))
        return
    bot.reply_to(message,'\n'.join(helpText['text']).format(message.from_user.first_name, message.from_user.last_name, message.from_user.username))

@bot.message_handler(commands=['list'])
def reply_list(message):
    try:
        obj=(message.text.split(' '))[1]
        bot.reply_to(message,"List of '{}':".format(obj))
        for field in eval("{}.__dir__()".format(obj)):
            typ=eval("str(type({}.{}))".format(obj,field))
            val=eval("repr({}.{})".format(obj,field))
            msg="{}:{} {}\n".format(field,typ,val)
            #if not typ.find("'builtin_function_or_method'") and not typ.find("'method-wrapper'") and not field.startswith('_')
            if not field.startswith('_'):
                bot.reply_to(message,"list of {}:\n{}".format(obj,msg))
    except Exception as e:
        bot.reply_to(message,"Error listing object: " + str(e))

@bot.message_handler(func=lambda message: True)
def reply_dialog(message):
    congratsText=getCongrats()
    if congratsText['status']=='error':
        logging.error("Cannot show help. {}".format(congratsText['text']))
        return
    bot.reply_to(message,random.choice(congratsText['text']))

bot.polling()