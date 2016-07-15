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
import json

try:
    import gspread
except ImportError:
    print("You need to have gspread to use this script. To install execute:" + \
           "'sudo pip install gspread'")
    sys.exit(1)

try:
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    print("You need to have oauth2client to use this script. To install execute:" + \
           "'sudo pip install oauth2client'")
    sys.exit(1)

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

# Get password and username
json_file = input("Path to Google credentials JSON file (see"\
                  " http://gspread.readthedocs.org/en/latest/oauth2.html): ")

# Get parameters
parameters_path = os.path.join(os.path.dirname(__file__), '..', 'default_parameters.txt')
lines = open(parameters_path, 'r').readlines()
parameters = {}
for line in lines:
    key, value = line.split(':')
    parameters[key] = value[:-1]

# Log on to disk
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

gc = gspread.authorize(credentials)
try:
    wks = gc.open(parameters['course']).sheet1
except gspread.SpreadsheetNotFound:
    json_key = json.load(open(json_file))
    print "The spreadsheet document {} not found. Maybe it does not exist?".format(parameters['course'])
    print "Otherwise, make sure that you shared the spreadsheet with {} and try again.".format(json_key['client_email'])
    sys.exit(1)

# Store file in ../Attendance/
attendance_location = os.path.join(os.path.dirname(__file__), '..',
                                   *parameters["filepath"].split(os.path.sep)[:-1])
# Create ../Attendance/ if it does not exist
if not os.path.exists(attendance_location):
  os.makedirs(attendance_location)

filename = os.path.join(attendance_location, "%s-students_base.txt" % parameters['course'])

if os.path.isfile(filename):
   answ = input("The student_base file exists, are you" + \
                 "sure you want to overwrite this?! (yes/no): ")
   if "yes" != answ.lower():
       exit(1)

student_base = open(filename, 'w')

string = 'Attendance // ' + ' // '.join(wks.get_all_values()[0][1:]) + '\n'
for row in wks.get_all_values()[1:]:
    string += '- // ' + ' // '.join(row[1:]) + '\n' # Remove timestamp from each row

student_base.write(string.encode('utf-8'))

print('Output written on %s.' % filename)

#TODO: Push the new file to a repository
