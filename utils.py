__author__ = 'ritesh'
"""
Nicked from : http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
"""
import time
import smtplib
from email.mime.text import MIMEText
from settings import EMAIL_ADDRESS, EMAIL_PW

def get_hits_left(r, api_name, api_url):
    """
    Returns number of hits left!
    """
    return r['resources'][api_name][api_url]['remaining']

def ratelimit(r, api_name, api_url):
    reset = r['resources'][api_name][api_url]['reset']
    remaining= r['resources'][api_name][api_url]['remaining']
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reset))
    return {'remaining': remaining, 'reset': t}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def send_email(to, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to
    session = smtplib.SMTP('smtp.gmail.com', '587')
    session.ehlo()
    session.starttls()
    session.login(EMAIL_ADDRESS, EMAIL_PW)
    session.sendmail(EMAIL_ADDRESS, to, msg.as_string())


