# -*- coding: utf-8 -*-

# For support for python 2 and 3
from __future__ import print_function, unicode_literals

from dateutil.parser import parse
from datetime import datetime

from .api import APIManager


class Student(object):
    """Holds all the information about the student."""

    def __init__(self, name, uio_username, username, university, course, email, present, rank):
        """When initialized it testes if the information is correct and if the
           student has been initialized before. If not it calles create_repository()
        """
        self.name = name
        self._present = "-"
        try:
            self.rank = int(rank)
            if rank > 3 or rank < 1:
                print("%s has a rank out of bound(%s) is has to be," % self.name, self.rank + \
                       "from 1 to 3. It is now set to 2.")
                self.rank = 2
        except:
            print("%s has wrong format on his/her rank," % self.name + \
                  " it has to be an integer. It is now set to 2.")
            self.rank = 2

        self.uio_username = uio_username
        self.email = email
        self.username = username
        self.course = course
        self.university = university

        # Create useful strings
        self.org = "%s-%s" % (university, course)

        # TODO: There probably is a good way to populate this when finding student repo below.
        self.last_active = None
        self.present = present

        self.api = APIManager()

        self.repo_name = "%s-%s" % (self.course, self.uio_username)
        # Check that there is an user with the given username
        if self.is_user():
            repo = self.api.get_repo(self.org, self.repo_name)
            if repo.status_code == 404:
                # Create repo if it doesn't exist
                self.create_repository()
                self.last_active = parse(datetime.now().isoformat(), ignoretz=True)
            else:
                # Populate last active
                self.last_active = parse(repo.json()["pushed_at"], ignoretz=True)

    def is_user(self):
        """
           Check if the given username is a user on GitHub.
           If it is not a user the program will skip this student
           and give a warning.
        """
        ref = self.api.get_user(self.username)
        msg = "User: %s does not exist on GitHub and a repository will not be created." \
               % self.username
        if ref.status_code != 200:
            print(msg)
            return False
        return True

    @staticmethod
    def strip_accents(text):
        """Change special characters into ascii counterpart."""

        # Remove special characters that unicodedata doesn't handle
        text = text.replace('ø', 'o')
        text = text.replace('Ø', 'O')
        text = text.replace('æ', 'ae')
        text = text.replace('é', 'e')
        text = text.replace("'", "")
        text = text.replace('Æ', 'AE')
        text = text.replace('å', 'aa') # Can skip if text is unicode
        text = text.replace('Å', 'AA')

        # TODO: need the text to be unicode to change it. With unicodedata
        #return ''.join(c for c in normalize('NFKD', text) if category(c) != 'Mn')
        return text

    def create_repository(self):
        """Creates a repository '<course>-<uio-username>' and a team '<uio-username>'."""

        # Arguments to new team and repo
        key_repo = {
                    "name": self.repo_name,
                    "auto_init": True,
                    "private": True
                   }
        key_team = {
                    "name": self.uio_username,
                    "repo_names": ["github/%s" % self.repo_name], # correct?
                    "permission": "admin"
                   }

        # Add team and repo
        r_repo = self.api.create_repo(self.org, key_repo)
        r_team = self.api.create_team(self.org, key_team)

        # When creating a team the user is added, fix this by removing
        # auth[0] from the team before the student is added
        if r_team.json()['members_count'] != 0 and r_team.status_code == 201:
            team_id = str(r_team.json()['id'])
            r_remove_auth = self.api.delete_team_member(self.org, team_id, self.api.auth[0])
            if r_remove_auth.status_code != 204:
                print("Could not delete user:%s from team:%s, this should" % (self.api.auth[0], self.name) + \
                        "be done manually or by a separate script")

        # Check success
        success = True
        if r_repo.status_code != 201:
            print("Error: %d - did not manage to add a repository for %s" % \
                  (r_repo.status_code, self.username))
            success = False
        elif r_team.status_code != 201:
            print("Error: %d - did not manage to add a team for %s" % \
                  (r_team.status_code, self.username))
            success = False

        # Add repository to team and invite user to team
        if success:
            team_id = str(r_team.json()['id'])
            # TODO: Is there a reason why you go for Content-Length: 0 for just one of the two PUT requests?
            r_add_repo = self.api.add_team_repo(team_id, self.org, self.repo_name)
            r_add_member = self.api.add_team_membership(team_id, self.username)

            # Check if everthing succeeded
            if r_add_repo.status_code != 204:
                print("Error: %d - did not manage to add repo to team:%s" % \
                      (r_add_repo.status_code, self.name))
            elif r_add_member.status_code != 200:
                print("Error: %d - did not manage to add usr:%s to team:%s" \
                       % (r_add_member.status_code, self.username, self.name))

    def repo_exist(self, repo_name):
        """Check if there exixts a repo with the given name"""
        repos = self.api.get_repos(self.org)
        for repo in repos:
            if repo_name == repo['name']:
                return True

        return False

    def has_team(self):
        """Check if there exist a team <uio-username>"""
        teams = self.api.get_teams(self.org)
        for team in teams:
            if self.uio_username == team['name']:
                return True

        return False

    def get_stats(self):
        """Not implemented"""
        pass

    @property
    def present(self):
        return self._present

    @present.setter
    def present(self, value):
        if value is True or str(value).lower() == "x":
            self._present = "x"
        else:
            self._present = "-"
