from __future__ import print_function, unicode_literals
import os
import json

from .parameters import get_parameters

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass


class CSVObject(object):
    def __init__(self, filename=None, content=None):
        if filename is None:
            self.raw_content = content
        else:
            self.raw_content = open(filename).read()
        self.values = []
        self._parse()

    def _parse(self):
        import csv
        reader = csv.reader(self.raw_content.splitlines())
        for row in reader:
            self.values.append(row)

    def __getitem__(self, item):
        return self.values[item]


def download_google_spreadsheet(name, filename=None):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # Get password and username
    json_file = input("Path to Google credentials JSON file (see" \
                      " http://gspread.readthedocs.org/en/latest/oauth2.html): ")

    # Log on to disk
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    gc = gspread.authorize(credentials)
    try:
        wks = gc.open(name).sheet1.export()
    except gspread.SpreadsheetNotFound:
        json_key = json.load(open(json_file))
        print("The spreadsheet document '{}' not found. Maybe it does not exist?".format(spreadsheet_name))
        print("Otherwise, make sure that you shared the spreadsheet with {} and try again.".format(
            json_key['client_email']))
        return None

    if filename is not None:
        with open(filename, "w") as f:
            f.write(wks)

    return wks.decode()


def create_students_file_from_csv(csv_str=None, csv_filename=None, output_filename="students_base.txt"):
    csv = CSVObject(filename=csv_filename, content=csv_str)

    if os.path.isfile(output_filename):
        answ = input("The %s file exists, are you " % (output_filename) + \
                     "sure you want to overwrite this?! (yes/no): ")
        if "yes" != answ.lower():
            exit(1)

    student_base = open(output_filename, 'w')

    string = 'Attendance // ' + ' // '.join(csv[0][1:]) + '\n'
    for row in csv[1:]:
        string += '- // ' + ' // '.join(row[1:]) + '\n'  # Remove timestamp from each row

    student_base.write(string)
    student_base.close()

    print('Output written on %s.' % output_filename)
    return output_filename




