import requests
import re
import sys
from getpass import getpass

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

# Ask user for verification
answ = input('Are you sure you want to run this script? All teams and repos will be deleted. (yes/no) ')
if answ.lower() != 'yes':
    sys.exit(1)

# Get username and password for admin to classroom
admin = input('Username: ')
p = getpass('Password:')

auth = (admin, p)
url = "https://api.github.com"

# Get list of teams and repos
list_teams = requests.get(url+"/orgs/UiO-INF5620/teams", auth=auth)
list_repos = requests.get(url+"/orgs/UiO-INF5620/repos", auth=auth)

# Find list of teams to delete
teams_to_delete = []
text = open('students_info.txt', 'r')
for line in text:
    line = re.split(r'\s*\/\/\s*', line)
    teams_to_delete.append(line[1])

# Delete teams
for team in list_teams.json():
   if team['name'] in teams_to_delete:
       requests.delete(url + "/teams/" + str(team['id']), auth=auth)

# Delete repos
for repo in list_repos.json():
   if 'INF5620-' in repo['name']:
       requests.delete(url + "/repos/UiO-INF5620/" + repo['name'], auth=auth)
