import requests

class collaboration()
    def __init__(self, students, max_group_size):
        if len(students.values()) == 0:
            assert False, "There are no students"

        if group_size > len(students.values()):
            self.groups = list(students.values())
        
        else:
            self.groups = []
            number_of_students = len(students.values())
            number_of_groups = number_of_students//max_group_size
            for i in range(number_of_groups):        
                self.groups.append(list(students.values())[i::number_of_groups])

        create_teams()     

     def create_teams(self):
         n = 0
         for team in group:
             n = n+1 if len(group)>n+1 else 0

             repo_names = get_repo_names(group[n])
             team_key = {
                         "name": "Team-%s" % (n+1),
                         "permission": "pull", #or push?
                         "repo_names": repo_names
                        }

             # Create team
             r_team = requests.post(
                                    team[0].url+"/teams",
                                    data=json.dumps(key_ream), 
                                    auth=team[0].auth
                                   )

             # Add students to the team
             for s in teams:
                 url_add = self.url+"/teams/Team-%d/members/%s" % (n+1, s.username)
                 r_add = requests.put(url_add, auth=self.auth)
                 if r_add.status_code != 204:
                     assert False, "Can't add user: %s to team: %s" \
                                    % (s.username, "Team-" % (n+1) )
             
            
     def get_repo_names(team):
         return ["github/%s/%s-%s" % (s.classroom, s.course, s.name.split()[0]) for s in team]

     def remove_teams(self, classroom):
         # Get list of all teams
         # Remove the teams that fit Team-x
          
