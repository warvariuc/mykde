from mykde import BaseAction


class Action(BaseAction):

    name = "Useful apps"
    packages = ['p7zip-full', 'speedcrunch', 'kolourpaint4', 'pavucontrol', 'overlay-scrollbar',
                'kwrite', 'openjdk-7-jdk']
    description = """
Some useful applications:
<ul>
    <li>7-zip archiver libs</li>
    <li>SpeedCrunch calculator</li>
    <li>KolourPaint image editor</li>
    <li>...</li>
</ul>
Full list: %s
""" % ', '.join(packages)

    def proceed(self):
        pass
