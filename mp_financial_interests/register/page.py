
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import requests
import requests_cache


class RegisterPage:

    @property
    def _soup(self):
        return self._get_soup(self.url)

    @staticmethod
    def _get_soup(url):
        _cache_key = '_cache'
        requests_cache.install_cache(_cache_key)
        r = requests.get(url)
        r.raise_for_status()
        # Pages are often malformed, so use the more lenient html5lib parser
        return BeautifulSoup(r.content, "html5lib")

    def get_relative_url(self, path):
        # For a path, Get a URL relative to this page
        return urljoin(self.url, path)
