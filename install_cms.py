#!/usr/bin/env python

# cms, destination, 
# GRANT: new_dbname, a_dbuser, host_to_connect_from, dboasswd
# CREATE: current dbuser, db pass, host, create db_name
#
#
#
#
#

import urllib
import tarfile
import os
import shutil
import glob
import subprocess
import fileinput


class InstallCMS():
    def __init__(self, cms, destination, new_dbname, grant_dbuser=None, 
                 grant_dbpasswd=None, grant_dbhost=None, db_user=None,
                 db_passwd=None, db_host=None):
        self.cms = cms.lower()
        self.destination = destination
        self.file_name = None
        self.db_user = db_user
        self.db_passwd = db_passwd
        self.db_host = db_host
        self.new_dbname = new_dbname
        self.grant_dbuser = grant_dbuser
        self.grant_dbpasswd = grant_dbpasswd
        self.grant_dbhost = grant_dbhost

        self.list_of_cms = {
                'WordPress': 
                    'http://wordpress.org/latest.tar.gz',
                'drupal-7.23': 
                    'http://ftp.drupal.org/files/projects/drupal-7.23.tar.gz',
                'drupal-6.28': 
                    'http://ftp.drupal.org/files/projects/drupal-6.28.tar.gz',
                            }

    def download(self):
        """
        Downloads the correct CMS file
        """
        for cms in self.list_of_cms:
            if cms.lower() == self.cms:
                self.file_name = self.list_of_cms[cms].split('/')[-1]
                urllib.urlretrieve(self.list_of_cms[cms],
                                   '/tmp/{0}'.format(self.file_name))

    def extractTar(self):
        """
        Extract TAR files to destination location
        """
        tar = tarfile.open('/tmp/{0}'.format(self.file_name))
        tar.extractall('/tmp/')
        tar.close()

    def shell(self, command):
        """
        """
        shells = subprocess.Popen(command,
                                 shell=True,
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.PIPE,
                                 )

        output, error = shells.communicate()

    def moveCmsToDestination(self):
        """
        """
        for file in glob.glob('/tmp/{0}/*'.format(self.cms)):
            print file
            shutil.move(file,
                        self.destination)

    def findReplace(self, file, find, replace):
        """
        """
        for line in fileinput.FileInput(file, inplace=1):
            line = line.replace(find, replace)
            print line,

    def updateWordpressDBInfo(self):
        """
        """
        shutil.move("{0}/wp-config-sample.php".format(self.destination),
                    "{0}/wp-config.php".format(self.destination)
                    )
        file = "{0}/wp-config.php".format(self.destination)
        self.findReplace(file, 'database_name_here', self.new_dbname)
        self.findReplace(file, 'username_here', self.grant_dbuser)
        self.findReplace(file, 'password_here', self.grant_dbpasswd)
        self.findReplace(file, 'localhost', self.db_host)

    def databaseExecute(self, execute):
        """
        """
        if not self.db_user \
           or not self.db_passwd \
           or not self.db_host:
            command = 'mysql -e"{0}"'.format(execute)
        elif not self.db_host:
            command = 'mysql -u{0} -p{1} -e"{2}"'.format(
                        self.db_user,
                        self.db_passwd,
                        execute)
        else:

            command = 'mysql -u{0} -p{1} -h{2} -e"{3}"'.format(
                        self.db_user,
                        self.db_passwd,
                        self.db_host,
                        execute)

        self.shell(command)

    def createDatabase(self):
        """
        """
        self.databaseExecute("CREATE DATABASE {0}".format(self.new_dbname))

    def createDatabaseUser(self):
        """
        """
        self.databaseExecute(
            "GRANT ALL PRIVILEGES ON {0}.* TO '{1}'@'{2}' IDENTIFIED BY '{3}'".format(
                self.new_dbname,
                self.grant_dbuser,
                self.grant_dbhost,
                self.grant_dbpasswd
                ))

    def run(self):
        self.download()
        self.extractTar()
        self.moveCmsToDestination()
        self.createDatabase()
        self.createDatabaseUser()
        if 'wordpress' in self.cms:
            self.updateWordpressDBInfo()

if __name__ == '__main__':
    from optparse import OptionParser, OptionGroup
    parser = OptionParser()
    req = OptionGroup(parser, "REQUIRED")
    req.add_option('-c', '--cms',
                   help="CMS to Install",
                   type='choice',
                   choices=['wordpress'],
                   metavar='CMS',
                   )
    req.add_option('-w', '--web-root',
                   help="/full/path/to/web/root",
                   metavar="WEB ROOT",
                   )
    parser.add_option_group(req)


    install = InstallCMS('wordpress', '/var/www/vhosts/testing', 'foobar3',
                         grant_dbuser='foo2',
                         grant_dbpasswd='rawr',
                         grant_dbhost='localhost')
    install.run()
    #install.createDatabase()
    #install.createDatabaseUser()
