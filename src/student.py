import requests


class Student()
   
    def __init__(self, name, username, classroom, course, admin, p):
        self.name = name
        self.username = username
        self.classroom = classroom
        self.course = course
        self.auth = (admin, p)
        self.url = 'https://api.github.com/orgs/%s' % classroom

        # Check that there is an user with the given username
        assert_is_user()

        # Check if user have a repository
        if not is_member():
             create_repository()

    def assert_is_user(self):
        # Check if username is valid
        ref = requests.get('https://api.github.com/users/%s' % self.username)
        msg = "User: %s does not exist on GitHub and a \
               repository will not be created." % user 
        assert True if ref.status_code == 200 else False, msg         

    def create_repository(self):
        """Creates a repository '<course>-<first name>' and a team '<full name>'."""
        key_repo = {
                    "name": "%s-%s" % (self.course, self.name.split()[0])
                    "auto_init": True
                    "private": True
                   }

        key_team = {
                    "name": self.name,
                    "permission": "admin",
                    "repo_names": 
                      [ 
                         "github/%s/%s-%s" % 
                         (self.classroom, 
                         self.course, 
                         self.name.split()[0])
                      ]
                   }

        r_repo = requests.post(self.url+"/repos",data=json.dumps(key_repo), auth=self.auth)
        r_team = requests.post(self.url+"/teams",data=json.dumps(key_ream), auth=self.auth)
        url_add = self.url+"/teams/" + self.name + "/members/" + self.username 
        r_add = requests.put(url_add, auth=self.auth)
        # TODO: Check if the operation was a success        

    def add_presens(self):
        #TODO: Store number of times present in some file
        pass

    def is_member(self):        
        ref = request.get(self.url + '/members/%s' % self.username), auth=self.auth)
        return True if ref.status_code == 204 else False
            
    def get_stats(self):
        #TODO: Get number of commits and so on, number of times present ect.
