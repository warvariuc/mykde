from scripts import Action


class Action(Action):

    name = "Useful apps"
    description = """
Other useful applications:
<ul>
    <li>7-zip archiver libs</li>
    <li>SpeedCrunch calculator</li>
    <li>KolourPaint</li>
</ul>
"""
    packages = ['p7zip-full', 'speedcrunch', 'kolourpaint4', 'pavucontrol']

    def proceed(self):
        pass
