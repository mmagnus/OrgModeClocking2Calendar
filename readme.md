OrgModeClocking2Calendar
-------------------------------------------------------------------------------

![](example.png)

The script will perform one way synchronization of your clocking (time tracking) entries [1] from OrgMode Emacs.

The script scans all lines in your OrgMode file that start with 'CLOCK:' and converts these lines into events to be inserted into your calendar of choice.

The script uses Apple Scripts (`insert_event()`) to insert a given event into a calendar. This could be changed in the future to some other function based on other tools, such as: Gcalcli.

The script doesn't read your calendar to see what was already inserted. The script is using a simple log file. The syntax is as the following:

	Thursday, 29 July, 2021 15:30 Thursday, 29 July, 2021 16:30

which means that *some* event was added for this time slot. Consequently, you can edit this task, and it will not be re-inserted into your calendar. But, if you change clocking (start or end) for this task,  it will be inserted. Then you have to remove redundant events from your calendar manually. Not perfect, but this is how it is right now. That's why it is better to use `--days` with a short date (for example, `-d 7` to insert events from the last week) spans so you can check if there are no redundancies in your Calendar. This could be fixed at some point.

To play around, you can use `--dry` to see the output of the script but not inserting anything into your calendars.

    (py37) [mx] orgmode2calendar$ git:(master) ✗ ./OrgModeClocking2Calendar.py --help
    usage: OrgModeClocking2Calendar.py [-h] [--debug] [-d DAYS] [-v] [--log LOG]
                                       [--date DATE] [--dry] [--filter FILTER]
                                       calendar file

    - fix arguments not to be hard coded
    - solve a problem if there is no log file

    Required:
    - empty files with logs

    positional arguments:
      calendar              calendar you want to send your data to
      file                  an OrgMode file

    optional arguments:
      -h, --help            show this help message and exit
      --debug               be verbose
      -d DAYS, --days DAYS
      -v, --verbose
      --log LOG
      --date DATE           in format 2010-01-01
      --dry
      --filter FILTER       folder only for this phrase

Example:

    $ ./OrgModeTimeTracker2Calendar.py 'Clocking Life' ~/Dropbox/geekbook/notes/work-curr.org
    ∆: 17 days, 12:47:34.673081 cutoff: 1 day, 0:00:00 use it: False
    2019-04-26 Fri 10:34 =>  0:02
    Marcin Magnus, PhD https://mmagnus.io  Friday, April 26, 2019 10:32 AM None
    Skip this task, too old!
    ∆: 179 days, 11:24:34.673436 cutoff: 1 day, 0:00:00 use it: False
    2018-11-15 Thu 16:00 =>  4:05
    Marcin Magnus, PhD https://mmagnus.io Talk with science people Thursday, November 15, 2018 11:55 AM None
    Skip this task, too old!
    ∆: 314 days, 9:19:34.673474 cutoff: 1 day, 0:00:00 use it: False
    2018-07-03 Tue 14:37 =>  0:37
    Marcin Magnus, PhD https://mmagnus.io Talk with science people Tuesday, July 03, 2018 02:00 PM None
    Skip this task, too old!
    (...)

or with a filter (new in 2021):

    ./OrgModeClocking2Calendar.py -d 3 mq  /Users/magnus//geekbook/notes/work-curr.org --filter '#mq' --log mq.log
    # insert clockings related to "#mq" (a tag I used for this project) into mq calendar (on your Mac, this 
    # calendar can be both Apple Calendar and Google Calendar, 
    # -d 3 means to use clocking from last 3 days (inclusive)
    # and the clocking inserted are saved into mq.log
    # (this file is used to check what is already in the calendar, if you remove this file that the script 
    # will simply add again all the clockings for "#mq")

The script is straightforward, it's a hack in some sense. For each clocking entry, an Apple Script is generated and Apple Tell is executed to push a new even to selected Calendar. Works only on Mac. All already entered entries go to a log file, so they are not entered one again.

[1] https://orgmode.org/manual/Clocking-commands.html#Clocking-commands

![hmgi7zdv67e71](https://user-images.githubusercontent.com/118740/127624535-66fa5243-94f3-4d4d-90a7-b60ae8a8f0d3.jpg)

Changelog:

- 210729 add --filter
- 200330 --date DATE
