#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telebot
import logging
import botConfig

bot=telebot.TeleBot(botConfig.token)

@bot.message_handler(commands=['start','help'])
def reply_help(message):
    bot.reply_to(message,"Это подсказка")

@bot.message_handler(func=lambda message: True)
def reply_echo(message):
    bot.reply_to(message,"Ты сказал %s" % message.text)

bot.polling()