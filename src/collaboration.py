import requests
import json

class Collaboration():
    def __init__(self, students, max_group_size):
        if len(students.values()) < 2:
            assert False, "There are one or less students, no need for collaboration"

        if max_group_size > len(students.values()):
            self.groups = list(students.values())
        
        else:
            self.groups = []
            number_of_students = len(students.values())
            number_of_groups = number_of_students//max_group_size
            for i in range(number_of_groups):        
                self.groups.append(list(students.values())[i::number_of_groups])

        self.auth = groups[0][0].auth
        self.url_orgs = groups[0][0].url_orgs
        self.org = grooups[0][0].org

        n = 0
        for team in self.groups:
            n = n+1 if len(self.groups)>n+1 else 0

            # Create a team with access to an another team's repos
            repo_names = self.get_repo_names(self.groups[n])
            team_key = {
                        "name": "Team-%s" % (n+1),
                        "permission": "push", #or pull?
                        "repo_names": repo_names
                       }
            r_team = requests.post(
                                   team[0].url_orgs+"/teams",
                                   data=json.dumps(team_key), 
                                   auth=self.auth
                                  )

            # Add students to the team
            for s in team:
                url_add = s.url_team+"/teams/%s/members/%s" % (str(r_team.json()['id']), s.username)
                r_add = requests.put(url_add, auth=s.auth)
                if r_add.status_code != 204:
                    print("Can't give user: %s access to Team-%d" \
                                   % (s.username, n+1))
             
            
    def get_repo_names(self, team):
        return ["github/%s-%s/%s-%s" % (s.university, s.course, s.course, s.name.split()[0]) 
                                       for s in team]

    def remove_teams(self, classroom):
        list_teams = requests.get(url_orgs+"/orgs/%s/teams" % self.org, auth=self.auth)

        for team in list_teams.json():
            if 'Team-' in team['name']:
                requests.delete(url + "/teams/" + str(team['id']), auth=auth)
