# Copyright 2008-2010 by Carnegie Mellon University

# @OPENSOURCE_HEADER_START@
# Use of the Network Situational Awareness Python support library and
# related source code is subject to the terms of the following licenses:
# 
# GNU Public License (GPL) Rights pursuant to Version 2, June 1991
# Government Purpose License Rights (GPLR) pursuant to DFARS 252.225-7013
# 
# NO WARRANTY
# 
# ANY INFORMATION, MATERIALS, SERVICES, INTELLECTUAL PROPERTY OR OTHER 
# PROPERTY OR RIGHTS GRANTED OR PROVIDED BY CARNEGIE MELLON UNIVERSITY 
# PURSUANT TO THIS LICENSE (HEREINAFTER THE "DELIVERABLES") ARE ON AN 
# "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY 
# KIND, EITHER EXPRESS OR IMPLIED AS TO ANY MATTER INCLUDING, BUT NOT 
# LIMITED TO, WARRANTY OF FITNESS FOR A PARTICULAR PURPOSE, 
# MERCHANTABILITY, INFORMATIONAL CONTENT, NONINFRINGEMENT, OR ERROR-FREE 
# OPERATION. CARNEGIE MELLON UNIVERSITY SHALL NOT BE LIABLE FOR INDIRECT, 
# SPECIAL OR CONSEQUENTIAL DAMAGES, SUCH AS LOSS OF PROFITS OR INABILITY 
# TO USE SAID INTELLECTUAL PROPERTY, UNDER THIS LICENSE, REGARDLESS OF 
# WHETHER SUCH PARTY WAS AWARE OF THE POSSIBILITY OF SUCH DAMAGES. 
# LICENSEE AGREES THAT IT WILL NOT MAKE ANY WARRANTY ON BEHALF OF 
# CARNEGIE MELLON UNIVERSITY, EXPRESS OR IMPLIED, TO ANY PERSON 
# CONCERNING THE APPLICATION OF OR THE RESULTS TO BE OBTAINED WITH THE 
# DELIVERABLES UNDER THIS LICENSE.
# 
# Licensee hereby agrees to defend, indemnify, and hold harmless Carnegie 
# Mellon University, its trustees, officers, employees, and agents from 
# all claims or demands made against them (and any related losses, 
# expenses, or attorney's fees) arising out of, or relating to Licensee's 
# and/or its sub licensees' negligent use or willful misuse of or 
# negligent conduct or willful misconduct regarding the Software, 
# facilities, or other rights or assistance granted by Carnegie Mellon 
# University under this License, including, but not limited to, any 
# claims of product liability, personal injury, death, damage to 
# property, or violation of any laws or regulations.
# 
# Carnegie Mellon University Software Engineering Institute authored 
# documents are sponsored by the U.S. Department of Defense under 
# Contract F19628-00-C-0003. Carnegie Mellon University retains 
# copyrights in all material produced under this contract. The U.S. 
# Government retains a non-exclusive, royalty-free license to publish or 
# reproduce these documents, or allow others to do so, for U.S. 
# Government purposes only pursuant to the copyright license under the 
# contract clause at 252.227.7013.
# @OPENSOURCE_HEADER_END@

"""
A set of functions to produce ranges of aesthetically-pleasing numbers
that have the specified length and include the specified range.
Functions are provided for producing nice numeric and time-based
ranges.
"""

from __future__ import division
from datetime import date, datetime, timedelta
import time
import copy
import math



#
# Regular number stuff (code mutated from original work by John
# Prevost)
#



nice_intervals = [1.0, 2.0, 2.5, 3.0, 5.0, 10.0]

def nice_ceil(x):
    if x == 0:
        return 0
    if x < 0:
        return nice_floor(x * -1) * -1
    z = 10.0 ** math.floor(math.log10(x))
    for i in xrange(len(nice_intervals) - 1):
        result = nice_intervals[i] * z
        if x <= result: return result
    return nice_intervals[-1] * z

def nice_floor(x):
    if x == 0:
        return 0
    if x < 0:
        return nice_ceil(x * -1) * -1
    z = 10.0 ** (math.ceil(math.log10(x)) - 1.0)
    r = x / z
    for i in xrange(len(nice_intervals)-1, 1, -1):
        result = nice_intervals[i] * z
        if x >= result: return result
    return nice_intervals[0] * z
    
def nice_round(x):
    if x == 0:
        return 0
    z = 10.0 ** (math.ceil(math.log10(x)) - 1.0)
    r = x / z
    for i in xrange(len(nice_intervals) - 1):
        result = nice_intervals[i] * z
        cutoff = (result + nice_intervals[i+1] * z) / 2.0
        if x <= cutoff: return result
    return nice_intervals[-1] * z

def nice_ticks(lo, hi, ticks=5, inside=False):
    """
    Find 'nice' places to put *ticks* tick marks for numeric data
    spanning from *lo* to *hi*.  If *inside* is ``True``, then the
    nice range will be contained within the input range.  If *inside*
    is ``False``, then the nice range will contain the input range.
    To find nice numbers for time data, use :func:`nice_time_ticks`.

    The result is a tuple containing the minimum value of the nice
    range, the maximum value of the nice range, and an iterator over
    the tick marks.

    See also :func:`nice_ticks_seq`.
    """

    delta_x = hi - lo
    if delta_x == 0:
        if lo == 0:
            return nice_ticks(-1, 1, ticks, inside)
        else:
            return nice_ticks(nice_floor(lo), nice_ceil(hi),
                              ticks, inside)
    nice_delta_x = nice_ceil(delta_x)
    delta_t = nice_round(delta_x / (ticks - 1))
    if inside:
        lo_t = math.ceil(lo / delta_t) * delta_t
        hi_t = math.floor(hi / delta_t) * delta_t
    else:
        lo_t = math.floor(lo / delta_t) * delta_t
        hi_t = math.ceil(hi / delta_t) * delta_t

    def t_iter():
        t = lo_t
        while t <= hi_t:
            yield t
            t = t + delta_t
    return (lo_t, hi_t, t_iter())

def nice_ticks_seq(lo, hi, ticks=5, inside=False):
    """
    A convenience wrapper of :func:`nice_ticks` to return the nice
    range as a sequence.
    """
    return tuple(nice_ticks(lo, hi, ticks, inside)[2])


#
# Time stuff. This shares some ideas with the above (T_r is basically
# nice_intervals for a number of different units), but is implemented
# totally differently, according to the method suggested by Wilkinson
# in _The Grammar of Graphics_.
#



# Some unit definitions, for convenience later
SECOND = 1
MINUTE = 60 * SECOND
HOUR   = 60 * MINUTE
DAY    = 24 * HOUR
WEEK   = 7  * DAY



one_day = timedelta(seconds=3600 * 24)
def end_of_month(year, month):
    if month == 12:
        return 31
    else:
        eom = date(year, month+1, 1) - one_day
        return eom.day





def month_floor(dt, n):
    """Round datetime down to nearest date that falls evenly on an
    n-month boundary. (E.g., valid intervals for a 3-month
    boundary are 1/1, 4/1, 7/1, and 10/1)"""
    year = dt.replace(month=1, day=1, hour=0,
                      minute=0, second=0, microsecond=0)
    next = year
    curr = None
    if next == dt:
        return dt
    else:
        while next < dt:
            curr = next
            if next.month + n > 12:
                break
            next = next.replace(month=next.month + n)
        return curr


def month_ceil(dt, n):
    """Round datetime up to nearest date that falls evenly on an
    n-month boundary. (E.g., valid intervals for a 3-month
    boundary are 1/1, 4/1, 7/1, and 10/1)"""
    f = month_floor(dt, n)
    # TODO: verify that this boundary works
    if f.month + n - 1 > 12:
        # TODO: verify that this works
        new_year = f.year + 1
        new_month = (((f.month - 1) + n) % 12) + 1
        return f.replace(year=new_year, month=new_month)
    else:
        return f.replace(month=f.month + n - 1)



class RollingDatetime(object):
    def __init__(self, dt, orig_day=None):
        assert dt is not None
        self.dt = dt
        # Keep the original day of the month around for reference
        if orig_day is None:
            self.orig_day = self.dt.day
        else:
            self.orig_day = orig_day
        if self.orig_day == end_of_month(self.dt.year, self.dt.month):
            self.is_eom = True
        else:
            self.is_eom = False
    def add_months(self, n):
        """Increment current date by n months, with the following
        semantics:

          - If the original day was the last day of the month, set the
            new day to the last day of the new month.
             
          - If the current day of the month is later than the last day
            of the new month, set it to the last day of the new month.

          - Otherwise, use the same day of the month."""
        allmonths = self.dt.month + n
        if allmonths > 12:
            new_year = self.dt.year + (allmonths // 12)
            new_month = allmonths % 12
        else:
            new_year = self.dt.year
            new_month = allmonths
        new_eom = end_of_month(new_year, new_month)
        if self.is_eom:
            new_day = new_eom
        else:
            if new_eom < self.orig_day:
                new_day = new_eom
            else:
                new_day = self.orig_day
        self.dt = self.dt.replace(
            year=new_year, month=new_month, day=new_day)
        return self
    def datetime(self):
        return copy.copy(self.dt)
    def __add__(self, n): raise NotImplemented("__add__")
    def __sub__(self, n): raise NotImplemented("__sub__")
    def floor(self, n): raise NotImplemented("floor")
    def ceil(self, n): raise NotImplemented("ceil")



class Months(RollingDatetime):
    def __add__(self, n):
        return self.add_months(n)
    def __sub__(self, n):
        # TODO: find anything that relies on this (mis)definition and
        # shoot it.
        # return self.dt.month - n.dt.month
        self_months = (self.dt.year * 12) + self.dt.month
        n_months = (n.dt.year * 12) + n.dt.month
        return self_months - n_months
    def floor(self, n):
        return Months(month_floor(self.dt, n), orig_day=self.orig_day)
    def ceil(self, n):
        return Months(month_ceil(self.dt, n), orig_day=self.orig_day)

    

class Years(RollingDatetime):
    def __add__(self, n):
        self.dt = self.dt.replace(year = self.dt.year + n)
        return self
    def __sub__(self, n):
        return self.dt.year - n.dt.year
    def floor(self, n):
        return Years(month_floor(self.dt, n * 12), orig_day=self.orig_day)
    def ceil(self, n):
        return Years(month_ceil(self.dt, n * 12), orig_day=self.orig_day)

    
# A set of time scales, and the data required to deal with each
# one. Each tuple contains:
#
#   1. A list of "nice numbers," measured in seconds, for each
#      scale.
#   2. The unit of measure (normalized to seconds) to which to round
#      endpoints.
#
# This just does the "regular" time intervals. Months and years are
# handled separately.
T_r = [
    ([s for s in (1, 2, 5, 15, 30)], SECOND),
    ([m * MINUTE for m in (1, 2, 5, 15, 30)], MINUTE),
    ([h * HOUR  for h in (1, 2, 3, 4, 6, 12)], HOUR),
    ([DAY], DAY),
    ([WEEK], WEEK)
]


def granularity(k, m):
    #print "k, m: ", k, ",", m
    if 0 < k and k < 2 * m:
        return 1 - (abs(k - m)/m)
    else:
        return 0
def coverage(r_d, r_s) :
    if r_d/r_s >= .75:
        return r_d/r_s
    else:
        return 0



#
# "Calendar" time ticks 
#

def calendar_time_ticks(lo, hi, ticks=5, inside=False, as_datetime=True):
    """Nice numbers for times at 'calendar' intervals (months and
    years) that are sometimes irregular in terms of time passed.

    @type lo: datetime
    @param lo: low end of time scale
    
    @type hi: datetime
    @param hi: high end of time scale
    
    @type ticks: int
    @param ticks: desired number of tick marks
    
    @type inside: bool
    @param inside: Should the ticks lie inside the lo-hi range?"""
    def as_seconds(dt):
        return time.mktime(dt.timetuple())
    d_range = as_seconds(hi) - as_seconds(lo)

    def intv_time_ticks(lo, hi, intv):
        if inside:
            s_end = hi.floor(intv)
            s_start = lo.ceil(intv)
        else:
            s_end = hi.ceil(intv)
            s_start = lo.floor(intv)
        #print "start: %s" % s_start.dt
        #print "end  : %s" % s_end.dt
        s_range_units = s_end - s_start
        s_range_seconds = as_seconds(s_end.dt) - as_seconds(s_start.dt)
        #print "s_range_units:", s_range_units
        s_ticks = s_range_units / intv
        g = granularity(s_ticks, ticks)
        #print "g:            ", g
        c = coverage(d_range, s_range_seconds)
        weighted_ave = (g + c)/2
        #print "ave:          ", weighted_ave
        return (s_start, s_end, intv, weighted_ave)

    candidate = (0, 0, 0, 0)
    # Go through month intervals first
    month_lo, month_hi = [Months(x) for x in (lo, hi)]
    for months in (1, 2, 3, 4, 6):
        new_candidate = intv_time_ticks(month_lo, month_hi, months)
        weighted_ave = new_candidate[3]
        if weighted_ave > candidate[3]:
            candidate = new_candidate
    # Do years
    year_lo, year_hi = [Years(x) for x in (lo, hi)]
    for years in (1, 2, 3, 4, 5, 10, 25):
        new_candidate = intv_time_ticks(year_lo, year_hi, years)
        weighted_ave = new_candidate[3]
        if weighted_ave > candidate[3]:
            candidate = new_candidate
    start, stop, step, score = candidate
    # return the beginning and end of the range, and an iterator
    # through it
    def tts(dt):
        return time.mktime(dt.timetuple())
    def dt_iter():
        curr = start
        while curr.dt <= stop.dt:
            yield curr.dt
            curr += step
    if as_datetime:
        return start.dt, stop.dt, dt_iter()
    else:
        it = dt_iter()
        def as_seconds():
            for i in it:
                yield time.mktime(i.timetuple())
        return tts(start.dt), tts(stop.dt), as_seconds()
        
#
# "Regular" time ticks
#

def regular_time_ticks(lo, hi, ticks=5, inside=False, as_datetime=True):
    """Nice numbers for times at regular intervals---seconds, minutes,
    days, weeks.

    @type lo: float
    @param lo: low end of time scale, in seconds
    
    @type hi: float
    @param hi: high end of time scale, in seconds
    
    @type ticks: int
    @param ticks: desired number of tick marks
    
    @type inside: bool
    @param inside: Should the ticks lie inside the lo-hi range?"""
    # Convenience functions
    def interval_floor(intv, x): return (x // intv) * intv
    def interval_ceil(intv, x): return ((x // intv) * intv) + intv
    drange = hi - lo
    candidate = (0, 0, 0, 0)
    for Q, unit in T_r:
        for q in Q:
            #print "====================================="
            #print "q:      ", q
            #print "unit:   ", unit
            #print "-------------------------------------"
            # range of the scale (r_s )
            if inside:
                s_start = interval_ceil(unit, lo)
                s_end = interval_floor(unit, hi)
            else:
                s_start = interval_floor(unit, lo)
                s_end = interval_ceil(unit, hi)
            s_range = s_end - s_start
            #print "s_range:", s_range
            s_ticks =  s_range / q
            g = granularity(s_ticks, ticks)
            #print "g:      ", g
            c = coverage(drange, s_range)
            #print "c:      ", c
            weighted_ave = (g + c)/2
            #print "ave:    ", weighted_ave
            if weighted_ave > candidate[3]:
                candidate = (s_start, s_end, q, weighted_ave)
    if candidate[0] is None:
        raise RuntimeError("Couldn't find usable time scale")
    start, stop, step, score = candidate
    # Some shorthand
    def fts(s):
        return datetime.fromtimestamp(s)
    if as_datetime:
        def dt_iter():
            for secs in xrange(int(start), int(stop), step):
                yield fts(secs)
        return fts(start), fts(stop), dt_iter()
    else:
        def as_seconds():
            for secs in xrange(int(start), int(stop), step):
                yield secs
        return start, stop, as_seconds()


# Renamed from get_time_ticks
def nice_time_ticks(lo, hi, ticks=5, inside=False, as_datetime=True):
    """
    Find 'nice' places to put *ticks* tick marks for time data
    spanning from *lo* to *hi*.  If *inside* is ``True``, then the
    nice range will be contained within the input range.  If *inside*
    is ``False``, then the nice range will contain the input range.
    To find nice numbers for numerical data, use :func:`nice_ticks`.

    The result is a tuple containing the minimum value of the nice
    range, the maximum value of the nice range, and an iterator over
    the ticks marks.  If *as_datetime* is ``True``, the result values
    will be :class:`datetime.datetime` objects.  Otherwise, the result
    values will be numbers of seconds since UNIX epoch.

    See also :func:`nice_time_ticks_seq`.
    """
    hi_secs = time.mktime(hi.timetuple())
    lo_secs = time.mktime(lo.timetuple())
    # Give it to months/years algorithm if it's that big
    if hi_secs - lo_secs >= 8 * WEEK:
        return calendar_time_ticks(lo, hi, ticks, inside, as_datetime)
    else:
        return regular_time_ticks(lo_secs, hi_secs, ticks, inside, as_datetime)

def nice_time_ticks_seq(lo, hi, ticks=5, inside=False, as_datetime=True):
    """
    A convenience wrapper of :func:`nice_time_ticks` to return the
    nice range as a sequence.
    """
    return tuple(nice_time_ticks(lo, hi, ticks, inside, as_datetime)[2])

__all__ = """
    nice_ticks
    nice_ticks_seq
    nice_time_ticks
    nice_time_ticks_seq
""".split()
