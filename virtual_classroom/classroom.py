from requests import get

class Classroom:
    """Contains help functions to get an overveiw of the virtual classroom"""

    def __init__(self, auth, url_orgs):
        self.auth = auth
        self.url_orgs = url_orgs

    def get_teams(self):
        return self._get(self.url_orgs + "/teams")

    def get_repos(self):
        return self._get(self.url_orgs + "/repos")

    def get_members(self, role='all'):
        return self._get(self.url_orgs + "/members", params={'role': role})

    def _get(self, url, params=None):

        p = {'per_page':100, 'page':1}
        if params is not None:
            p.update(params)

        # Find numer of pages
        r = get(url, auth=self.auth, params=p)

        if 'Link' not in r.headers.keys():
            return r.json()

        else:
            header = r.headers['Link'].split(',')
            for link in header:
                if 'rel="last"' in link:
                    pages = int(link.split(';')[0][-2])

            # Get each page
            teams = r.json()
            for page in range(pages-1):
                p['page'] = page+2
                r = get(url, auth=self.auth, params=p)
                teams += r.json()

            return teams
