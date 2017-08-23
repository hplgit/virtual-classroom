# -*- coding: utf-8 -*-

from __future__ import print_function
from re import split
from datetime import datetime

from .student import Student
from .send_email import Email, EmailBody, SMTPGoogle, SMTPUiO, connect_to_email_server
from .parameters import get_parameters
from .collaboration import start_peer_review
from .get_all_repos import download_repositories
from .api import APIManager

try:
    from dateutil.parser import parse
except ImportError:
    print("This program depends on the module dateutil, install to run" + \
          " program!\n\n sudo pip install python-dateutil")
    exit(1)


class Classroom(object):
    """Contains help functions to get an overveiw of the virtual classroom"""

    def __init__(self, file=None):
        self.students = {}
        self.collaboration = None
        self.review_groups = None
        if file is None:
            # TODO: Fetch default file
            return

        # Load parameters
        parameters = get_parameters()
        self.university = parameters["university"]
        self.course = parameters["course"]
        self.org = "%s-%s" % (self.university, self.course)

        lines = open(file, "r").readlines()
        # Create a dict with students
        for line in lines:
            try:
                present, name, username, email, _, _ = split(r"\s*\/\/\s*", line.replace('\n', ''))
                rank = 1
            except:
                present, name, username, email, _ = split(r"\s*\/\/\s*", line.replace('\n', ''))
                rank = 1
            if present.lower() == 'x' and username != "":
                print("Handle student {0}".format(name))
                self.students[name] = Student(name,
                                              username,
                                              self.university,
                                              self.course,
                                              email,
                                              rank)

    def mark_active_repositories(self, active_since, filename=None, dayfirst=True, **kwargs):
        """Create a students file where students with active repositories are marked

        Active here means that the repository has been pushed changes since the given `active_since` date.

        Parameters
        ----------
        active_since : str, datetime
            A string or datetime object representing a date from which to count a repostiory as active.
        filename : str, optional
            A string with the file name of the students file to write to. 
            Default is "students-active-since-dd-mm-yyyy.txt"
        dayfirst : bool, optional
            Used for parsing active_since if it is a string. Then if dayfirst is True ambigious dates will interpret
            the day before the month.
            Default is True.
        kwargs
            Optional keyword arguments that is sent to the parsing of a string `active_since` value.

        """
        if not isinstance(active_since, datetime):
            active_since = parse(active_since, dayfirst=dayfirst, **kwargs)

        if filename is None:
            filename = "students-active-since-%s.%s.%s.txt" % (active_since.day, active_since.month, active_since.year)

        f = open(filename, "w")
        string = "Attendance // Name // Github username // Email // Course" + "\n"

        for student in self.students.values():
            mark = "x" if student.last_active > active_since else "-"
            string += " // ".join((mark,
                                   student.name,
                                   student.username,
                                   student.email,
                                   student.course)) + "\n"

        f.write(string.encode("utf-8"))
        f.close()

    def start_peer_review(self, max_group_size=None, rank=None):
        parameters = get_parameters()
        # TODO: Consider renaming max_students to max_group_size
        max_group_size = parameters["max_students"] if max_group_size is None else max_group_size
        rank = parameters["rank"] if rank is None else rank

        self.review_groups = start_peer_review(self.students, max_group_size, rank)

    def fetch_peer_review(self):
        # TODO: Would be nice to have. Would allow for interactions with ongoing peer reviews.
        pass

    def end_peer_review(self):
        api = APIManager()
        teams = api.get_teams(self.org)

        number_deleted = 0
        number_not_deleted = 0
        not_deleted = ''
        for team in teams:
            if 'Team-' in team['name']:
                r = api.delete_team(team['id'])
                if r.status_code != 204:
                    number_not_deleted += 1
                    not_deleted += '\n' + team['name']
                else:
                    number_deleted += 1

        if number_not_deleted == 0:
            print('Deleted all teams related to the group session (%d teams deleted)' % \
                  number_deleted)
        else:
            print('Deleted %s teams, but there were %s teams that where not deleted:%s' % \
                  (number_deleted, number_not_deleted, not_deleted))

    def end_semester(self):
        # TODO: Also delete teams. Might benefit from iterating through self.students.
        # TODO: Consider if using self.students is better than fetching all members of org.
        #       Downside is some students might not be marked anymore in the students file.
        #       But there would be realistic workarounds for this, and would keep it cleaner here.
        api = APIManager()
        list_repos = api.get_repos(self.org)
        list_members = api.get_members(self.org, "member")

        for member in list_members:
            # if member['login'].encode('utf-8') in members_to_delete
            print("Deleting %s" % member["login"])
            r = api.delete_org_member(self.org, member["login"])
            print(r.status_code)

        # Delete repos
        for repo in list_repos:
            if self.course in repo['name']:
                print("Deleting repository ", self.org + repo['name'])
                r = api.delete_repo(self.org, repo["name"])
                print(r.status_code)

    def download_repositories(self, directory):
        """Downloads all repositories in the classroom
        
        """
        download_repositories(directory)

    def preview_email(self, filename, extra_params={}):
        email_body = EmailBody(filename)

        student = self.students[list(self.students.keys())[0]]
        group = None if self.review_groups is None else self.review_groups[0]
        params = {"group": group, "student": student, "classroom": self}
        params.update(extra_params)
        email_body.params = params
        return email_body.render()

    def email_students(self, filename, subject="", extra_params={}, smtp=None):
        """Sends an email to all students in the classroom.

        Will try to format the email body text with student attributes and `extra_params`.

        Parameters
        ----------
        filename : str
            Path to the file containing the email body text
        subject : str, optional
            Subject of the email
        extra_params : dict, optional
            Dictionary of extra parameters to format the email body text
        smtp : str, optional
            The SMTP server to use. Can either be 'google' or 'uio'.

        """
        server = connect_to_email_server(smtp)
        email_body = EmailBody(filename)
        email = Email(server, email_body, subject=subject)

        for name in self.students:
            student = self.students[name]
            params = {"student": student, "classroom": self}
            params.update(extra_params)
            email_body.params = params
            email.send(student.email)

    def email_review_groups(self, filename, subject="", extra_params={}, smtp=None):
        """Sends an email to all review groups in the classroom.

        Will try to format the email body text with group attributes,
        student attributes and `extra_params`.

        Parameters
        ----------
        filename : str
            Path to the file containing the email body text
        subject : str, optional
            Subject of the email
        extra_params : dict, optional
            Dictionary of extra parameters to format the email body text
        smtp : str, optional
            The SMTP server to use. Can either be 'google' or 'uio'.

        """
        server = connect_to_email_server(smtp)
        email_body = EmailBody(filename)
        email = Email(server, email_body, subject=subject)

        for group in self.review_groups:
            params = {"group": group, "classroom": self}
            for student in group.students:
                params["student"] = student
                params.update(extra_params)
                email_body.params = params
                email.send(student.email)






