#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
- fix arguments not to be hard coded
- solve a problem if there is no log file

Required:
- empty files with logs
"""
from __future__ import print_function

import argparse
import datetime
import os
import re
import time


os.environ['TZ'] = 'Europe/Warsaw'
time.tzset()
REGION = 'euro'
from datetime import date, timedelta


def get_parser():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--debug",
                        action="store_true", help="be verbose")
    parser.add_argument("-d", "--days",  type=int) # default=1,
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--log")
    parser.add_argument("--date", help="in format 2010-01-01")
    parser.add_argument("calendar", help="calendar you want to send your data to", default="Clocking Work")
    parser.add_argument("--dry", action="store_true")
    parser.add_argument("file", help="an OrgMode file")
    return parser


def prepare_date(str, retdata=False, double=False, verbose=False):
    """Format the date from 2018-06-18 Mon 13:00 to Monday, June 18, 2018 01:00 PM.
    """
    if verbose: print(); print(str)
    if verbose: print(str.split(' '))  # ['2018-07-03', 'Tue', '17:16']

    try:
        date, day, timex = str.split(' ')
    except:  # ValueError:  # ['2018-07-03', '17:16'] if there is no day name
        day = ''
        try:
            date, timex = str.split(' ')
        except:
            print(str)
            return  ### ?

    hour, min = [int(i) for i in timex.split(':')]
    year, month, day = [int(i) for i in date.split('-')]
    dt = datetime.datetime(year, month, day, hour, min, 0, 0)
    
    if REGION == 'euro':
        if double:
            if retdata:
                return dt, datetime.date(year, month, day)
            else:
                return dt.strftime("%A, %d %B, %Y %I:%M %p"), dt.strftime("%A, %B %d")  # return as a string
        else:
            if retdata:
                return dt
            else:
                return dt.strftime("%A, %d %B, %Y %I:%M %p")
    else:
        if double:
            if retdata:
                return dt, datetime.date(year, month, day)
            else:
                return dt.strftime("%A, %B %d, %Y %I:%M %p"), dt.strftime("%A, %B %d")  # return as a string
        else:
            if retdata:
                return dt
            else:
                return dt.strftime("%A, %B %d, %Y %I:%M %p")


def insert_event(calendar, project, task, start, end, dry):
    """Insert an event into calendar using Apple tell"""
    # you can use also activate, to move Calendar to the top
    cmd = """
    tell application \"Calendar\"
	tell calendar \"%s\"
        set theCurrentDate to (date "%s")
        set EndDate to (date "%s")
        make new event at end with properties {description:"%s", summary:"%s", start date:theCurrentDate, end date:EndDate}
	end tell
	reload calendars
    end tell""" % (calendar, start, end, '', task + ' (' + project + ')')
    #  summary:"[#A] Diet box <2018-09-28 Fri>(#health & #look :@health:)",
    # now the format is <task> (<project>)
    print(cmd)
    with open("/tmp/orgmode2calendar.scpt", 'w') as f:
        f.write(cmd)
    if not dry:
        os.system("osascript /tmp/orgmode2calendar.scpt")




# main
if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    f = open(args.file)
    items = []

    if args.log:
        logfn = args.log
    else:
        logfn = os.path.basename(args.file.replace('.org', '.log'))

    for l in f:
        if l.startswith('* '):
            curr_prj = re.sub(' +', ' ',l.replace('* ', '').strip())
            curr_task = ''  # be default it's empty if there is no curr_task
            # and the time is logged for * <project>
        if l.startswith('** '):
            curr_task = re.sub(' +', ' ',l.replace('** ', '').strip())
        if l.strip().startswith('CLOCK:'):
            # CLOCK: [2018-07-16 Mon 14:30]--[2018-07-16 Mon 16:00] =>  1:30
            if '--' not in l:
                continue
            start, end = l.replace('[', '').replace(']','').replace('CLOCK:', '').split('--')

            start = start.strip()
            end = end.strip()

            ###
            startdt, startdt_day = prepare_date(start, retdata=True, double=True)
            curr_task = curr_task.replace('DONE ', '').replace('TODO ', '').replace('INPROGRESS ', '')
            curr_prj = curr_prj.replace('DONE ', '').replace('TODO ', '').replace('INPROGRESS ', '')
            
            if args.debug: print('∆:', delta, 'cutoff:', cutoff, 'use it:', delta < cutoff)
            try:
                if args.debug: print(curr_prj)
            except NameError:
                if args.debug: print("Error in %s" % l)
            if args.verbose:
                print("%s %s %s %s" % (curr_prj, curr_task, prepare_date(start, verbose=args.verbose), prepare_date(end, verbose=args.verbose)))
                
            if args.date:
                # if given date
                d = [int(x) for x in args.date.split('-')]
                d = date(d[0], d[1], d[2])
                if startdt_day != d: # 2020-03-19 2020-03-19
                    #if args.verbose:
                    print('Skip this task, not the day')                    
                    continue

            # id days, then if old task then skip
            if args.days:
                cutoff = timedelta(days=args.days)
                delta = datetime.datetime.now() - startdt
                if not (delta < cutoff):
                    if args.verbose: print('Skip this task, too old!')
                    continue
            
            if '=>' in end:
                end, foo = end.split('=>')
                end = end.strip()

            try:
                log = open(logfn)
            except:
                logs = []
            else:
                logs = log.read()
                log.close()

            if "%s %s" % (prepare_date(start), prepare_date(end)) in logs:
                #if args.debug:
                print(" [-] already added %s %s" % (prepare_date(start), prepare_date(end)))
                pass
            else:
                print(" [x] added %s %s" % (prepare_date(start), prepare_date(end)))
                insert_event(args.calendar, curr_prj, curr_task, prepare_date(start), prepare_date(end), args.dry)
                if not args.dry:
                    log = open(logfn, 'a')
                    log.write("%s %s\n" % (prepare_date(start), prepare_date(end)))
                    log.close()

            if args.debug:
                break
