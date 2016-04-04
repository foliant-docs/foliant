# -*- coding: utf-8 -*

import smtplib
import json
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import encoders


def email_fields_from_config():
    """
    gets email login,pass, destination address and subject(title) from config
    all params are strings
    """
    c = open('config.json')
    config = json.load(c)
    c.close()
    email_dest = config['email_destination']
    email_title = config['title']
    k = open('keys.json')
    keys = json.load(k)
    k.close()
    email_login = keys['email_login']
    email_pass = keys['email_pass']
    return email_login, email_pass, email_dest, email_title


def send_email(login, passw, dest, title, fn):
	"""
	sends email with attachment
	"""
	msg = MIMEMultipart() 
	msg['From'] = login
	msg['To'] = dest
	msg['Subject'] = title	 
	body = "С уважением,\nОтдел технической документации"	 
	msg.attach(MIMEText(body, 'plain'))
	attachment = open(fn, "rb")
	part = MIMEBase('application', 'octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attachment; filename= %s" % fn)
	msg.attach(part)
	server = smtplib.SMTP_SSL('smtp.yandex.ru', port=465) 
	server.login(login, passw)
	text = msg.as_string()
	server.sendmail(login, dest, text)
	server.quit()


