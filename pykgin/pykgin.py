#/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Pkgin API in Python.
This module lets you use pkgin in a python script.
"""

# modules
from subprocess import Popen, PIPE
from pykgin_exceptions import PykginError
import re

# variables
PKGIN_PATH = "/home/solevis/src/pkgin/pkgin"
INSTALLED = 0
OUTDATED = 1
GREATER = 2
STATES = {"=":INSTALLED, "<":OUTDATED, ">":GREATER}
DEFAULT_ARGS = ["-V", "-y"]

class Pykgin(object):
    """Pkgin class provides methods to impletement pkgin in your code."""

    def __init__(self, pkgin_bin=PKGIN_PATH):
        """Constructor."""
        # re parser for package name and version
        self.package_re = \
                re.compile(r'(?P<name>.+(-[^-])*)-(?P<version>.+)')
        self.pkgin_bin = pkgin_bin

    @staticmethod
    def __extract_package_version(package_string):
        """Separate package name and package version
        into a string using regular expression"""
        # remove leading whitespace
        package_string = package_string.strip()
        # create a re parser
        compil = re.compile(r'(?P<name>.+(-[^-])*)-(?P<version>.+)')
        # search package name and version
        search = compil.search(package_string)
        # retrieve result as list
        output = search.groupdict()

        return output

    @staticmethod
    def __execute(pkgin_bin, cmd, *args):
        """Execute pkgin with cmd in arg. Raise an exception
        if there are a pkgin error."""
        dave = open("/dev/null", "w")
        # create the command list
        pkgin = [pkgin_bin]
        pkgin.extend(DEFAULT_ARGS)
        pkgin.append(cmd)
        for arg in args:
            pkgin.append(arg)
        # execute pkgin
        popen = Popen(pkgin, stdout=dave, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)

    def remove(self, *args):
        """Remove packages and depending packages."""
        self.__execute(self.pkgin_bin, "remove", *args)

    def keep(self, *args):
        """Marks package as "non auto-removable"."""
        self.__execute(self.pkgin_bin, "keep", *args)

    def unkeep(self, *args):
        """Marks package as "auto-removable"."""
        self.__execute(self.pkgin_bin, "unkeep", *args)

    def installed(self, package):
        """Say if package is installed or not."""
        packages = self.list()
        for pkg in packages:
            if pkg['name'] == package:
                return True
        return False


    def install(self, *args):
        """Performs packages installation or upgrade."""
        # create the command list
        pkgin = [self.pkgin_bin, "-y", "install"]
        for arg in args:
            pkgin.append(arg)
        # execute pkgin
        popen = Popen(pkgin, stdout=PIPE, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        else:
            # retrieve output
            output = stdoutdata
            # create a list which contain each packages
            output_whole_list = output.split('\n')
            for line in output_whole_list:
                if line.find("to be installed:") != -1:
                    # extract usefull string
                    infos = line.split(':')[1].split('(')
                    # extract string which contains packages list
                    packages_list = infos[0].strip().split(' ')
                    # extract download and install size from the rest of the
                    # string
                    download_size = infos[1].split(' ')[0]
                    install_size = infos[1].split(' ')[3]
                    # extract version of each packages
                    packages = []
                    for pkg in packages_list:
                        packages.append(self.__extract_package_version(pkg))
                    # add infos to a dict
                    output = {}
                    output['packages'] = packages
                    output['download_size'] = download_size
                    output['install_size'] = install_size

                    return(output)

    def clean(self):
        """Clean packages cache."""
        self.__execute(self.pkgin_bin, "clean")

    def update(self):
        """Creates and populates the initial database."""
        self.__execute(self.pkgin_bin, "update")

    def search(self, arg):
        """Search for a package."""
        output_list = []
        # execute pkgin
        popen = Popen([self.pkgin_bin, "-P", "search", arg], stdout=PIPE,
                stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_whole_list = output.split('\n')
        # remove pkgin blabla
        output_whole_list = output_whole_list[0:-5]
        # create a new list in which package informations are separate
        for pkg in output_whole_list:
            # split the string
            current = pkg.split(' ', 2)
            # retrieve package informations
            package = self.__extract_package_version(current[0])
            # extract state keyword
            state = current[1]
            if state in STATES:
                package['state'] = STATES[state]
            else:
                package['state'] = None

            # add the package dictionnary to the list
            output_list.append(package)

        return output_list

    def show_keep(self, command="show-keep"):
        """Display "non auto-removable" packages."""
        output_list = []
        # execute pkgin
        popen = Popen([self.pkgin_bin, "-P", command], stdout=PIPE, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_whole_list = output.split('\n')
        # remove last element (due to the last \n)
        output_whole_list.pop()
        # create a new list in which package informations are separate
        for pkg in output_whole_list:
            current = pkg.split(' ', 1)
            output_list.append(self.__extract_package_version(current[0]))

        return output_list

    def show_no_keep(self):
        """Display "auto-removable" packages."""
        return self.show_keep("show-no-keep")

    def show_full_deps(self, package):
        """Display dependencies recursively."""
        return self.show_deps(package, "show-full-deps")

    def show_rev_deps(self, package):
        """Display reverse dependencies recursively."""
        return self.show_deps(package, "show-rev-deps")

    def show_deps(self, package, command="show-deps"):
        """Display direct dependencies."""
        output_list = []
        # execute pkgin
        popen = Popen([self.pkgin_bin, "-P", command, package], stdout=PIPE, \
                stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_whole_list = output.split('\n')
        # remove last element (due to the last \n)
        output_whole_list.pop()
        # check if the list is empty
        if(len(output_whole_list) != 0):
            # remove the first element (pkgin blabla)
            output_whole_list.pop(0)
        # create a new list in which package informations are separate
        for pkg in output_whole_list:
            output_list.append(self.__extract_package_version(pkg))

        return output_list

    def avail(self):
        """Lists available packages."""
        return self.list("avail")

    def list(self, command="list"):
        """Lists installed packages."""
        output_list = []
        # execute pkgin
        popen = Popen([self.pkgin_bin, "-P", command], stdout=PIPE, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_whole_list = output.split('\n')
        # remove last element (due to the last \n)
        output_whole_list.pop()
        # create a new list in which package name and description are separate
        for pkg in output_whole_list:
            # split the string
            split = pkg.split(' ', 1)
            # extract version and package name
            package = self.__extract_package_version(split[0])
            # remove leading whitespace from the description
            description = split[1].strip()
            # add the desctription to the dictionnary
            package['description'] = description
            # add the package dictionnary to the list
            output_list.append(package)

        return output_list

    def provides(self, package, command="provides"):
        """Show what files a package provides."""
        # execute pkgin
        popen = Popen([self.pkgin_bin, command, package], stdout=PIPE, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each files withou useless char
        output_list = [item.strip() for item in output.split('\n')[1:-1]]

        return output_list

    def requires(self, package):
        """Show what files a package provides."""
        return self.provides(package, "requires")

    @staticmethod
    def export_pkg(filename=None):
        """Export "non auto-removable" packages to stdout."""
        output_list = []
        # execute pkgin
        popen = Popen([self.pkgin_bin, "export"], stdout=PIPE, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        if(filename):
            save = open(filename, "w")
            save.write(output)
        # create a list which contain each files withou useless char
        output_whole_list = [item.strip() for item in output.split('\n')[1:-1]]
        # create a list containing dict in which package and location are
        # separate
        for item in output_whole_list:
            # dict for the current package
            dict_tmp = {}
            # separate location and package name
            item_splited = item.split('/')
            # fill current dict
            dict_tmp['location'] = item_splited[0]
            dict_tmp['package_name'] = item_splited[1]
            # add the dict into the list
            output_list.append(dict_tmp)

        return output_list

    def import_pkg(self, filename):
        """Import "non auto-removable" package list from file."""
        # execute pkgin
        popen = Popen([self.pkgin_bin, "-y", "import", filename], stdout=PIPE,
                stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_whole_list = output.split('\n')
        for line in output_whole_list:
            if line.find("to be installed:") != -1:
                # extract usefull string
                infos = line.split(':')[1].split('(')
                # extract string which contains packages list
                packages_list = infos[0].strip().split(' ')
                # extract download and install size from the rest of the
                # string
                download_size = infos[1].split(' ')[0]
                install_size = infos[1].split(' ')[3]
                # extract version of each packages
                packages = []
                for pkg in packages_list:
                    packages.append(self.__extract_package_version(pkg))
                # add infos to a dict
                output = {}
                output['packages'] = packages
                output['download_size'] = download_size
                output['install_size'] = install_size

        return(output)

    def autoremove(self):
        """Autoremove oprhan dependencies."""
        # execute pkgin
        popen = Popen([self.pkgin_bin, "autoremove"], stdout=PIPE, stdin=PIPE)
        # send "y" to continu e and retrieve output at the same time
        output = popen.communicate("y\n")
        # create a list which contain each packages
        output_whole_list = output[0].split('\n')
        for line in output_whole_list:
            if line.find("to be autoremoved:") != -1:
                # extract usefull string
                infos = line.split(':')[1].split('(')
                # extract string which contains packages list
                packages_list = infos[0].strip().split(' ')
                # extract version of each packages
                packages = []
                for pkg in packages_list:
                    packages.append(self.__extract_package_version(pkg))

                return(packages)

    def upgrade(self, command="upgrade"):
        """Upgrade main packages to their newer versions."""
        # execute pkgin
        popen = Popen([self.pkgin_bin, "-y", command], stdout=PIPE, stdin=PIPE,
                stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_whole_list = output.split('\n')
        # add infos to a dict
        output = {}
        for line in output_whole_list:
            if line.find("to be upgraded:") != -1:
                # extract usefull string
                infos = line.split(':')[1].split('(')
                # extract string which contains packages list
                packages_list = infos[0].strip().split(' ')
                # extract version of each packages
                packages_upgraded = []
                for pkg in packages_list:
                    packages_upgraded.append(\
                            self.__extract_package_version(pkg))
                output['packages_upgraded'] = packages_upgraded
            if line.find("to be installed:") != -1:
                # extract usefull string
                infos = line.split(':')[1].split('(')
                # extract string which contains packages list
                packages_list = infos[0].strip().split(' ')
                # extract download and install size from the rest of the
                # string
                download_size = infos[1].split(' ')[0]
                install_size = infos[1].split(' ')[3]
                # extract version of each packages
                packages_installed = []
                for pkg in packages_list:
                    packages_installed.append(\
                            self.__extract_package_version(pkg))
                output['packages_installed'] = packages_installed
                output['download_size'] = download_size
                output['install_size'] = install_size

        return output

    def full_upgrade(self):
        """Upgrade all packages to their newer versions."""
        return self.upgrade("full-upgrade")

    def show_category(self, category):
        """Show packages belonging to category."""
        output_list = []
        # execute pkgin
        popen = Popen([self.pkgin_bin, "show-category", category], stdout=PIPE, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_raw_list = output.split('\n')
        # remove last element (due to the last \n)
        output_raw_list.pop()
        # extract packages informations
        output_list = []
        for element in output_raw_list:
            print element
            package_raw = element.split("- ")[1]
            print package_raw
            output_list.append(self.__extract_package_version(package_raw))

        return output_list

    def show_pkg_category(self, package):
        """Show package's category"""
        output_list = []
        # execute pkgin
        popen = Popen([self.pkgin_bin, "show-pkg-category", package], stdout=PIPE, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_raw_list = output.split('\n')
        # remove last element (due to the last \n)
        output_raw_list.pop()
        # extract packages informations
        output_list = []
        for element in output_raw_list:
            category = element.split(' ')[0]
            output_list.append(category)

        return output_list

    def show_all_categories(self):
        """Show all categories."""
        output_list = []
        # execute pkgin
        popen = Popen([self.pkgin_bin, "show-all-categories"], stdout=PIPE, stderr=PIPE)
        # retrieve output streams
        (stdoutdata, stderrdata) = popen.communicate()
        # if pkgin error
        if(stderrdata):
            # remove the line feed
            error = stderrdata[0:-1]
            raise PykginError(error)
        # retrieve output
        output = stdoutdata
        # create a list which contain each packages
        output_list = output.split('\n')
        # remove last element (due to the last \n)
        output_list.pop()

        return output_list

if __name__ == "__main__":
    print __doc__

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

