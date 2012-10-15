__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>, 2012"

import sys, os
from PyQt4 import QtCore, QtGui, QtWebKit


def load_page(themeDir):
    #webView.load(QtCore.QUrl(pageFilePath)) # load existing page
    html = '''\
<html><head>
<script language="JavaScript">
function popupImage(img) {
  var newImg = new Image();
  newImg.src = img.src;
  window.open(img.src, '', 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=no, resizable=no, copyhistory=no, width=' + newImg.width + ', height=' + newImg.height);
}
</script>
<style type="text/css">
.thumbnail_placeholder {
  display: table;
  float: left;
  padding: 3px;
  margin: 3px;
  background-color: #FFFFF;
  cursor: pointer;
  border: 2px solid #E0E0E0;
  -webkit-border-radius: 5px;
}
.thumbnail_placeholder:hover {
  background-color: #F5F5F5;
  border: 2px solid rgb(241,173,143);
}
.thumbnail_placeholder > * {
  width: 300px;
  height: 240px;
  display: table-cell;
  text-align: center;
  vertical-align: middle;
}
.thumbnail_placeholder > * > img {
  max-width: 100%;
  max-height: 100%;
}
</style>
</head><body><h3>Description</h3>
'''
    themeDir = unicode(themeDir)
    with open(os.path.join(themeDir, 'description')) as file:
        html += file.read().replace('\n', '<br/>') # theme description
    html += '<p><hr><h3>Screenshots</h3>'
    html += '<p>Click to view in full size:</p>'
    screenshotsDir = os.path.join(themeDir, 'screenshots')

    for fileName in os.listdir(screenshotsDir):
        filePath = os.path.join(screenshotsDir, fileName)
        if os.path.isfile(filePath):
            html += """\
<div class="thumbnail_placeholder">
    <div>
        <img src="file://{}" onclick="javascript:popupImage(this)"/>
    </div>
</div>""".format(filePath)

    html += '<div style="clear: both"></div></body></html>'
    webView.setHtml(html)


def handle_link_clicked(url):
    QtGui.QDesktopServices.openUrl(url)

def handle_context_menu(coord):
    menu = QtGui.QMenu()
    menu.addAction('Clear', lambda: webView.setHtml(''))
    menu.exec_(QtGui.QCursor().pos())

def createWindow(webWindowType):
    global __webView # reference to avoid segmentation fault
    __webView = QtWebKit.QWebView()
    return __webView


def init(_webView):
    global webView
    webView = _webView

    webView.createWindow = createWindow # override this function to enable popup windows
    webView.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
    webView.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)
    webView.linkClicked.connect(handle_link_clicked)
    webView.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
    webView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
    webView.customContextMenuRequested.connect(handle_context_menu)

