# -*- coding: UTF-8 -*-

from datetime import datetime
from datetime import timedelta

def getTime(days = 365):
    """get the start and end time

    Returns:
        start: the start time
        end: the time right now
    """
    end = datetime.now()
    start = datetime.now() - timedelta(days = days)
    return start, end
