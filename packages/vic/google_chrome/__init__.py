from scripts import Action


class GoogleChrome(Action):

    name = "Google Chrome"
    description = """\
Google Chrome has out of the box support for proprietary audio/video codesc, Adobe Flash, PDF support.<br>
<a href="http://code.google.com/p/chromium/wiki/ChromiumBrowserVsGoogleChrome">Differences between Google Chrome and Linux distro Chromium </a>
"""

    repositories = {
        'google.list': ('deb http://dl.google.com/linux/chrome/deb/ stable main',
                        'https://dl-ssl.google.com/linux/linux_signing_key.pub')
    }
    packages = ['google-chrome-stable']
