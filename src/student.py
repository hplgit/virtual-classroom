# -*- coding: utf-8 -*-

from __future__ import print_function

from requests import get, put, post 
from json import dumps
from sys import exit
from unicodedata import normalize, category

class Student():
    """Holdes all the information about the student.""" 

    def __init__(self, name, username, university, course, email, auth, send_email):
        """When initialized it testes if the information is correct and if the
           student has been initialized before. If not it calles create_repository()
        """
        self.name = name
        self.email = email
        self.username = username
        self.course = course
        self.university = university
        self.auth = auth
        self.send_email = send_email

        # Create useful strings
        self.org = "%s-%s" % (university, course)
        self.url_orgs = 'https://api.github.com/orgs/%s' % (self.org)
        self.url_teams = 'https://api.github.com/teams' 

        # Check that there is an user with the given username
        if self.is_user():
            # Check if user have a team
            if not self.has_team():
                self.create_repository()

            # Get repo name
            else:
                r = get(self.url_orgs + "/teams", auth=auth, params={'per_page': 100})
                header = r.headers['link'].split(',')
                for link in header:
                    if 'rel="last"' in link:
                        pages = int(link.split(';')[0][-2])

                id_ = False
                for page in range(pages):
                    r = get(self.url_orgs + "/teams", auth=auth, 
                             params={'per_page': 100, 'page':page+1})

                    for team in r.json():
                        if team['name'].encode('utf-8') == self.name: 
                            id_ = team['id']
                            break

                    if id_:
                        r = get(self.url_teams + "/" + str(id_) + "/repos", auth=auth)
                        for repo in r.json():
                            self.repo_name = repo['name'].encode('utf-8')
                            break
 
    def is_user(self):
        """
           Check if the given username is a user on GitHub. 
           If it is not a user the program will exit with a worning
        """

        ref = get('https://api.github.com/users/%s' % self.username, auth=self.auth)
        msg = "User: %s does not exist on GitHub and a repository will not be created." \
               % self.username
        if ref.status_code != 200: 
            print(msg)
            return False
        return True

    def strip_accents(self, text):
        """Change special characters into ascii counterpart."""

        # Remove special characters that unicodedata doesn't handle
        text = text.replace('ø', 'o')
        text = text.replace('Ø', 'O')
        text = text.replace('æ', 'ae')
        text = text.replace('Æ', 'AE')
        text = text.replace('å', 'aa') # Can skip if text is unicode
        text = text.replace('Å', 'AA')

        # TODO: need the text to be unicode to change it. With unicodedata
        #return ''.join(c for c in normalize('NFKD', text) if category(c) != 'Mn')
        return text

    def create_repository(self):
        """Creates a repository '<course>-<first name>' and a team '<full name>'."""
        
        # Find repo name
        # Convert special characters
        first_name = self.strip_accents(self.name.split(" ")[0])
        self.repo_name = "%s-%s" % (self.course, first_name)
        i = 0
        while self.repo_exist(self.repo_name): 
            self.repo_name += self.strip_accents(self.name.split(" ")[1+i])
            i += 1
        
        # Arguments to new team and repo
        key_repo = {
                    "name": self.repo_name,
                    "auto_init": True,
                    "private": True
                   }
        key_team = {
                    "name": self.name,
                    "repo_names": ["github/%s" % self.repo_name], # correct?
                    "permission": "admin"
                   }

        # Add team and repo and add repository and user to team.
        r_repo = post(self.url_orgs + "/repos", data=dumps(key_repo), auth=self.auth)
        r_team = post(self.url_orgs + "/teams", data=dumps(key_team), auth=self.auth)

        url_add_member = self.url_teams + "/%s/members/%s" % (r_team.json()['id'], self.username)
        url_add_repo = self.url_teams + "/%s/repos/%s/%s" % (r_team.json()['id'],                                                                                  self.org, self.repo_name)
        r_add_repo = put(url_add_repo, auth=self.auth)
        r_add_member = put(url_add_member, headers={'Content-Length': 0}, auth=self.auth)

        # Check if everthing succeeded  
        if r_repo.status_code != 201: 
            print("Error: %d - did not manage to add a repository for %s" % \
                  (r_repo.status_code, self.username))
        elif r_team.status_code != 201:
            print("Error: %d - did not manage to add a team for %s" % \
                  (r_team.status_code, self.username))
        elif r_add_repo.status_code != 204:
            print("Error: %d - did not manage to add repo to team:%s" % \
                  (r_add_repo.status_code, self.name))
        elif r_add_member.status_code != 204:
            print("Error: %d - did not manage to add usr:%s to team:%s" \
                   % (r_add_member.status_code, self.username, self.name))
        else:
            # Send information to the student
            self.send_email.new_student(self)

    def repo_exist(self, repo_name):
        """Check if there exixts a repo with the given name"""
        list_repos = get(self.url_orgs + "/repos", auth=self.auth, params={'per_page': 100})
        header = list_repo.headers['link'].split(',')
        for link in header:
            if 'rel="last"' in link:
                pages = int(link.split(';')[0][-2])

        for page in range(pages):
            list_repos = get(self.url_orgs + "/repos", auth=self.auth, 
                              params={'per_page': 100, 'page':page+1})
            for repo in list_repos.json():
                if repo_name == repo['name'].encode('utf-8'):
                    return True

        return False
        
    def has_team(self):
        """Check if there exist a team <full name>"""
        # Find number of pages with teams
        list_teams = get(self.url_orgs+"/teams", auth=self.auth, params={'per_page': 100})
        header = list_teams.headers['link'].split(',')
        for link in header:
            if 'rel="last"' in link:
                pages = int(link.split(';')[0][-2])

        for page in range(pages):
            list_teams = get(self.url_orgs+"/teams", auth=self.auth, 
                              params={'per_page': 100, 'page': page + 1})        
            for team in list_teams.json():
                if self.name == team['name'].encode('utf-8'):
                    return True

        return False

    def get_stats(self):
        pass
