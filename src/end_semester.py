"""A script to end the semester. Removes all repositories matching the students in
Attendence/student_base.txt and all teams Team-<number>. This script should not
be invoked unless you are absolutly certain."""

import requests
import re
import sys
from os import path
from getpass import getpass
from classroom import Classroom

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

org = "%(university)s-%(course)s" % parameters

# Get list of teams and repos
url_orgs = 'https://api.github.com/orgs/%s' % (org)
classroom = Classroom(auth, url_orgs)
list_teams = classroom.get_teams()
list_repos = classroom.get_repos()
list_members = classroom.get_members()

# Find list of teams and members to delete
teams_to_delete = []
members_to_delete = []
text = open(path.join(path.dirname(__file__), "Attendance", course + "students_base.txt"), 'r')
for line in text:
    line = re.split(r'\s*\/\/\s*', line)
    teams_to_delete.append(line[1])
    members_to_delete.append(line[2])

# Delete members
for member in list_members:
    #if member['login'].encode('utf-8') in members_to_delete
    if member["type"] == "User":
        print "Deleting ", member["login"],
        r = requests.delete(url + "/members/" + str(member['login']), auth=auth)
        print r.status_code

# Delete teams
for team in list_teams:
   if team['name'].encode('utf-8') in teams_to_delete:
       print "Deleting ", team["name"],
       r = requests.delete(url + "/teams/" + str(team['id']), auth=auth)
       print r.status_code

# Delete repos
for repo in list_repos:
   if course in repo['name']:
       print "Deleting repository ", org + repo['name'],
       r = requests.delete(url + "/repos/%s/" % org + repo['name'], auth=auth)
       print r.status_code
