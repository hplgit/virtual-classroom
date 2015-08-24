"""A script to end the semester. Removes all repositories matching the students in
Attendence/student_base.txt and all teams Team-<number>. This script should not
be invoked unless you are absolutly certain."""

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

# Get course
parameters = {}
default_parameters_path = path.join(path.dirname(__file__), 'default_parameters.txt')
lines = open(default_parameters_path, 'r').readlines()
for line in lines:
    key, value = line.split(':')
    parameters[key] = value[:-1]
course = parameters["course"] + "-"


# Get username and password for admin to classroom
admin = input('Username: ')
p = getpass('Password:')

auth = (admin, p)
url = "https://api.github.com"

# Get parameters
parameters = {}
lines = open('default_parameters.txt', 'r').readlines()
for line in lines:
    key, value = line.split(':')
    parameters[key] = value[:-1]

org = "%(university)s-%(course)s" % parameters

# Get list of teams and repos
list_teams = requests.get(url+"/orgs/%s/teams" % org, auth=auth)
list_repos = requests.get(url+"/orgs/%s/repos" % org, auth=auth)

# Find list of teams to delete
teams_to_delete = []
text = open('Attendance/students_base.txt', 'r')
for line in text:
    line = re.split(r'\s*\/\/\s*', line)
    teams_to_delete.append(line[1])

# Delete teams
for team in list_teams.json():
   if team['name'].encode('utf-8') in teams_to_delete:
       requests.delete(url + "/teams/" + str(team['id']), auth=auth)

# Delete repos
for repo in list_repos.json():
   if course in repo['name']:
       requests.delete(url + "/repos/%s/" % org + repo['name'], auth=auth)
