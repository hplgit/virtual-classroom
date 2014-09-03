from requests import get, put, post
from json import dumps

class Collaboration():
    """Holds all the information about the groups during a group session"""

    def __init__(self, students, max_group_size):
        """Divide the students in to groups and give them access to another groups
           reposetories.
        """                 
        if len(students.values()) < 2:
            assert False, "There are one or less students, no need for collaboration"

        if max_group_size > len(students.values()):
            #TODO: This case failes
            self.groups = list(students.values())
            test_student = self.groups[0]
        
        else:
            # Set up groups with max number of students
            self.groups = []
            number_of_students = len(students.values())
            rest = number_of_students%max_group_size
            integer_div = number_of_students//max_group_size
            number_of_groups = integer_div if rest == 0 else integer_div + 1
            for i in range(number_of_groups):        
                self.groups.append(list(students.values())[i::number_of_groups])

            test_student = self.groups[0][0]

        # Get some parameters from the student instance
        self.auth = test_student.auth
        self.url_orgs = test_student.url_orgs
        self.org = test_student.org
        self.send_email = test_student.send_email

        teams = test_student.get_teams()
        for team in teams:
            if 'Team-' in team['name'].encode('utf-8'):
                print('There are already teams with collaboration. Delete these by runing'\
                      +' "python start_group.py --e True"')
                exit(1)

        n = 0
        for group in self.groups:
            n = n+1 if len(self.groups)>n+1 else 0

            # Create a team with access to an another team's repos
            repo_names = self.get_repo_names(self.groups[n])
            team_name = "Team-%s" % (n)
            team_key = {
                        "name": team_name,
                        "permission": "push", #or pull? 
                        "repo_names": repo_names # is this necessary
                       }
            r_team = post(
                          self.url_orgs+"/teams",
                          data=dumps(team_key), 
                          auth=self.auth
                         )

            # Add repos to the team
            for s in self.groups[n]:
                url_add_repo = s.url_teams + "/%s/repos/%s/%s" \
                           % (r_team.json()['id'], s.org, s.repo_name)
                r_add_repo = put(url_add_repo, auth=s.auth)
                if r_add_repo.status_code != 204:
                    print("Error: %d - Can't add repo:%s access to Team-%d" \
                                   % (r_add_repo.status_code, s.repo_name, n))
           
            # Add students to the team
            for s in group:
                url_add_member = s.url_teams + "/%s/members/%s" \
                           % (r_team.json()['id'], s.username)
                r_add_member = put(url_add_member, auth=s.auth)
                if r_add_member.status_code != 204:
                    print("Can't give user:%s access to Team-%d" \
                                   % (s.username, n))
            
            # Send email
            self.send_email.new_group(self.groups[n-1], team_name, self.groups[n])
            
    def get_repo_names(self, team):
        return ["github/%s/%s-%s" % (s.org, s.course, s.repo_name) for s in team]
