#!/usr/bin/env python

"""
Collecting information from a google spreadsheet. This spreasheet takes
information from a google form. This is meant for the students to fill
out such that it is easier for you to get all the information you need.

The expected form of the spreadsheet is 
Timestamp | Full name | Username on GitHub | Email address

When you create your google form you should have your questions in this
order.
"""

import sys 
import os 
import getpass

try:
    import gspread
except ImportError:
    print("You need to have gspread to use this script.")
    sys.exit(1)

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

email = input("For Google\nEmail: ")
password = getpass.getpass("Password:")

gc = gspread.login(email, password)
wks = gc.open("INF5620").sheet1

abs_path = os.path.abspath(__file__)
filename = os.path.sep.join(abs_path.split(os.path.sep)[:-2]) + '/Attendance/students_base.txt'
if os.path.isfile(filename):
   answ = input("The student_base file exists, are you" + \
                 "sure you want to overwrite this?! (yes/no): ")
   if "no" == answ.lower():
       exit(1)

student_base = open(filename, 'w')

string = 'Attendance // ' + ' // '.join(wks.get_all_values()[0][1:]) + '\n' 
for row in wks.get_all_values()[1:]:
    string += '- // ' + ' // '.join(row[1:]) + '\n' # Remove timestamp from each row

student_base.write(string.encode('utf-8'))

#TODO: Push the new file to a repository
