# -*- coding: utf-8 -*-

import configparser, json, urllib.request, urllib.parse, sys

config_file = "config.ini"
cursorfile = "cursor.txt"
send = True

class words(object):

    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.config.read(config_file)
        with open(cursorfile,'r') as crs:
            self.cfg_cursor = int(crs.read())
        crs.close()
        self.cfg_wordlist = self.config.get('settings','wordlist')
        self.cfg_words = self.config.getint('settings','words')

    def get(self):
        # Get X new words for today.
        with open(self.cfg_wordlist) as f:
            words = f.read().splitlines()
        self.words = words[self.cfg_cursor:self.cfg_cursor+self.cfg_words]
        return self.words

    def cursorWrite(self):
        with open(cursorfile,'w') as crs:
            crs.write(str(self.cfg_cursor+self.cfg_words))
        crs.close()

class dct(object):

    def __init__(self):
        config = configparser.RawConfigParser()
        config.read(config_file)
        self.cfg_url = config.get('dictionary','url')
        self.cfg_key = config.get('dictionary','key')
        self.cfg_lang = config.get('dictionary','lang')

    def get(self, f):
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

class mailer(object):

    def __init__(self):
        config = configparser.RawConfigParser()
        config.read(config_file)
        self.cfg_from = config.get('email','from')
        self.cfg_to = config.get('email','to')
        self.cfg_subject = config.get('email','subject')

    def send(self, body):

        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        email_text = MIMEText(body, "html", "utf-8")

        msg = MIMEMultipart()
        msg['Subject'] = self.cfg_subject
        msg['To'] = self.cfg_to
        msg['From'] = self.cfg_from
        msg.attach(email_text)
        try:
            server = smtplib.SMTP('localhost')
            server.ehlo()
            server.sendmail(email_from, email_to, msg.as_string())
            server.quit()
            
        except:
            e = sys.exc_info()
            print("Errorino")
            print(e)




x = words() # Initiate config file
words = x.get() # Fetch current word list
dct = dct() # Initiate dictionary connection
body = [] # create empty list for body
for word in words: # Get definitions for each word and add HTML
    a = ""
    definition = dct.get(word)

    for f in definition:
        for t in f['tr']:
            a += "<br><b>%s</b> - <i>%s</i><br>" % (t['text'],t['pos'])
            try:
                if len(t['ex'])>0:
                    a += "<h5>EXAMPLES:</h5><ul>"
                for ex in t['ex']:
                    a += "<li><b>%s</b>:  <i>%s</i></li>" % (ex['text'],ex['tr'][0]['text'])
                a += "</ul>"
            except:
                continue
    
    # Add this formatted word & def to body
    line = "<h2>%s</h2><br>%s<hr>" % (word,"".join(a))
    body.append(line)

# Join all words and defs into mail body
body = "".join(body)
body += "<br><br><a href=\"https://tech.yandex.com/dictionary/\">Powered by Yandex.Dictionary</a>"


if send: # Send if not debug
    mail = mailer()
    mail.send(body)
else:
    print(body)

x.cursorWrite() # Update cursor file


"""

Languages available:
["be-be","be-ru","bg-ru","cs-en","cs-ru","da-en","da-ru","de-en","de-ru","de-tr","el-en","el-ru","en-cs","en-da","en-de","en-el","en-en","en-es","en-et","en-fi","en-fr","en-it","en-lt","en-lv","en-nl","en-no","en-pt","en-ru","en-sk","en-sv","en-tr","en-uk","es-en","es-es","es-ru","et-en","et-ru","fi-en","fi-ru","fr-en","fr-ru","it-en","it-ru","lt-en","lt-ru","lv-en","lv-ru","nl-en","nl-ru","no-en","no-ru","pl-ru","pt-en","pt-ru","ru-be","ru-bg","ru-cs","ru-da","ru-de","ru-el","ru-en","ru-es","ru-et","ru-fi","ru-fr","ru-it","ru-lt","ru-lv","ru-nl","ru-no","ru-pl","ru-pt","ru-ru","ru-sk","ru-sv","ru-tr","ru-tt","ru-uk","sk-en","sk-ru","sv-en","sv-ru","tr-de","tr-en","tr-ru","tt-ru","uk-en","uk-ru","uk-uk"]

"""
