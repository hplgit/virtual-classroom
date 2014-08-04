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
        self.url = 'https://api.github.com/orgs/%s-%s' % (university, course)

        # Check that there is an user with the given username
        self.assert_is_user()

        # Check if user have a repository
        if not self.has_team():
            self.create_repository()

    def assert_is_user(self):
        # Check if username is valid
        ref = requests.get('https://api.github.com/users/%s' % self.username)
        msg = "User: %s does not exist on GitHub and a \
               repository will not be created." % self.username 
        assert True if ref.status_code == 200 else False, msg         

    def create_repository(self):
        """Creates a repository '<course>-<first name>' and a team '<full name>'."""
        key_repo = {
                    "name": "%s-%s" % (self.course, self.name.split()[0]),
                    "auto_init": True,
                    "private": True
                   }

        key_team = {
                    "name": self.name,
                    "permission": "admin",
                    "repo_names": 
                      [ 
                         "github/%s-%s/%s-%s" % 
                         (self.university,
                         self.course, 
                         self.course, 
                         self.name.split()[0])
                      ]
                   }

        r_repo = requests.post(self.url+"/repos",data=json.dumps(key_repo), auth=self.auth)
        r_team = requests.post(self.url+"/teams",data=json.dumps(key_team), auth=self.auth)
        url_add = self.url+"/teams/" + self.name + "/members/" + self.username 
        r_add = requests.put(url_add, auth=self.auth)

        #TODO: Add support for email.
        print(r_repo.status_code, r_team.status_code, r_repo.status_code)
        # Check if everthing succeeded  
        if r_repo.status_code != 204: 
            print("Error: %d - did not manage to add a repository for %s" % \
                  (r_repo.status_code, self.username))

        if r_team.status_code != 201:
            print("Error: %d - did not manage to add a team for %s" % \
                  (r_repo.status_code, self.username))

        if r_repo.status_code != 201:
            print("Error: %d - did not manage to add usr:%s to team:%s" \
                   % (r_repo.status_code, self.username, self.name))

    def add_presens(self):
        #TODO: Store number of times present in some file
        pass

    def has_team(self):        
        ref = requests.get(self.url + '/teams/%s' % self.name, auth=self.auth)
        return True if ref.status_code == 200 else False
            
    def get_stats(self):
        #TODO: Get number of commits and so on, number of times present ect.
        pass
