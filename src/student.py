import requests
import json

class Student():
   
    def __init__(self, name, username, university, course, email, admin, p):
        self.name = name
        self.email = email
        self.username = username
        self.course = course
        self.university = university
        self.auth = (admin, p)
        self.org = "%s-%s" % (university, course)
        self.url_orgs = 'https://api.github.com/orgs/%s' % (self.org)
        self.url_teams = 'https://api.github.com/teams'
 

        # Check that there is an user with the given username
        self.is_user()

        # Check if user have a repository
        if not self.has_team():
            self.create_repository()

    def is_user(self):
        # Check if username is valid
        ref = requests.get('https://api.github.com/users/%s' % self.username)
        msg = "User: %s does not exist on GitHub and a repository will not be created." \
               % self.username 
        if ref.status_code != 200: print(msg)

    def create_repository(self):
        """Creates a repository '<course>-<first name>' and a team '<full name>'."""
        repo_name = "%s-%s" % (self.course, self.name.split(" ")[0])
        key_repo = {
                    "name": repo_name,
                    "auto_init": True,
                    "private": True
                   }

        key_team = {
                    "name": self.name,
                    "repo_names": ["github/%s" % repo_name],
                    "permission": "admin"
                   }

        # Add team and repo and add repository and user to team.
        r_repo = requests.post(self.url_orgs + "/repos", data=json.dumps(key_repo), auth=self.auth)
        r_team = requests.post(self.url_orgs + "/teams", data=json.dumps(key_team), auth=self.auth)
        #r_add_repo = requests.put(self.url_teams + "/%s/repos/%s/%s" % (self.name, 
        #                          self.org, repo_name), auth=self.auth)
        url_add = self.url_teams + "/%s/members/%s" % (r_team.json()['id'], self.username)
        r_add_member = requests.put(url_add, headers={'Content-Length': 0}, auth=self.auth)

        #TODO: Add support for email.
        #print(r_repo.status_code, r_team.status_code, r_repo.status_code)

        # Check if everthing succeeded  
        if r_repo.status_code != 201: 
            print("Error: %d - did not manage to add a repository for %s" % \
                  (r_repo.status_code, self.username))

        if r_team.status_code != 201:
            print("Error: %d - did not manage to add a team for %s" % \
                  (r_team.status_code, self.username))

        if r_add_member.status_code != 201:
            print("Error: %d - did not manage to add usr:%s to team:%s" \
                   % (r_add_member.status_code, self.username, self.name))
            print(r_repo.json())

    def add_presens(self):
        #TODO: Store number of times present in some file
        pass

    def has_team(self):        
        ref = requests.get(self.url_teams + '/%s' % self.name, auth=self.auth)
        return True if ref.status_code == 200 else False
            
    def get_stats(self):
        #TODO: Get number of commits and so on, number of times present ect.
        pass
