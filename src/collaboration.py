from requests import get, put, post, delete
from sys import exit
from json import dumps

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

class Collaboration():
    """Holds all the information about the groups during a group session"""

    def __init__(self, students, max_group_size, send_email, rank):
        """Divide the students in to groups and give them access to another groups
           reposetories."""
        if len(students.values()) < 2:
            print("There are one or less students, no need for collaboration")
            sys.exit(1)

        self.send_email = send_email

        if max_group_size > len(students.values()):
            #TODO: This case failes
            self.groups = list(students.values())
            test_student = self.groups[0]

        else:
            # Set up groups with max number of students
            number_of_students = len(students.values())
            rest = number_of_students%max_group_size
            integer_div = number_of_students//max_group_size
            number_of_groups = integer_div if rest == 0 else integer_div + 1

            if not rank:
                self.groups = []
                for i in range(number_of_groups):
                    self.groups.append(list(students.values())[i::number_of_groups])

            else:
                rank_1 = []
                rank_2 = []
                rank_3 = []

                # get a list of students seperated on rank
                for s in students.itervalues():
                    if s.rank == 1:
                        rank_1.append(s)
                    elif s.rank == 2:
                        rank_2.append(s)
                    elif s.rank == 3:
                        rank_3.append(s)

                # Container for groups
                self.groups = [[] for i in range(number_of_groups)]

                # One from each category
                stopped1 = 0
                stopped2 = 0
                stopped3 = 0
                nloops = 0
                while stopped1 + stopped2 + stopped3 < 3:
                    nloops += 1
                    for i in range(number_of_groups*(nloops-1),
                                number_of_groups*nloops):
                        j = number_of_groups*(nloops-1)
                        if i < len(rank_1):
                            self.groups[i-j].append(rank_1[i])
                        elif stopped1 == 0:
                            stopped1 = 1

                        if i < len(rank_2):
                            self.groups[i-j].append(rank_2[i])
                        elif stopped2 == 0:
                            stopped2 = 1

                        if i < len(rank_3):
                            self.groups[i-j].append(rank_3[i])
                        elif stopped3 == 0:
                            stopped3 = 1

            test_student = self.groups[0][0]

        # Get some parameters from the student instance
        self.auth = test_student.auth
        self.url_orgs = test_student.url_orgs
        self.org = test_student.org
        self.url_teams = test_student.url_teams

        teams = test_student.get_teams()  # get all teams in the UiO organisation
        max_team_number = 0
        for team in teams:
            if 'Team-' in team['name'].encode('utf-8'):
                if max_team_number == 0:
                    print('Warning: There are already teams with collaboration. Delete these by runing'\
                          +' "python start_group.py --e True"')

                    max_team_number = max(max_team_number,
                            int(team['name'].split('-')[1]))

        # Check that all students have repository names. Otherwise
        # print warning and abort
        for students in self.groups:
            for student in  students:
                try:
                    student.repo_name
                except:
                    print "Uups. student {} has no repostory. You need to fix that.".format(student.email)
                    import sys; sys.exit(1)


        for n, group in enumerate(self.groups):

            # Get evualation group (next group in the list)
            eval_group = self.groups[(n+1)%len(self.groups)]

            # Create a team with access to an another team's repos
            repo_names = self.get_repo_names(eval_group)
            team_name = "Team-%s" % (n + max_team_number + 1)
            team_key = {
                        "name": team_name,
                        "permission": "push",     # or pull?
                        "repo_names": repo_names  # is this necessary?
                       }
            r_team = post(
                          self.url_orgs+"/teams",
                          data=dumps(team_key),
                          auth=self.auth
                         )

            # When creating a team the user is added, fix this by removing
            # auth[0] from the team before the students are added
            if r_team.json()['members_count'] != 0 and r_team.status_code == 201:
                url_rm_auth = self.url_teams + '/' + str(r_team.json()['id']) + \
                               '/members/' + self.auth[0]
                r_remove_auth = delete(url_rm_auth, auth=self.auth)
                if r_remove_auth.status_code != 204:
                    print("Could not delete user:%s from team:%s, this should"
                        "be done manualy or by a seperate script" % (self.auth[0], team_name))

            # Add repos to the team
            for s in eval_group:
                url_add_repo = s.url_teams + "/%s/repos/%s/%s" \
                           % (r_team.json()['id'], s.org, s.repo_name)
                r_add_repo = put(url_add_repo, auth=s.auth)
                if r_add_repo.status_code != 204:
                    print("Error: %d - Can't add repo:%s to Team-%d" \
                                   % (r_add_repo.status_code, s.repo_name, n))

            # Add students to the team
            for s in group:
                url_add_member = s.url_teams + "/%s/members/%s" \
                           % (r_team.json()['id'], s.username)
                r_add_member = put(url_add_member, auth=s.auth)
                if r_add_member.status_code != 204:
                    print("Error: %d - Can't give user:%s access to Team-%d" \
                                   % (r_add_member.status_code, s.username, n))

            # Add solution repo
            r_add_fasit = put(s.url_teams + "/%s/repos/%s/Solutions" %
                                (r_team.json()['id'], s.org), auth=s.auth)
            if r_add_fasit.status_code != 204:
                print("Error: %d - Can't add solutions repo to teams")

            # TODO: Create google form here

            # Send email
            if send_email is not None:
                self.send_email.new_group(team_name, group, eval_group)#, self.project)

    def get_repo_names(self, team):
        repo_names = []
        for s in team:
            #print(s.org)
            #print(s.name)
            repo_names.append("github/%s/%s-%s" % (s.org, s.course, s.repo_name))
        return repo_names
