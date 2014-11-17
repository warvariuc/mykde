import mykde


class Action(mykde.BaseAction):

    name = "Useful apps"
    packages = [
        'p7zip-full',
        'speedcrunch',
        'pavucontrol',
        'kwrite',
        'muon',
    ]
    description = """
Some useful applications:
<ul>
    <li>7-zip archiver</li>
    <li>SpeedCrunch calculator</li>
    <li>...</li>
</ul>
Full list: %s
""" % ', '.join(packages)

    def proceed(self):
        pass
