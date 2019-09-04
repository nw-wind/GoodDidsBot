#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import logging
import random
import datetime

import google_sheets_api
import botConfig

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    ssID=open(botConfig.ssIdFileName).read()
except IOError:
    ssID=''
    open(botConfig.ssIdFileName,'w').write(ssID)


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

def doAddToGoogleDocs(text):
    google_sheets_api.add_line(ssID, botConfig.ssTitle, [1,datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"),text])

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
    doAddToGoogleDocs(message.text)
    bot.reply_to(message,random.choice(congratsText['text']))

if __name__ == '__main__':
    #    try:
    sheets = google_sheets_api.get_sheets(ssID)
    for sheet in sheets:  # находим точное название листа
        sh = sheet.get("properties", {}).get("title", "")
        if sh == botConfig.ssTitle:
            break
    else:
        # если ее нет то создаем
        google_sheets_api.create_sheet(ssID, botConfig.ssTitle)
        google_sheets_api.add_line(ssID, botConfig.ssTitle, [["Num", "Date", "Dids"]])

        time.sleep(2)
    #    except Exception as e:
    #        print("Error occured. {}".format(str(e)))
    bot.polling()