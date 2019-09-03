#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import logging
import botConfig

bot=telebot.TeleBot(botConfig.token)

@bot.message_handler(commands=['start','help'])
def reply_help(message):
    #        reply_to(message,"Это подсказка" + repr(message.from_user.__dir__()))
    #with message.from_user:
        bot.reply_to(message,"First '{}' Second '{}' User '{}' is-bot '{}' lang '{}'".format(message.from_user.first_name,message.from_user.last_name,message.from_user.username,message.from_user.is_bot,message.from_user.language_code))

@bot.message_handler(commands=['show'])
def reply_show(message):
    try:
        bot.reply_to(message,"{} = {}".format(message.text,eval( "repr({})".format( (message.text.split(' '))[1] ))))
    except Exception as e:
        bot.reply_to(message,"Error listing object: " + str(e))

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
def reply_echo(message):
    bot.reply_to(message,"Ты сказал: %s" % message.text)

bot.polling()