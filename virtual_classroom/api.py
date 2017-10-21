# Python imports
from requests import get, post, put, delete
from getpass import getpass
from json import dumps
from re import findall

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass


# Mimic enum like behaviour
# Maybe I went too far and made it unnecessarily complicated
class Endpoint(object):
    class EndpointItem(object):
        def __init__(self, *args):
            self.values = []
            for arg in args:
                if isinstance(arg, self.__class__):
                    self.values += [i for i in arg.values]
                else:
                    self.values.append(arg)

        def url(self, *args):
            url = "".join(self.values)
            return url.format(*args)

        def __str__(self):
            return self.url()

    API_URL = EndpointItem("https://api.github.com")

    USERS_API = EndpointItem(API_URL, "/users/{}")

    REPO_API = EndpointItem(API_URL, "/repos/{}/{}")

    REPOSITORIES_API = EndpointItem(API_URL, "/repositories")
    REPOSITORY = EndpointItem(REPOSITORIES_API, "/{}")

    ORGS_API = EndpointItem(API_URL, "/orgs/{}")
    TEAMS = EndpointItem(ORGS_API, "/teams")
    REPOS = EndpointItem(ORGS_API, "/repos")
    MEMBERS = EndpointItem(ORGS_API, "/members")
    ORG_MEMBER = EndpointItem(MEMBERS, "/{}")

    TEAM_API = EndpointItem(API_URL, "/teams/{}")
    TEAM_REPOS = EndpointItem(TEAM_API, "/repos")
    TEAM_REPO = EndpointItem(TEAM_REPOS, "/{}/{}")
    TEAM_MEMBERSHIPS = EndpointItem(TEAM_API, "/memberships")
    TEAM_MEMBERSHIP = EndpointItem(TEAM_MEMBERSHIPS, "/{}")
    TEAM_MEMBERS = EndpointItem(TEAM_API, "/members")


class APIManager(object):
    """Connects and communicates with the Github API.
    
    """
    auth = None

    def __init__(self):
        if self.auth is None:
            self.auth = self.create_auth()

    @classmethod
    def create_auth(cls):
        """Get password and username from the user"""
        # Get username and password for admin to classroom
        admin = input('For GitHub\nUsername: ')
        p = getpass('Password: ')
        cls.auth = (admin, p)

        # Check if username and password is correct
        r = get(Endpoint.API_URL, auth=(admin, p))
        if r.status_code != 200:
            print('Username or password is wrong (GitHub), please try again!')
            exit(1)

        return cls.auth

    def delete_repo(self, owner, name):
        return delete(Endpoint.REPO_API.url(owner, name), auth=self.auth)

    def delete_team(self, org, team):
        return delete(Endpoint.TEAM_API.url(team), auth=self.auth)

    def delete_org_member(self, org, member):
        return delete(Endpoint.ORG_MEMBER.url(org, member), auth=self.auth)

    def delete_team(self, team):
        return delete(Endpoint.TEAM_API.url(team), auth=self.auth)

    def delete_team_membership(self, team, member):
        return delete(Endpoint.TEAM_MEMBERSHIP.url(team, member), auth=self.auth)

    def add_team_repo(self, team_id, org, repo):
        return put(Endpoint.TEAM_REPO.url(team_id, org, repo), headers={'Content-Length': "0"}, auth=self.auth)

    def add_team_membership(self, team_id, member):
        return put(Endpoint.TEAM_MEMBERSHIP.url(team_id, member), headers={'Content-Length': "0"}, auth=self.auth)

    def create_repo(self, org, key_repo):
        return post(Endpoint.REPOS.url(org), data=dumps(key_repo), auth=self.auth)

    def create_team(self, org, key_team):
        return post(Endpoint.TEAMS.url(org), data=dumps(key_team), auth=self.auth)

    def get_repo(self, org, repo_name):
        return get(Endpoint.REPO_API.url(org, repo_name), auth=self.auth)

    def get_repository(self, repo_id):
        return get(Endpoint.REPOSITORY.url(repo_id), auth=self.auth)

    def get_user(self, username):
        return get(Endpoint.USERS_API.url(username), auth=self.auth)

    def get_team_members(self, team_id):
        return self._get(Endpoint.TEAM_MEMBERS.url(team_id))

    def get_team_repos(self, team_id):
        return self._get(Endpoint.TEAM_REPOS.url(team_id))

    def get_teams(self, org):
        return self._get(Endpoint.TEAMS.url(org))

    def get_repos(self, org):
        return self._get(Endpoint.REPOS.url(org))

    def get_members(self, org, role='all'):
        return self._get(Endpoint.MEMBERS.url(org), params={'role': role})

    def _get(self, url, params=None):

        p = {'per_page':100, 'page':1}
        if params is not None:
            p.update(params)

        # Find number of pages
        r = get(url, auth=self.auth, params=p)

        if 'Link' not in r.headers.keys():
            return r.json()

        else:
            header = r.headers['Link'].split(',')
            for link in header:
                if 'rel="last"' in link:
                    link = link.split(";")[0]
                    pages = findall("\?page\=(\d+)", link)
                    if len(pages) <= 0:
                        pages = findall("\&page\=(\d+)", link)
                    pages = int(pages[0])

            # Get each page
            teams = r.json()
            for page in range(pages-1):
                p['page'] = page+2
                r = get(url, auth=self.auth, params=p)
                teams += r.json()

            return teams