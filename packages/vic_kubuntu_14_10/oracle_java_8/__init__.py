import mykde


class Action(mykde.BaseAction):

    name = "Oracle Java(TM) Development Kit (JDK) 8"
    description = """
The JDK(TM) is a development environment for building and running applications, applets, and
components using the Java programming language.<br>
The JDK(TM) includes Java Runtime Environment (JRE) for running applications, Java Plug-in for
running applets in web browsers and tools useful for developing and testing programs written in the
Java programming language.
"""

    repositories = {
        'ppa:webupd8team/java': ('', '')
    }
    packages = ['oracle-java8-installer']
