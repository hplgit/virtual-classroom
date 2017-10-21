#!/usr/bin/env python
# Future import
from __future__ import print_function, unicode_literals

# Python import
from sys import exit
from os import path
from argparse import ArgumentParser
from datetime import datetime

# Virtual classroom
from virtual_classroom.parameters import get_parameters
from virtual_classroom.classroom import Classroom


def read_command_line():
    """Read arguments from commandline"""
    parser = ArgumentParser()

    parameters = get_parameters()

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
    parser.add_argument("--email_tmp_file", dest="email_tmp_file", type=str, default="email_tmp_%s.txt",
                        help="This argument is used to determine the name of the file to store information \
                             emails sent.")
    parser.add_argument("--email_delay", dest="email_delay", type=float, default=1.0,
                        help="This argument is used to determine the delay between each email sent.")
    parser.add_argument("--email_review_groups", dest="email_review_groups", type=bool, default=False,
                        help="This flag tells the script to only send emails to review groups.\
                         Useful if sending out the emails was interrupted.")
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
            args.email, args.email_tmp_file, args.email_delay, args.email_review_groups


def main():
    students_file, course, university, max_students, \
     end, start_semester, get_repos, get_repos_filepath, get_feedback, \
      get_feedback_filepath, smtp, rank, email, email_tmp_file, email_delay, \
        email_review_groups = read_command_line()

    classroom = Classroom(students_file)

    if end:
        classroom.end_peer_review()

    elif get_repos:
        classroom.download_repositories(get_repos_filepath)

    elif get_feedback:
        from virtual_classroom.get_all_feedbacks import Feedbacks
        # TODO: Not yet supported.
        feedbacks = Feedbacks(university, course, get_feedback_filepath)
        feedbacks()

    else:
        if not email_review_groups:
            if not start_semester:
                classroom.start_peer_review(max_group_size=max_students, rank=rank)
            elif email:
                classroom.email_students("message_new_student.rst",
                                         "New repository",
                                         smtp=smtp)

        if (not start_semester and email) or email_review_groups:
            classroom.email_review_groups("message_collaboration.rst",
                                          "New group",
                                          smtp=smtp,
                                          tmp_file=email_tmp_file,
                                          delay=email_delay)

if __name__ == '__main__':
    main()
