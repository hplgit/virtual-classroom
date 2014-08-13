from __future__ import print_function
import requests
import json

class Student():
   
    def __init__(self, name, username, university, course, email, auth, send_email):
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
        self.is_user()

        # Check if user have a team
        if not self.has_team():
            self.create_repository()

        # Get repo name
        else:
            r = requests.get(self.url_orgs + "/teams", auth=auth)
            for team in r.json():
                if team['name'].encode('utf-8') == self.name: 
                    id_ = team['id']

            r = requests.get(self.url_teams + "/" + str(id_) + "/repos", auth=auth)
            for repo in r.json():
                self.repo_name = repo['name']
 

    def is_user(self):
        # Check if username is valid
        ref = requests.get('https://api.github.com/users/%s' % self.username)
        msg = "User: %s does not exist on GitHub and a repository will not be created." \
               % self.username 
        if ref.status_code != 200: print(msg)

    def create_repository(self):
        """Creates a repository '<course>-<first name>' and a team '<full name>'."""
        
        # Find repo name
        self.repo_name = "%s-%s" % (self.course, self.name.split(" ")[0])
        i = 0
        while self.repo_exist(self.repo_name): 
            self.repo_name += self.name.split(" ")[1+i]
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
        r_repo = requests.post(self.url_orgs + "/repos", data=json.dumps(key_repo), auth=self.auth)
        r_team = requests.post(self.url_orgs + "/teams", data=json.dumps(key_team), auth=self.auth)
         
        url_add_member = self.url_teams + "/%s/members/%s" % (r_team.json()['id'], self.username)
        url_add_repo = self.url_teams + "/%s/repos/%s/%s" % (r_team.json()['id'],                                                                                  self.org, self.repo_name)

        r_add_repo = requests.put(url_add_repo, auth=self.auth)
        r_add_member = requests.put(url_add_member, headers={'Content-Length': 0}, auth=self.auth)

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
        list_repos = requests.get(self.url_orgs + "/repos", auth=self.auth)
        for repo in list_repos.json():
            if repo_name == repo['name']:
                return True
        return False
        

    def has_team(self):        
        list_teams = requests.get(self.url_orgs+"/teams", auth=self.auth)
        for team in list_teams.json():
            if self.name == team['name'].encode('utf-8'):
                return True

        return False

            
    def get_stats(self):
        #TODO: Get number of commits and so on, number of times present ect.
        pass
