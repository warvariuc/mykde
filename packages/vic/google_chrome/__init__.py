from scripts import Action


class Action(Action):

    name = "Google Chrome"
    description = """\
Google Chrome has out of the box support for proprietary audio/video codesc, Adobe Flash, PDF support.<br>
<a href="http://code.google.com/p/chromium/wiki/ChromiumBrowserVsGoogleChrome">Differences between Google Chrome and Linux distro Chromium </a>
"""
    
    trusted_public_keys = ['https://dl-ssl.google.com/linux/linux_signing_key.pub']
    repositories = {
        'google.list': 'http://dl.google.com/linux/chrome/deb/ stable main'
    }
    packages = ['google-chrome-stable']
