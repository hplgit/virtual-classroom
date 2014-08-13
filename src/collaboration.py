import requests
import json

class Collaboration():
    def __init__(self, students, max_group_size):
        #TODO: Check if there is come team calles Team-<number>
        #      these should be deleted first.
         
        if len(students.values()) < 2:
            assert False, "There are one or less students, no need for collaboration"

        if max_group_size > len(students.values()):
            self.groups = list(students.values())
            self.auth = self.groups[0].auth
            self.url_orgs = self.groups[0].url_orgs
            self.org = self.groups[0].org
        
        else:
            self.groups = []
            number_of_students = len(students.values())
            rest = number_of_students%max_group_size
            truediv = number_of_students//max_group_size
            number_of_groups = truediv if rest == 0 else truediv + 1
            for i in range(number_of_groups):        
                self.groups.append(list(students.values())[i::number_of_groups])

            self.auth = self.groups[0][0].auth
            self.url_orgs = self.groups[0][0].url_orgs
            self.org = self.groups[0][0].org
            self.send_email = self.groupd[0][0].send_email

        n = 0
        for team in self.groups:
            n = n+1 if len(self.groups)>n+1 else 0

            # Create a team with access to an another team's repos
            repo_names = self.get_repo_names(self.groups[n])
            team_name = "Team-%s" % (n)
            team_key = {
                        "name": team_name,
                        "permission": "push", #or pull? 
                        "repo_names": repo_names # is this necessary
                       }
            r_team = requests.post(
                                   team[0].url_orgs+"/teams",
                                   data=json.dumps(team_key), 
                                   auth=self.auth
                                  )

            # Add repos to the team
            for s in self.groups[n]:
                url_add_repo = s.url_teams + "/%s/repos/%s/%s" \
                           % (r_team.json()['id'], s.org, s.repo_name)
                r_add_repo = requests.put(url_add_repo, auth=s.auth)
                if r_add_repo.status_code != 204:
                    print("Error: %d - Can't add repo:%s access to Team-%d" \
                                   % (r_add_repo.status_code, s.repo_name, n))
           
            # Add students to the team
            for s in team:
                url_add_member = s.url_teams + "/%s/members/%s" \
                           % (r_team.json()['id'], s.username)
                r_add_member = requests.put(url_add_member, auth=s.auth)
                if r_add_member.status_code != 204:
                    print("Can't give user:%s access to Team-%d" \
                                   % (s.username, n))
            
            # Send email
            self.send_email.new_group(group[n-1], team_name, group[n]
            
    def get_repo_names(self, team):
        return ["github/%s/%s-%s" % (s.org, s.course, s.repo_name) for s in team]
