from scripts import ActionPackage, ActionSet


class ActionPackage(ActionPackage):
    author = 'Victor Varvaryuk <victor.varvariuc@gmail.com>'
    version = 1
    description = """\
Theme pack name: <b>Classic Blue</b>.

<b>Features:</b>

- <a href="http://kde-look.org/content/show.php?content=40492">QtCurve</a> custom widgets style
- <a href="http://kde-look.org/content/show.php?content=101767">Hycons</a> icons set
- Custom color scheme
- QtCurve custom window borders (Kwin theme)
- <a href="http://www.droidfonts.com/droidfonts/">Droid</a> fonts
- <a href="http://kde-look.org/content/show.php?content=124213">Produkt</a> Plasma theme
- <a href="http://kde-look.org/content/show.php?content=137923">Kubuntu-Silver</a> splash theme
- Custom Krusader settings
- Other minor tweaks

I tried to make the QtCurve theme to contain is little lines as possible - to make visually light.

The theme pack consists of files and settings for different parts of KDE, and scripts to install those.
Author of installation scripts and package compilation: <a href="mailto:victor.varvariuc@gmail.com">Victor Varvariuc</a>, 2011


xnview - unpack to ~/apps/ and create .desktop file in Graphics category
clip2net
"""

from . import fonts


class TestActionSet(ActionSet):
    name = 'test'
    description = 'test'
    actions = [fonts.Action]  # list of action classes contained in this action set
