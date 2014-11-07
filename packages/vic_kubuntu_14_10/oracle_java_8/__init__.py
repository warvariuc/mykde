import mykde


class Action(mykde.BaseAction):

    name = "Oracle Java Runtime Environment 8"
    description = """
Oracle Java Runtime Environment 8
"""

    repositories = {
        'ppa:webupd8team/java': ('', '')
    }
    packages = ['oracle-java8-installer']
