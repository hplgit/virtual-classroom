# Future import
#from __future__ import absolute_import

# Python import
import sys
import re
import os
import requests
import argparse
from getpass import getpass
from datetime import datetime

# Local import
from student import Student
from collaboration import Collaboration
from send_email import Email

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

def read_command_line():
    parser = argparse.ArgumentParser()

    # File with attendance
    date = datetime.now()
    month = str(date.month) if date.month > 9 else "0" + str(date.month)
    expected_file = "./Attendance/%d-%s-%d.txt" % (date.year, month, date.day)

    parser.add_argument('--f', '--file', type=str,
                        default=expected_file, 
                        help=""" A file including all students, in this course. Format: \
                        Attendence(X/-) //  Name //  Username // email""", metavar="students_file")
    parser.add_argument('--c', '--course', type=str,
                        default="INF5620", help="Name of the course", metavar="course")
    parser.add_argument('--u', '--university', type=str,
                        default="UiO",
                        help="Name of the university, the viritual-classroom should \
                        be called <university>-<course>", metavar="university")
    parser.add_argument('--m', '--max_students', type=str, default="3",
                        help="Maximum number of students in each group.", metavar="university")
    parser.add_argument('--e', '--end_group', type=bool,
                        default=False,
                        help='Will only delete the current teams on the form Team-<number>')

    args = parser.parse_args()

    # Check if file exists    
    if not os.path.isfile(args.f):
       msg = "The file: %s does not exist. \nPlease provide a different file path, or" +\
             " create the file first. Use cp students_base.txt YYYY-MM-DD.txt" % \
              args.f
       print(msg)
       sys.exit(1)

    # Make sure end is a bool
    end = args.e if args.e == False else True

    return args.f, args.c, args.u, int(args.m), end


def get_password(place):
    # Get username and password for admin to classroom
    admin = input('For %s\nUsername: ' % place)
    p = getpass('Password:')

    # Check if username and password is correct
    r = requests.get('https://api.github.com', auth=(admin, p))
    if r.status_code != 200:
        print('Username or password is wrong, pleace try again!')
        sys.exit(1)    

    return (admin, p)


def create_students(students_file, course, university):
    students = {}
    text = open(students_file).readlines()

    # Get username and password for admin to classroom
    auth = get_password('Github') 
  
    #push_attendance(auth)
    # Initialize email
    send_email = "" # Email()

    # Create a dict with students
    for line in text:
        pressent, name, username, email = re.split(r"\s*\/\/\s*", line)
        if pressent == 'X':
            students[name] = Student(name, username, university, course, email, auth, send_email)

    return students   

def push_attendance(auth):
    # TODO: This is not tested, and not done
    # Push the attendance file
    date = datetime.now()
    month = str(date.month) if date.month > 9 else "0" + str(date.month)

    key_push = { 'message': 'Attendance %d-%s-%d"'  % (date.year, month, date.day),
                 'commiter': {
                               'name': 'Username: %s' % auth[0] 
                               'email': 'inf5620@gmail.com'
                             },
                 'content': 'some Base64 coded stuff'
               }
    r = requests.put('repos/%-%/Attendance/contents/', 
    os.system('git add %d-%s-%d.txt'  % (date.year, month, date.day))
    os.system('git commit -m "Attendance %d-%s-%d"'  % (date.year, month, date.day))
    os.system('git push %s@git.com:%s-%s.git' % (auth[0], university, course))
    os.chdir('..')


def end_group(org):
    auth = get_password('Github')
    url_orgs = 'https://api.github.com/orgs/%s/teams' % (org)    

    list_teams = requests.get(url_orgs, auth=auth)
    success = True
    number_deleted = 0

    for team in list_teams.json():
        if 'Team-' in team['name']:
            r = requests.delete("https://api.github.com/teams/" + str(team['id']), auth=auth)
            if r.status_code != 204:
                print('Could not delete team %s' % team['name'])
                success = False
            else:
                number_deleted += 1

    if success:
        print('Deleted all teams related to the group session (%d teams deleted)' % number_deleted)


if __name__ == '__main__':
    students_file, course, university, max_students, end = read_command_line()
    if end:
        org = "%s-%s" % (university, course)
        end_group(org)
    else:
        students = create_students(students_file, course, university)
        Collaboration(students, max_students)
