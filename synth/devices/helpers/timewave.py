"""TIMEWAVE
   Create periodic events over periods of human time"""
# To "and" use min(), to "or" use max()
#
# Copyright (c) 2017 DevicePilot Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime, random, ast
import numpy
from common import ISO8601
from common import utils

# TODO: Converting to pendulum would make this all much easier!

def toHours(spec):
    """spec is of the form '08:00-10:00' """
    return (int(spec[0:2])+int(spec[3:5])/60.0, int(spec[6:8])+int(spec[9:11])/60.0)

def hourInDay(t):
    """Returns hour in day (as a float, to nearest second, e.g. 07:30 is 7.5)"""
    dt = ISO8601.epoch_seconds_to_datetime(t)
    return int(dt.strftime("%H")) + int(dt.strftime("%M"))/60.0 + int(dt.strftime("%S"))/3600.0    

def dayOfWeek(t):
    """Returns e.g. 'Mon'"""
    dt = ISO8601.epoch_seconds_to_datetime(t)
    return dt.strftime("%a")

def startOfNextDay(t):
    """Given a time, returns time of next midnight."""
    s = ISO8601.epoch_seconds_to_ISO8601(t)    # e.g. "2007-10-23T23:32:10Z
    dt = ISO8601.epoch_seconds_to_datetime(t)
    dt += datetime.timedelta(days=1)
    s = dt.strftime("%Y-%m-%dT00:00:00")    # We've assumed timezone!
    return ISO8601.to_epoch_seconds(s)

def hourToHHMMSS(h):
    """Given a floating hour time, return a string in HH:MM:SS format (e.g. 14.5 becomes '14:30:00')"""
    assert h<24
    hours = int(h)
    minsF = (h-int(h))*60.0
    mins = int(minsF)
    secs = int((minsF-mins)*60.0)
    return "%02d:%02d:%02d" % (hours, mins, secs)

def hourWave(t,spec):
    (startHour, endHour) = toHours(spec)
    h = hourInDay(t)
    if (h >= startHour) and (h < endHour):
        return 1.0
    return 0.0

def dayWave(t,spec):
    """spec is a list e.g. ['Mon', 'Tue', 'Wed']"""
    if dayOfWeek(t) in spec:
        return 1.0
    return 0.0


def jitter(t, X, amountS):
    """Return a random number (intended as a time offset, i.e. jitter) within the range +/-amountS
       The jitter is different (but constant) for any given day in t (epoch secs)
       and for any value X (which might be e.g. deviceID)"""
    dt = ISO8601.epoch_seconds_to_datetime(t)
    dayOfYear = int(dt.strftime("%j"))
    year = int(dt.strftime("%Y"))
    uniqueValue = year*367+dayOfYear+abs(hash(X))   # Note that hash is implementation-dependent so may give different results on different platforms
    rand = utils.hashIt(uniqueValue,100)
    sign = int(str(uniqueValue)[0]) < 5
    v = (rand / 100.0) * amountS
    if sign:
        v = -v
    return v


def nextUsageTime(t, daySpec, hourSpec):
    """Given a daySpec e.g. ["Mon","Tue"] and an hourspec e.g. '08:00-10:00'
       work out a next time t which falls within that spec (picking randomly within the hour range)
       if given a time already within spec, move to the NEXT such time)"""
    (startHour, endHour) = toHours(hourSpec)
    (h,d) = (hourInDay(t), dayOfWeek(t))
    if (d in daySpec) and (h<endHour):  # If already in spec, move beyond
        t += 60*60*endHour-h
        
    while True: # Move to a valid day of the week
        (h,d) = (hourInDay(t), dayOfWeek(t))
        if (d in daySpec) and (h<endHour):
            break
        t = startOfNextDay(t)
    chosenHour = startHour + (endHour-startHour)*random.random()
    ts = ISO8601.epoch_seconds_to_ISO8601(t)
    ts = ts[:11]+hourToHHMMSS(chosenHour)+ts[19:]
    t = ISO8601.to_epoch_seconds(ts)
    return t

def interp(specStr, t):
    """Return the current value of t using linear interpolation.

       <specStr> is a string containing a list of pairs e.g. '[[0,20],[30,65],[60,50],[90,75]]'
       The first element of each pair is DAYS. The second is a NUMBER.
       <t> is time in seconds"""
    specList = ast.literal_eval(specStr)
    X = [i[0] for i in specList]
    Y = [i[1] for i in specList]
    day = t/(60*60*24.0)
    return numpy.interp(day,X,Y)

if __name__ == "__main__":
    specStr = "[[0,20],[30,65],[60,50],[90,75]]"
    for day in range(-10,100):
        print(day, interp(specStr, day*60*60*24))
    
##    specW = ["Mon","Tue","Wed","Thu","Fri"]
##    specD = "08:00-10:00"
##    t = 0
##    while True:
##        print ISO8601.epoch_seconds_to_datetime(t).strftime("%a %Y-%m-%dT%H:%M:%S")
##        t = nextUsageTime(t,specW,specD)
#    for t in range(100):
#        print jitter(t*60*60*24,0,100)

##    for t in range(0,60*60*24*7,3600):
##        print ISO8601.epoch_seconds_to_datetime(t).strftime("%a %d-%b-%Y at %H:%M:%S : "),
##        print min(
##                days(t,["Mon","Tue","Wed","Thu","Fri"]),
##                max(
##                    hours(t,"08:00-10:00"), hours(t,"16:00-18:00")
##                )
##              )

