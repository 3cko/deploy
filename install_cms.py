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

    def checkRoot(self):
        user = os.geteuid()
        if user != 0:
            print "You need to be logged in as root or use sudo to run me"
            sys.exit(0)
        else:
            return True

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
        Extract TAR files to /tmp location
        """
        tar = tarfile.open('/tmp/{0}'.format(self.file_name))
        tar.extractall('/tmp/')
        tar.close()

    def shell(self, command):
        """
        Execute shell commands
        """
        shells = subprocess.Popen(command,
                                 shell=True,
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.PIPE,
                                 )

        output, error = shells.communicate()

    def moveCmsToDestination(self):
        """
        Move the CMS from /tmp/dir to self.destination
        """
        for file in glob.glob('/tmp/{0}/*'.format(self.cms)):
            shutil.move(file,
                        self.destination)

    def findReplace(self, file, find, replace):
        """
        Find and replace strings in place for a text file
        """
        for line in fileinput.FileInput(file, inplace=1):
            line = line.replace(find, replace)
            print line,

    def updateWordpressDBInfo(self):
        """
        Move wp-config-sample.php to wp-config.php
        Update database credentials in wp-config.php
        """
        shutil.move("{0}/wp-config-sample.php".format(self.destination),
                    "{0}/wp-config.php".format(self.destination)
                    )
        file = "{0}/wp-config.php".format(self.destination)
        if self.new_dbname:
            self.findReplace(file, 'database_name_here', self.new_dbname)
        if self.grant_dbuser:
            self.findReplace(file, 'username_here', self.grant_dbuser)
        if self.grant_dbpasswd:
            self.findReplace(file, 'password_here', self.grant_dbpasswd)
        if self.grant_dbhost:
            self.findReplace(file, 'localhost', str(self.grant_dbhost))

    def databaseExecute(self, execute):
        """
        Strings for database execution with self.shell
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
        Create database mysql syntax
        """
        self.databaseExecute("CREATE DATABASE IF NOT EXISTS {0}".format(
                             self.new_dbname))

    def createDatabaseUser(self):
        """
        Grant database user permission to access new database from localhost \
or remote location
        """
        self.databaseExecute(
            "GRANT ALL PRIVILEGES ON {0}.* TO '{1}'@'{2}' \
IDENTIFIED BY '{3}'".format(
                self.new_dbname,
                self.grant_dbuser,
                self.grant_dbhost,
                self.grant_dbpasswd
                ))

    def run(self):
        self.download()
        self.extractTar()
        self.moveCmsToDestination()
        if self.new_dbname:
            self.createDatabase()
        if self.grant_dbuser:
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
                   choices=['wordpress', 'drupal-7.23', 'drupal-6.28'],
                   metavar='CMS',
                   )
    req.add_option('-d', '--destination',
                   help="/full/path/to/destination/dir",
                   metavar="/DESTINATION/DIR",
                   )
    req.add_option('--new-dbname',
                   help="New Database Name",
                   metavar="DBNAME",
                   )
    grants = OptionGroup(parser, "OPTIONAL: DB CRED FOR GRANTING DB USER \
ACCESS TO NEW DB")
    grants.add_option('--grant-dbuser',
                      help="Database User grant access to the specified \
database",
                      metavar="USERNAME",
                      )
    grants.add_option('--grant-dbpasswd',
                      help="Database User password for 'identify by' to the \
specified database",
                      metavar="PASSWORD",
                      )
    grants.add_option('--grant-dbhost',
                      help="Database User host location for access remotely",
                      metavar="USERNAME",
                      default='localhost',
                      )
    dbinfo = OptionGroup(parser, "REQUIRED IF ~/.my.cnf DOES NOT EXIST")
    dbinfo.add_option('--db-user',
                      help="Database username to connect to database server",
                      metavar="USERNAME",
                      )
    dbinfo.add_option('--db-passwd',
                      help="Database user's password to connect to database \
server",
                      metavar="PASSWORD",
                      )
    dbinfo.add_option('--db-host',
                      help="Database host to connect to database server",
                      metavar="USERNAME",
                      default='localhost',
                      )
    parser.add_option_group(req)
    parser.add_option_group(grants)
    parser.add_option_group(dbinfo)
    options, args = parser.parse_args()

    if not options.cms:
        parser.error("A CMS has to be specified")
    if not options.destination:
        parser.error("Destination path for where WordPress is to be added \
needs to be specified")

    # turn optparse instance into a dictionary   
    install = InstallCMS(**vars(options))
    install.checkRoot()
    install.run()
