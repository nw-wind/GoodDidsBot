#!/usr/bin/python

import telebot
from telebot import apihelper
import logging

token=''

apihelper.proxy = {'https':'socks5://userproxy:password@proxy_address:port'}
bot=telebot.TeleBot(token)

@bot.message_handler(commands=['start','help'])
def reply_help(message):
    bot.reply_to(message,"Это подсказка")

@bot.message_handler(func=lambda message: True)
def reply_echo(message):
    bot.reply_to(message,"Ты сказал %s" % message.text)

bot.polling()