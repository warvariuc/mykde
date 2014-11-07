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
