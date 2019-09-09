#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import logging
import random
import time,sys,signal
import datetime
import mysql.connector

import botConfig

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
bot=telebot.TeleBot(botConfig.token)

def myLog(msg):
    cursor=myConn.cursor()
    cursor.execute("insert into log(dt,msg) values (now(), %s)",(msg,))
    myConn.commit()

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

def getPlanCongrats():
    return loadTextFile(botConfig.planCongratsFile)

def getTypeErrors():
    return loadTextFile(botConfig.typeErrorsFile)

def doDbRecord(m):
    try:
        logging.info("{}\t{}\t{} {}\t\"{}\"".format(m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name, m.text))
        cursor=myConn.cursor()
        cursor.execute(("insert into did(dt,cid,did) values (now(),%s,%s)"),(m.from_user.id,m.text))
        cursor.execute(("select * from user where id = %s"),(m.from_user.id,))
        if cursor.fetchone() is None:
            cursor.execute(("insert into user(id,username,first_name,last_name) values (%s,%s,%s,%s)"),(m.from_user.id,m.from_user.username,m.from_user.first_name,m.from_user.last_name))
        myConn.commit()
        myLog("User \"{}\" enter \"{}\"".format(m.from_user.username, m.text))
    except Exception as e:
        logging.error(str(e))

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
    if (message.text.split(' '))[0].lower() == 'покажи':
        cursor=myConn.cursor()
        #logging.info("select * from did where cid=%s",(message.from_user.id,))
        cursor.execute("select * from did where cid=%s order by dt desc limit 5",(message.from_user.id,))
        s='\n'.join([t[2] for t in cursor.fetchall()])
        bot.reply_to(message,s)
    elif (message.text.split(' '))[0].lower() == 'я':
        congratsText=getCongrats()
        if congratsText['status']=='error':
            logging.error("Cannot show help. {}".format(congratsText['text']))
            return
        doDbRecord(message)
        bot.reply_to(message,random.choice(congratsText['text']))
    elif (message.text.split(' '))[0].lower() == 'хочу':
        planCongratsText=getPlanCongrats()
        if planCongratsText['status']=='error':
            logging.error("Cannot show help. {}".format(planCongratsText['text']))
            return
        doDbRecord(message)
        bot.reply_to(message,random.choice(planCongratsText['text']))
    else:
        typeErrorsText=getTypeErrors()
        if typeErrorsText['status']=='error':
            logging.error("Cannot show help. {}".format(typeErrorsText['text']))
            return
        bot.reply_to(message,random.choice(typeErrorsText['text']))

def interuppt_handler(signum, frame):
    logging.info("Ctrl-C pressed.")
    sys.exit(-2) 

if __name__ == '__main__':
    signal.signal(signal.SIGINT, interuppt_handler)
    myConn=mysql.connector.connect(host=botConfig.myHost, database=botConfig.myDb, user=botConfig.myUser, password=botConfig.myPassword)
    myLog("Начало работы")
    while True:
        try:
            bot.polling()
        except Exception as e:
            logging.error("Execution error: {}".format(str(e)))
            time.sleep(2)
