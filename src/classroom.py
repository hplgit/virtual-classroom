from requests import get

class Classroom:
    """Contains help functions to get an overveiw of the viritual classroom"""

    def __init__(self, auth, url_orgs):
        self.auth = auth
        self.url_orgs = url_orgs

    def get_teams(self):
        return self._get(self.url_orgs + "/teams")

    def get_repos(self):
        return self._get(self.url_orgs + "/repos")

    def _get(self, url):
        # Find numer of pages
        r = get(url, auth=self.auth, params={'per_page':100, 'page':1})
   
        if 'link' not in r.headers.keys():
            return r.json()
        
        else:
            header = r.headers['link'].split(',')
            for link in header:
                if 'rel="last"' in link:
                    pages = int(link.split(';')[0][-2])

            # Get each page   
            teams = r.json()
            for page in range(pages-1):
                r = get(url, auth=self.auth, params={'per_page':100, 'page':page+2})
                teams += r.json()

            return teams
