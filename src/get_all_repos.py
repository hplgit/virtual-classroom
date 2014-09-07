import os
from classroom import Classroom

def collect_repos(auth, university, course, get_repos_filepath):

    call_dir = os.getcwd()
    repos_filepath = os.path.join(call_dir, get_repos_filepath, "%s_all_repos" % course)
    if not os.path.isdir(repos_filepath):
        os.mkdir(repos_filepath)
    #else:
        # TODO: check if there are student repos here allready

    org = "%s-%s" % (university, course)
    url_orgs = 'https://api.github.com/orgs/%s' % (org)
    classroom = Classroom(auth, url_orgs)
    repos = classroom.get_repos()
    SSH_base = "git@github.com:%s/" % org

    SSH_links = []
    for repo in repos:
        if course in repo['name'].encode('utf-8'):
            SSH_links.append(SSH_base + repo['name'].encode('utf-8'))

    # Change to destination folder
    os.chdir(repos_filepath)
    
    for SSH_link in SSH_links:
        result = os.system('git clone ' + SSH_link)
        print(result)

    # Change back to call dir
    os.chdir(call_dir)
