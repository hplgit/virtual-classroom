# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
from datetime import datetime
from time import sleep

from .student import Student
from .send_email import Email, EmailBody, SMTPGoogle, SMTPUiO, connect_to_email_server
from .parameters import get_parameters
from .collaboration import start_peer_review
from .get_all_repos import download_repositories
from .api import APIManager
from .students_file import parse_students_file, save_students_file
from .group import ReviewGroup

try:
    from dateutil.parser import parse
except ImportError:
    print("This program depends on the module dateutil, install to run" + \
          " program!\n\n sudo pip install python-dateutil")
    exit(1)


class Classroom(object):
    """Contains help functions to get an overveiw of the virtual classroom"""

    def __init__(self, filename=None, ignore_present=False):
        self.students = {}
        self.collaboration = None
        self.review_groups = None

        # Load parameters
        parameters = get_parameters()
        self.university = parameters["university"]
        self.course = parameters["course"]
        self.org = "%s-%s" % (self.university, self.course)

        try:
            raw_students = parse_students_file(filename)
        except Exception as e:
            print("Error when parsing students file: %s" % e)
            print("Continuing without built students. Some methods will not work.")
            return

        # Create a dict with students
        for student in raw_students:
            if (student["present"].lower() == 'x' or ignore_present) and student["username"] != "":
                rank = 1  # Rank is not functional at the moment.
                print("Initialize student {0}".format(student["name"]))
                self.students[student["username"]] = Student(student["name"],
                                                             student["uio_username"],
                                                             student["username"],
                                                             self.university,
                                                             self.course,
                                                             student["email"],
                                                             student["present"],
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
            If an empty string is given the default (global) students_file will be overwritten.
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
        elif filename == "":
            filename = None

        for student in self.students.values():
            student.present = (student.last_active > active_since)
        save_students_file(self.students.values(), filename=filename)

    def start_peer_review(self, max_group_size=None, rank=None, shuffle=False):
        parameters = get_parameters()
        # TODO: Consider renaming max_students to max_group_size
        max_group_size = parameters["max_students"] if max_group_size is None else max_group_size
        rank = parameters["rank"] if rank is None else rank

        self.review_groups = start_peer_review(self.students, max_group_size, rank, shuffle=shuffle)

    def fetch_peer_review(self):
        # TODO: Limitation is that it fetches all collaborations, not just most recent
        #       (if multiple are active, or one forgot to delete the old)
        api = APIManager()
        teams = api.get_teams(self.org)
        self.review_groups = []
        for team in teams:
            if "Team-" in team["name"]:
                # This is an ongoing review group.
                group_students = []
                members = api.get_team_members(team["id"])
                for member in members:
                    username = member["login"]
                    # TODO: This might crash. A student could drop out mid-peer-review.
                    #       What to do if student doesn't exist?
                    group_students.append(self.students[username])

                review_repos = []
                repos = api.get_team_repos(team["id"])
                for repo in repos:
                    review_repos.append(repo["name"])

                self.review_groups.append(ReviewGroup(team["name"],
                                                      group_students,
                                                      review_repos))
        print("Found %d review groups." % (len(self.review_groups)))

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

    @staticmethod
    def download_repositories(directory):
        """Downloads all repositories in the classroom
        
        """
        download_repositories(directory)

    def preview_email(self, filename, extra_params={}, student=None, group=None):
        """Preview the formatted email of the file.
        
        Useful for making sure the email templates are rendered correctly.
        
        Using the webbrowser package the function will try to open a HTML page,
        for realistic preview of the formatted email.
        
        Parameters
        ----------
        filename : str
            Filename of the template file for the email.
        extra_params : dict, optional
            Extra params to format the email body text.
        student : Student, optional
            If supplied use the values of this student to format the email.
            If not supplied the first student in the student list is chosen.
        group : ReviewGroup, optional
            If supplied use the values of this group to format the email.
            If not supplied the first review group is chosen if it exists in this instance.

        Returns
        -------
        str
            The formatted template in text (not HTML) format.

        """
        email_body = EmailBody(filename)

        student = self.students[list(self.students.keys())[0]] if student is None else student
        if group is None:
            group = None if self.review_groups is None else self.review_groups[0]
        params = {"group": group, "student": student, "classroom": self}
        params.update(extra_params)
        email_body.params = params
        render = email_body.render()

        try:
            import webbrowser
            import os
            path = os.path.abspath('temp.html')
            url = 'file://' + path
            html = '<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8">' \
                   + email_body.text_to_html(render) \
                   + '</html>'

            with open(path, 'w') as f:
                f.write(html)
            webbrowser.open(url)
        except:
            pass
        return render

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

    def email_review_groups(self,
                            filename,
                            subject="",
                            extra_params={},
                            smtp=None,
                            tmp_file="review_groups_{}.txt",
                            delay=1.0):
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
        tmp_file : str, optional
            A temporary file to write information about which emails have been sent.
            The filename may contain one {} which will be filled with a timestamp.
            You can use this file to continue from a previous send email operation that failed midway,
            just remember to specify the correct timestamp if you used the default timestamp.
            Default is "review_groups_%s.txt".
        delay : float, optional
            Delay between each email procedure. The delay is given in seconds and can be a decimal value.
            Default is 1.0.

        """
        if self.review_groups is None:
            self.fetch_peer_review()

        if tmp_file:
            now = datetime.now()
            tmp_file = tmp_file.format(int(now.timestamp()))

        done_mails = []
        try:
            with open(tmp_file, "r") as f:
                contents = f.read()
                done_mails = contents.split(",")
        except IOError:
            pass

        server = connect_to_email_server(smtp)
        email_body = EmailBody(filename)
        email = Email(server, email_body, subject=subject)

        with open(tmp_file, "a") as f:
            for group in self.review_groups:
                params = {"group": group, "classroom": self}
                for student in group.students:
                    if student.email in done_mails:
                        continue
                    params["student"] = student
                    params.update(extra_params)
                    email_body.params = params
                    res = email.send(student.email)
                    if res:
                        f.write("{},".format(student.email))
                    sleep(delay)






