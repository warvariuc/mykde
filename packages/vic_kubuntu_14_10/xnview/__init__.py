import mykde


class XnView(mykde.BaseAction):

    name = "XnView"
    description = """
XnViewMP is a powerful cross-platform media browser, viewer and converter, supporting more than
500 file formats.
<br>
<img src="screenshot.png"/>
"""
    repositories = {
        'ppa:dhor/myway': ('', ''),
    }
    packages = ['xnview']

    def proceed(self):
        self.print_html('<b>Associate image fiels with XnView, because the package does not do this</b>')
        commands = """\
xdg-mime default xnview.desktop image/jpeg
xdg-mime default xnview.desktop image/png
xdg-mime default xnview.desktop image/bmp
xdg-mime default xnview.desktop image/tiff
xdg-mime default xnview.desktop image/x-portable-anymap
xdg-mime default xnview.desktop image/x-portable-bitmap
xdg-mime default xnview.desktop image/x-portable-graymap
xdg-mime default xnview.desktop image/x-portable-pixmap
"""
        for command in commands.splitlines():
            self.call(command)
