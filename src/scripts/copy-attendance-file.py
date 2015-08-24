#!/usr/bin/env python

from datetime import datetime
from sys import exit
import os

parameters_path = os.path.join(os.path.dirname(__file__), '..', 'default_parameters.txt')
lines = open(parameters_path, 'r').readlines()

parameters = {}
for line in lines:
    key, value = line.split(':')
    parameters[key] = value[:-1]

date = datetime.now()
month = str(date.month) if date.month > 9 else "0" + str(date.month)
day = str(date.day) if date.day > 9 else "0" + str(date.day)

attendance_file = os.path.join(os.path.dirname(__file__), '..', 
                                parameters['filepath'] % (date.year, month, day))
attendance_folder = os.path.join(os.path.dirname(__file__), '..', 
                                  attendace_file.split(os.path.sep)[:-1])

if not os.path.exists(attendance_folder):
  print('Folder\n  %s\ndoes not exist. Run get-info-google-spreadsheet.py.' \
      % attendance_folder)
  exit(1)

student_base = attendance_folder + '%s-students_base.txt' % parameters['course']
os.system('cp ' + student_base + ' ' + attendance_file)

print('Copied student base to file.\n  %s' % attendance_file)
