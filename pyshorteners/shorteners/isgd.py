from pyshorteners.base import BaseShortener
from pyshorteners.exceptions import ShorteningErrorException

class Shortener(BaseShortener):
    """
    Is.gd shortener implementation

    Example:

        >>> import pyshorteners
        >>> s = pyshorteners.Shortener()
        >>> s.isgd.short('http://www.google.com')
        'http://is.gd/TEST'
        >>> s.isgd.expand('http://is.gd/TEST')
        'http://www.google.com'

    """

    api_url = "https://is.gd/create.php"

    def short(self, url, *custom):
        """Short implementation for Is.gd

        Args:
            url: the URL you want to shorten

        Returns:
            A string containing the shortened URL

        Raises:
            ShorteningErrorException: If the API returns an error as response
        """

        url = self.clean_url(url)
        params = {"format": "simple", "url": url, "shorturl": custom}
        response = self._get(self.api_url, params=params)
        if response.ok:
            return response.text.strip()
        raise ShorteningErrorException(response.content)
        # return f'http://is.gd/{list(custom)[0]}'

# s = Shortener()
# print(s.short('http://fb.com', "adobetest15468"))
