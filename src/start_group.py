#!/usr/bin/python
# Future import
#from __future__ import absolute_import

# Python import
from sys import exit
from re import split
from os import path
try:
    from requests import put, get, delete
except ImportError:
    print("This program depends on the module request, install to run" +\
           " program!\n\n sudo pip install requests")
    exit(1)
from argparse import ArgumentParser
from base64 import b64encode
from getpass import getpass
from datetime import datetime
from json import dumps

# Local import
from student import Student
from collaboration import Collaboration
from send_email import Email, SMTPGoogle, SMTPUiO
from classroom import Classroom

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

def read_command_line():
    """Read arguments from commandline"""
    parser = ArgumentParser()

    parameters = {}
    default_parameters_path = path.join(path.dirname(__file__), 'default_parameters.txt')
    lines = open(default_parameters_path, 'r').readlines()
    for line in lines:
        key, value = line.split(':')
        parameters[key] = value[:-1]

    # File with attendance
    date = datetime.now()
    month = str(date.month) if date.month > 9 else "0" + str(date.month)
    day = str(date.day) if date.day > 9 else "0" + str(date.day)
    parameters['filepath'] = path.join(path.dirname(__file__),
                                        parameters['filepath'] % (date.year, month, day))

    parser.add_argument('--f', '--file', type=str,
                        default=parameters['filepath'],
                        help=""" A file including all students, in this course. Format:
                        Attendence(X/-) //  Name //  Username // email""", metavar="students_file")
    parser.add_argument('--c', '--course', type=str,
                        default=parameters['course'], help="Name of the course", metavar="course")
    parser.add_argument('--u', '--university', type=str,
                        default=parameters['university'],
                        help="Name of the university, the viritual-classroom should \
                        be called <university>-<course>", metavar="university")
    parser.add_argument('--m', '--max_students', type=int, default=parameters['max_students'],
                        help="Maximum number of students in each group.", metavar="max group size")
    parser.add_argument('--e', '--end_group', type=bool,
                        default=False, metavar="end group (bool)",
                        help='Delete the current teams on the form Team-<number>')
    parser.add_argument('--i', '--start_semester', type=bool,
                        default=False, metavar="initialize group (bool)",
                        help='Create repositories and teams for the students.')
    parser.add_argument('--g', '--get_repos', type=bool,
                        default=False, help="Clone all student repos into the" + \
                                             "filepath ./<course>_all_repos",
                        metavar="Get all repos (bool)")
    parser.add_argument('--get_repos_filepath', type=str, default=".",
                        help="This argument is only used when --get_repos is used. \
                              It states the location of where the folder \
                              <course>_all_repos should be located \
                              this is expected to be a relative path from where \
                              you are when you execute this program",
                        metavar="Get all repos (bool)")
    parser.add_argument('--F', '--get_feedback', type=bool,
                        default=False, help="Store all the feedback files into the" + \
                                             "filepath ./<course>_all_repos. To change" \
                                             " the location use '--get_feedback_filepath'",
                        metavar="Get all feedbacks (bool)")
    parser.add_argument('--get_feedback_filepath', type=str, default="",
                        help="This argument is only used when --get_feedback is used. \
                              It states the location of where the folder \
                              <course>_all_feedbacks should be located \
                              this is expected to be a relative path from where \
                              you are when you execute this program",
                        metavar="Get all feedbacks (bool)")
    parser.add_argument('--smtp', type=str, choices=['uio','google'],
                        default=parameters['smtp'],
                        help='Choose which smtp server emails are to be sent from.')
    parser.add_argument('--rank', type=bool, default=False,
                        help="How to divide in to groups, with or without a \
                        classification of the students from 1 to 3, where 1 is \
                        a top student.", metavar="rank")
    parser.add_argument('--email', dest='email', action='store_true', help="Send email")
    parser.add_argument('--no-email', dest='email', action='store_false', help="Send no email")
    parser.set_defaults(email=True)

    args = parser.parse_args()

    # Check if file exists
    if not path.isfile(args.f) and not args.e and not args.F and not args.g:
       msg = "The file: %s does not exist. \nPlease provide a different file path, or" + \
              "create the file first. Use the script 'copy-attendance-file.py'"
       msg = msg % args.f
       print(msg)
       exit(1)

    return args.f, args.c, args.u, args.m, args.e, args.i, args.g, args.get_repos_filepath, \
            args.F, args.get_feedback_filepath, args.smtp, args.rank, \
            args.email


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


def create_students(students_file, course, university, send_email, rank):
    """Creates a dicts of students with their full name as a key."""
    students = {}
    text = open(students_file).readlines()

    # Get username and password for admin to classroom
    auth = get_password()

    # Push the file with attendance
    #push_attendance(auth, course, university)

    # Create a dict with students
    for line in text:
        print "Handle student {0}".format(line.strip())
        try:
            pressent, name, username, email, subcourse, rank = split(r"\s*\/\/\s*", line.replace('\n', ''))
        except:
            pressent, name, username, email, subcourse = split(r"\s*\/\/\s*", line.replace('\n', ''))
            rank = 1
        if pressent.lower() == 'x' and username != "":
            students[name] = Student(name, username, university, course,
                                     email, auth, send_email, rank)

    return students


def push_attendance(auth, course, university):
    """Push the attendance file to the repo for later use"""
    date = datetime.now()
    month = str(date.month) if date.month > 9 else "0" + str(date.month)
    day = str(date.day) if date.day > 9 else "0" + str(date.day)

    # Get content
    filename = "%s-%s-%s-%s.txt" % (course, date.year, month, day)
    content = b64encode(open("Attendance/%s" % filename, 'r').read())

    # Parameters
    key_push = { 'message': 'Attendance %s'  % filename.split('.')[0],
                 'commiter': {
                               'name': 'Username: %s' % auth[0],
                               'email': 'inf5620@gmail.com' #TODO: find a generall email
                             },
                 'content': content
               }
    url = 'https://api.github.com/repos/%s-%s/Attendance/contents/%s' % \
           (university, course, filename)

    # Push file
    r = put(url, data=dumps(key_push), auth=auth)


def end_group(org):
    """Deletes all teams on the form Team-<number>"""
    auth = get_password()
    url_orgs = 'https://api.github.com/orgs/%s' % (org)

    number_deleted = 0

    classroom = Classroom(auth, url_orgs)
    teams = classroom.get_teams()

    print [team["name"] for team in teams]
    print len(teams)

    number_not_deleted = 0
    not_deleted = ''
    for team in teams:
        if 'Team-' in team['name']:
            r = delete("https://api.github.com/teams/" + str(team['id']), auth=auth)
            if r.status_code != 204:
                number_not_deleted += 1
                not_deleted += '\n' + team['name']
            else:
                number_deleted += 1

    if number_not_deleted == 0:
        print('Deleted all teams related to the group session (%d teams deleted)' % \
                number_deleted)
    else:
        print('Delted %s teams, but there were %s teams that where not deleted:%s' % \
               (number_deleted, number_not_deleted, not_deleted))


def main():
    students_file, course, university, max_students, \
     end, start_semester, get_repos, get_repos_filepath, get_feedback, \
      get_feedback_filepath, smtp, rank, email = read_command_line()

    if end:
        org = "%s-%s" % (university, course)
        end_group(org)

    elif get_repos:
        from get_all_repos import collect_repos
        auth = get_password()
        collect_repos(auth, university, course, get_repos_filepath)

    elif get_feedback:
        from get_all_feedbacks import Feedbacks
        auth = get_password()
        feedbacks = Feedbacks(auth, university, course, get_feedback_filepath)
        feedbacks()

    else:
        if email:
            # Set up e-mail server
            if smtp == 'google':
                server = SMTPGoogle()
            elif smtp == 'uio':
                server = SMTPUiO()
            send_email = Email(server)
        else:
            send_email = None

        students = create_students(students_file, course, university, send_email, rank)
        if not start_semester:
            Collaboration(students, max_students, send_email, rank)

        # Logout e-mail server
        if email:
            try:
                send_email.logout()
            except:
                pass

if __name__ == '__main__':
    main()
