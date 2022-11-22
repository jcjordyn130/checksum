#!/bin/env python
""" checksum_stats.py -- a script to pretty print the stats file from checksum.py
This is made to be as lightweight as possible for quick sucessive runs using `watch`,
so some design choices are made such as using sys.argv instead of argparser for a simple string argument.
"""

import json
from sys import argv
from datetime import datetime
import os
import time

def print_stats(jsonfile):
    with open(jsonfile, "r") as file:
        stats = json.load(file)
        
    timestartedhuman = datetime.fromtimestamp(stats['timestarted'])

    print(f"Comparing {stats['oldroot']} and {stats['newroot']} using {stats['checksum']}")
    print(f"Running since: {timestartedhuman}")
    print(f"Files processed: {stats['filecount']}")
    print(f"Number of error files: {stats['errorcount']}")
    print(f"Number of different files: {stats['diffcount']}")
    print(f"Number of skipped files: {stats['skippedcount']}")

if len(argv) != 2:
    print("sys.argv length isn't 2... no file passed or too many arguments.")
    raise SystemExit(1)

watchtime = os.getenv("CSUM_WATCH")
if watchtime:
    while True:
        term_size = os.get_terminal_size()
        print("#" * term_size.columns)
        try:
            print_stats(argv[-1])
        except json.decoder.JSONDecodeError:
            print("Error occured while parsing stats file... trying again because of $CSUM_WATCH!")
        time.sleep(float(watchtime))
else:
    print_stats(argv[-1])
