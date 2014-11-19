import json

from PyKDE4 import kdecore

import mykde


# http://api.kde.org/frameworks-api/frameworks5-apidocs/plasma-framework/html/classPlasma_1_1Applet.html
PLASMA_DESKTOP_APPLETSRC_PATH = '~/.kde/share/config/plasma-desktop-appletsrc'


class Action(mykde.BaseAction):

    name = "Homerun Kicker"
    description = """
Install and add to all panels Homerun Kicker widget
<br>
<img src="screenshot.jpg"/>
"""
    affects = [mykde.Plasma]
    packages = ['plasma-widget-homerun-kicker']

    def proceed(self):

        konf_path = self.make_abs_path(PLASMA_DESKTOP_APPLETSRC_PATH)
        # http://api.kde.org/pykde-4.7-api/kdecore/KConfig.html
        konf = kdecore.KConfig(konf_path, kdecore.KConfig.SimpleConfig)
        conf = self.get_group_dict(konf)

        # calculate maximum applet ID
        max_applet_id = self.get_max_applet_id(conf)

        for containment_id, containment in conf['Containments'].items():
            # NOTE: should we care about activityId?
            # if containment["screen"] != 1:
            #     continue  # for tests
            if containment["plugin"] != "panel":
                continue
            # containment["formfactor"] == 3:  # enum Plasma::Types::FormFactor Vertical
            applets = list(containment['Applets'].items())
            applets.sort(key=lambda item: item[1]["LayoutInformation"]["Order"])
            if applets[0][1]['plugin'] == 'org.kde.homerun-kicker':
                continue
            max_applet_id += 1
            applets.insert(0, (str(max_applet_id), {
                "plugin": "org.kde.homerun-kicker",
                "LayoutInformation": {"Order": 0},
            }))
            for applet_order, (applet_id, applet) in enumerate(applets):
                applet["LayoutInformation"]["Order"] = applet_order
            containment['Applets'] = dict(applets)

        self.write_group_dict(konf, conf)  # dict -> rc file
        # save the changes to the rc file
        konf.sync()

    def get_group_dict(self, kgroup):
        group = {}
        for entry_name, entry_value in kgroup.entryMap().items():
            try:
                entry_value = int(entry_value)
            except ValueError:
                pass
            group[entry_name] = entry_value
        for group_name in kgroup.groupList():
            group[group_name] = self.get_group_dict(kgroup.group(group_name))
        return group

    def write_group_dict(self, kgroup, group):
        for entry_name, entry_value in group.items():
            if isinstance(entry_value, dict):
                self.write_group_dict(kgroup.group(entry_name), entry_value)
            else:
                kgroup.writeEntry(entry_name, entry_value)

    def get_max_applet_id(self, conf):
        # calculate maximum applet ID
        max_applet_id = 0
        for containment_id, containment in conf['Containments'].items():
            for applet_id in containment.get('Applets', []):
                max_applet_id = max(max_applet_id, int(applet_id))
        return max_applet_id
