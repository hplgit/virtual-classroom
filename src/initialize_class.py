import sys
import re
from student import *

def read_command_line():
    #TODO: Add other options
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str,
                        default="students.txt", 
                        help=""" A file including all students, in this course. File have
                        to be on the format:
                        Present(X/-) //  Name //  Username""", metavar=students_file)
    parser.add_argument('-c', '--course', type=str,
                        default="INF6520", 
                        help="Name of the course", metavar=course)

    args = parser.parse_args()
    #TODO: Check if file exists
    return args.students_file, args.course

def create_students(students_file, course):
    students = {}
    text = open(students_file).readlines()
    for line in text:
        pressent, name, username = re.split(r"\s*\/\/\s*", line)
        students[name] = Student(name, username, course)
    return students
        

def start_class(students):
    groups = []
    number_of_students = len(student.values())
    number_of_groups = number_of_students//3
    for i in range(number_of_groups):
        groups.append(list(students.values())[i::number_of_groups])
    for i in range(len(groups)):
        for student in group[i]:
            next_ = i+1 if i+1 != len(groups) else 0
            student.give_access(group[next_])

if __name__ == '__main__':
    students_file, course = pars_commandline()
    students = create_students(students_file, course)
    start_class(students)
