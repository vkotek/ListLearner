# -*- coding: utf-8 -*-

import configparser, urllib, json
import urllib.request, urllib.parse
import sys, pprint
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config_file = "config.ini"

class wordmailer(object):

    def __init__(self):
        config = configparser.RawConfigParser()
        config.read(config_file)
        self.cfg_wordlist = config.get('settings','wordlist')
        self.cfg_cursor = config.getint('settings','cursor')
        self.cfg_words = config.getint('settings','words')
        self.cfg_email = config.get('settings','email')

    def getWords(self):
        with open(self.cfg_wordlist) as f:
            words = f.read().splitlines()
        self.words = words[self.cfg_cursor:self.cfg_cursor+self.cfg_words]
        return self.words
    
    def preMail(self,word,definition):
        text = word+"\n"+pprint.pformat(definition)
        return text
    
    def mailer(self, text):
        server = 'kotek.co'
        to = [self.cfg_email]
        fm = 'admin@kotek.co'
        msg = text
        
        session = smtplib.SMTP(server)
        session.sendmail(fm,to,msg)
        


class dictionary(object):

    def __init__(self):
        config = configparser.RawConfigParser()
        config.read(config_file)
        self.cfg_url = config.get('dictionary','url')
        self.cfg_key = config.get('dictionary','key')
        self.cfg_lang = config.get('dictionary','lang')

    def getDef(self, f):
        lang = "ru-en"
        url = self.cfg_url.format(self.cfg_key, lang, f)
        url = urllib.parse.quote(url, safe=':/?&=')
        
        try:
            with urllib.request.urlopen(url) as data:
                data = json.loads(data.read().decode('utf8'))
                data = data['def']
            return data     
        except:
            e = sys.exc_info()
            error = "Error getting definition. Sorry.\n\n%s\n\n%s" % (url,e)


# Initiate config file
a = wordmailer()
# Fetch current word list
words = a.getWords()
# Initiate dictionary connection
dct = dictionary()

body = []
for word in words:
    body.append(a.preMail(word,dct.getDef(word)))


email_from = "admin@kotek.co"
email_to = "kotek.vojtech@gmail.com" # MUST BE A LIST
email_subject = "Words for today"
email_text = MIMEText("\n".join(words), "plain", "utf-8")

msg = MIMEMultipart()
msg['Subject'] = email_subject
msg['To'] = email_to
msg['From'] = email_from
msg.preamble = """
%s
""" % email_text

try:
    server = smtplib.SMTP('localhost')
    server.ehlo()
    server.sendmail(email_from, email_to, msg.as_string())
    server.quit()
    
except:
    e = sys.exc_info()
    print("Errorino")
    print(e)


"""
Powered by Yandex.Dictionary
https://tech.yandex.com/dictionary/

Languages available:
["be-be","be-ru","bg-ru","cs-en","cs-ru","da-en","da-ru","de-en","de-ru","de-tr","el-en","el-ru","en-cs","en-da","en-de","en-el","en-en","en-es","en-et","en-fi","en-fr","en-it","en-lt","en-lv","en-nl","en-no","en-pt","en-ru","en-sk","en-sv","en-tr","en-uk","es-en","es-es","es-ru","et-en","et-ru","fi-en","fi-ru","fr-en","fr-ru","it-en","it-ru","lt-en","lt-ru","lv-en","lv-ru","nl-en","nl-ru","no-en","no-ru","pl-ru","pt-en","pt-ru","ru-be","ru-bg","ru-cs","ru-da","ru-de","ru-el","ru-en","ru-es","ru-et","ru-fi","ru-fr","ru-it","ru-lt","ru-lv","ru-nl","ru-no","ru-pl","ru-pt","ru-ru","ru-sk","ru-sv","ru-tr","ru-tt","ru-uk","sk-en","sk-ru","sv-en","sv-ru","tr-de","tr-en","tr-ru","tt-ru","uk-en","uk-ru","uk-uk"]

"""
