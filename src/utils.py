# -*- coding: UTF-8 -*-

import datetime
import random

def randomColor():
    colors1 = '0123456789ABCDEF'
    num = "#"
    for i in range(6):
        num += random.choice(colors1)
    return num

def getTime(days = 365):
    """get the start and end time

    Returns:
        start: the start time
        end: the time right now
    """
    end = datetime.datetime.now()
    start = datetime.datetime.now() - datetime.timedelta(days = days)
    return start, end

def getTimeThisYear(year = 0):
    """get the start and end time this year

    Returns:
        start: the start time
        end: the time right now
    """
    if year == 0:
        now = datetime.datetime.now()
        year = now.year
        
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    return start, end

    

def getDatetime(timestamp):
    """get class datatime from str

    Args:
       timestamp: string time from email's header

    Returns:
        timestamp 
    """
    utclist = timestamp.split(' ')
    utcstr = ''
    for i in range(0, 5):
        utcstr = utcstr + utclist[i] + ' '

    utcdatetime = datetime.datetime.strptime(utcstr, '%a, %d %b %Y %H:%M:%S ')
    return utcdatetime

def getSuffix(email):
    if '@' in email:
        return email.split('@')
    else:
        return email, 'empty'
