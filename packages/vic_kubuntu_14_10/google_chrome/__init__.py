import mykde


class Action(mykde.BaseAction):

    name = "Google Chrome"
    description = """
Google Chrome has out of the box support for:
<ul>
    <li>proprietary audio/video codecs</li>
    <li>Adobe Flash</li>
    <li>PDF</li>
</ul>
<a href="http://code.google.com/p/chromium/wiki/ChromiumBrowserVsGoogleChrome">
    Differences between Google Chrome and Linux distro Chromium
</a>
<br>
<img src="screenshot.png"/>
"""

    repositories = {
        'google-chrome.list': ('deb http://dl.google.com/linux/chrome/deb/ stable main',
                               'https://dl-ssl.google.com/linux/linux_signing_key.pub')
        # NOTE: Upon installing Chrome automatically adds its repo to the system
    }
    packages = ['google-chrome-stable']

    def proceed(self):
        self.update_kconfig('./kdeglobals', '~/.kde/share/config/kdeglobals')
