# Future import
#from __future__ import absolute_import

# Python import
from sys import exit
from re import split
from os import path
from requests import put, get, delete
from argparse import ArgumentParser
from base64 import b64encode
from getpass import getpass
from datetime import datetime
from json import dumps

# Local import
from student import Student
from collaboration import Collaboration
from send_email import Email

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

def read_command_line():
    """Read arguments from commandline"""
    parser = ArgumentParser()

    parameters = {}
    lines = open('default_parameters.txt', 'r').readlines()
    for line in lines:
        key, value = line.split(':')
        parameters[key] = value[:-1]
        
    # File with attendance
    date = datetime.now()
    month = str(date.month) if date.month > 9 else "0" + str(date.month)
    day = str(date.day) if date.day > 9 else "0" + str(date.day)
    parameters['filepath'] = parameters['filepath'] % (date.year, month, day)

    parser.add_argument('--f', '--file', type=str,
                        default=parameters['filepath'], 
                        help=""" A file including all students, in this course. Format: \
                        Attendence(X/-) //  Name //  Username // email""", metavar="students_file")
    parser.add_argument('--c', '--course', type=str,
                        default=parameters['course'], help="Name of the course", metavar="course")
    parser.add_argument('--u', '--university', type=str,
                        default=parameters['university'],
                        help="Name of the university, the viritual-classroom should \
                        be called <university>-<course>", metavar="university")
    parser.add_argument('--m', '--max_students', type=str, default=parameters['max_students'],
                        help="Maximum number of students in each group.", metavar="max group size")
    parser.add_argument('--e', '--end_group', type=bool,
                        default=False, metavar="end group (bool)", 
                        help='Delete the current teams on the form Team-<number>')
    parser.add_argument('--i', '--start-semester', type=bool,
                        default=False, metavar="initialize group (bool)",
                        help='Create repositories and teams for the students.')

    args = parser.parse_args()

    # Check if file exists    
    if not path.isfile(args.f):
       msg = "The file: %s does not exist. \nPlease provide a different file path, or" +\
             " create the file first. Use cp students_base.txt %s YYYY-MM-DD.txt"
       msg = msg % (args.f, args.c)
       print(msg)
       exit(1)

    # Make sure end and start_semester is a bool
    end = args.e if args.e == False else True
    start_semester = args.i if args.i == False else True

    return args.f, args.c, args.u, int(args.m), end, start_semester


def get_password():
    """Get password and username from the user"""
    # Get username and password for admin to classroom
    admin = input('For GitHub\nUsername: ')
    p = getpass('Password:')

    # Check if username and password is correct
    r = get('https://api.github.com', auth=(admin, p))
    if r.status_code != 200:
        print('Username or password is wrong (GitHub), please try again!')
        exit(1)    

    return (admin, p)


def create_students(students_file, course, university):
    """Creates a dicts of students with their full name as a key."""
    students = {}
    text = open(students_file).readlines()

    # Get username and password for admin to classroom
    auth = get_password() 
  
    # Push the file with present
    #push_attendance(auth, course, university)

    # Initialize email
    send_email = Email()

    # Create a dict with students
    for line in text:
        pressent, name, username, email = split(r"\s*\/\/\s*", line.replace('\n', ''))
        if pressent == 'X':
            students[name] = Student(name, username, university, course, email, auth, send_email)

    return students   

def push_attendance(auth, course, university):
    """Push the attendance file to the repo for later use"""
    date = datetime.now()
    month = str(date.month) if date.month > 9 else "0" + str(date.month)

    # Get content
    filename = "%s-%d-%s-%d.txt" % (course, date.year, month, date.day)
    content = b64encode(open("Attendance/%s" % filename, 'r').read())

    # Parameters
    key_push = { 'message': 'Attendance %s'  % filename.split('.')[0],
                 'commiter': {
                               'name': 'Username: %s' % auth[0],
                               'email': 'inf5620@gmail.com'
                             },
                 'content': content
               }
    url = 'https://api.github.com/repos/%s-%s/Attendance/contents/%s' % \
           (university, course, filename)

    # Push file
    r = put(url, data=dumps(key_push), auth=auth) 
   

def end_group(org):
    """Deletes all teams on the form Team-<number>"""
    auth = get_password('Github')
    url_orgs = 'https://api.github.com/orgs/%s/teams' % (org)    

    list_teams = get(url_orgs, auth=auth)
    success = True
    number_deleted = 0

    for team in list_teams.json():
        if 'Team-' in team['name']:
            r = delete("https://api.github.com/teams/" + str(team['id']), auth=auth)
            if r.status_code != 204:
                print('Could not delete team %s' % team['name'])
                success = False
            else:
                number_deleted += 1

    if success:
        print('Deleted all teams related to the group session (%d teams deleted)' % number_deleted)


def main():
    students_file, course, university, max_students, end, start_semester = read_command_line()
    if end:
        org = "%s-%s" % (university, course)
        end_group(org)
    else:
        students = create_students(students_file, course, university)
        if not start_semester:
            Collaboration(students, max_students)


if __name__ == '__main__':
    main()
