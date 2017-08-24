from __future__ import print_function, unicode_literals
import sys
import os

# Local imports
from .api import APIManager
from .parameters import get_parameters


def download_repositories(directory):
    call_dir = os.getcwd()
    repos_filepath = os.path.join(call_dir, directory)
    if not os.path.isdir(repos_filepath):
        os.makedirs(repos_filepath)
    else:
        if os.listdir(repos_filepath) != []:
            print("There are already repos in this folder, please \
                    remove them before cloning new into this folder")
            sys.exit(0)

    parameters = get_parameters()
    university = parameters["university"]
    course = parameters["course"]
    org = "%s-%s" % (university, course)

    api = APIManager()

    print("Getting list of repositories...")
    repos = api.get_repos(org)
    print("Found {} repositories.".format(len(repos)))

    # Create the SSH links
    SSH_links = []
    for i, repo in enumerate(repos):
        print("Getting repository links: {}%".format((100*i)/len(repos)))
        if course in repo['name']:
            r = api.get_repository(repo['id'])
            SSH_links.append(r.json()['ssh_url'])

    # Change to destination folder
    os.chdir(repos_filepath)

    # Clone into the repos
    for i, SSH_link in enumerate(SSH_links):
        print("Cloning repositories {}%".format((100*i)/len(SSH_links)))
        result = os.system('git clone ' + SSH_link)
        print("done.")

    # Change back to call dir
    os.chdir(call_dir)
