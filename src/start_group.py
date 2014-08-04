# Future import
#from __future__ import absolute_import

# Python import
import sys
import re
import os
import argparse
from getpass import getpass

# Local import
from student import Student
from collaboration import Collaboration

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

def read_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('--f', '--file', type=str,
                        default="students_info.txt", 
                        help=""" A file including all students, in this course. Format: \
                        Present(X/-) //  Name //  Username // email""", metavar="students_file")
    parser.add_argument('--c', '--course', type=str,
                        default="INF5620", help="Name of the course", metavar="course")
    parser.add_argument('--u', '--university', type=str,
                        default="UiO",
                        help="Name of the university, the viritual-classroom should \
                        be called <university>-<course>", metavar="university")
    parser.add_argument('--m', '--max_students', type=str, default="3",
                        help="Maximum number of students in each group.", metavar="university")


    args = parser.parse_args()

    # Check if file exists    
    if not os.path.isfile(args.f):
       msg = "The file: %s does not exist. Please provide a different file path." % \
              args.students_file
       print(msg), sys.exit(1)

    return args.f, args.c, args.u, int(args.m)

def create_students(students_file, course, university):
    students = {}
    text = open(students_file).readlines()

    # Get username and password for admin to classroom
    admin = input('Username: ')
    p = getpass('Password:')

    # Create a dict with students
    for line in text:
        pressent, name, username, email = re.split(r"\s*\/\/\s*", line)
        students[name] = Student(name, username, university, course, email, admin, p)

    return students   


if __name__ == '__main__':
    students_file, course, university, max_students = read_command_line()
    students = create_students(students_file, course, university)
    Collaboration(students, max_students)
