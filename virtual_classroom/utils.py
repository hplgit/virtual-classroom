from __future__ import print_function, unicode_literals
import os
import json

from .parameters import get_parameters

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass


def download_spreadsheet(name):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # Get password and username
    json_file = input("Path to Google credentials JSON file (see" \
                      " http://gspread.readthedocs.org/en/latest/oauth2.html): ")

    # Get parameters
    parameters = get_parameters()

    # Log on to disk
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    gc = gspread.authorize(credentials)
    try:
        wks = gc.open(name).sheet1
    except gspread.SpreadsheetNotFound:
        json_key = json.load(open(json_file))
        print("The spreadsheet document '{}' not found. Maybe it does not exist?".format(spreadsheet_name))
        print("Otherwise, make sure that you shared the spreadsheet with {} and try again.".format(
            json_key['client_email']))
        return None

    # Store file in ../Attendance/
    attendance_location = os.path.join(os.path.dirname(__file__), '..',
                                       *parameters["filepath"].split(os.path.sep)[:-1])
    # Create ../Attendance/ if it does not exist
    if not os.path.exists(attendance_location):
        os.makedirs(attendance_location)

    filename = os.path.join(attendance_location, "%s-students_base.txt" % parameters['course'])

    if os.path.isfile(filename):
        answ = input("The student_base file exists, are you " + \
                     "sure you want to overwrite this?! (yes/no): ")
        if "yes" != answ.lower():
            exit(1)

    student_base = open(filename, 'w')

    string = 'Attendance // ' + ' // '.join(wks.get_all_values()[0][1:]) + '\n'
    for row in wks.get_all_values()[1:]:
        string += '- // ' + ' // '.join(row[1:]) + '\n'  # Remove timestamp from each row

    student_base.write(string.encode('utf-8'))

    print('Output written on %s.' % filename)
    return string







