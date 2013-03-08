from mykde import Action


class KubuntuBackportsPpa(Action):

    name = "Kubuntu Backports PPA"
    description = """
Kubuntu Backports PPA (Personal Package Archives) contains backports of new versions of KDE and
major KDE apps for Kubuntu which are either too large a change or not yet tested enough to go to
Ubuntu Backports.<br>
These are only final releases of major new versions of KDE and related packages.<br>
Generally these can be expected to work, but will often be less mature or less tested than versions
in the official repositories for a release.
"""

    repositories = {
        'ppa:kubuntu-ppa/backports': ('', '')
    }
