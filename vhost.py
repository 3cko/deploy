#!/usr/bin/env python

# Create new vhost conf for any distro
# detect web service
# add gzip

#modules
import urllib
import fileinput
import os
import errno
import pwd
import sys
#import argparse


class VHost():
    def __init__(self, domain, service):
        self.domain = domain
        self.service = service
        self.file = None
        self.documentRoot = '/var/www/vhosts'

        vhosts = {'httpd': 'https://raw.github.com/3cko/deploy/master/conf/httpd.conf',
                  'apache2': 'http://',}
        paths = {'httpd': './test',
                 'apache2': '/etc/apache2/sites-available',}

    def detectWebService(self):
        """
        Check for apache2, httpd, nginx
        """
        pass

    def validateDir(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def checkUser(self):
        user = pwd.getpwuid(os.getuid()).pw_name
        if user is not 'root':
            print "You must be logged in as root or use sudo to run me"
            sys.exit(0)
        else:
            return True

    def getVirtualHost(self):
        """
        download appropriate vhost conf from git
        """

        self.file = "{0}/{1}.conf".format(self.paths[self.service], self.domain)

        # check if vhost dir exists, if not create it
        #self.validateDir(self.paths[self.service])

        # get vhost template from github
        vhost_file = urllib.urlretrieve(
                        self.vhosts[self.service],
                        file)
        
        # find and replace example.com with domain name in vhost template
        # self.updateTemplateWithDomain(self.domain, file)

    def updateTemplate(self, file, find, replace):
        #f = open(file, 'w')
        for line in fileinput.FileInput(file, inplace=1):
            line = line.replace(find, replace)
            print line,

    def updateVhostWithDocRoot(self):
        self.validateDir(self.documentRoot)
        self.updateTemplate(self.file, '/path/to/doc/root', self.documentRoot)

    def updateVhostWithDomain(self):
        self.updateTemplate(self.file, 'example.com', self.domain)

    def run(self):
        """
        create a vhost
        """
        if self.checkUser():
            # ensure service path exists for vhosts
            self.validateDir(self.paths[self.service])
            
            # get vhost file and update paths
            self.getVirtualHost()
            
            # replace example.com to self.domain
            self.updateVhostWithDomain()

            # create document root for domain
            self.updateVhostWithDocRoot()
            
            #
    

if __name__ == '__main__':
    vhost = VHost('foo.com', 'httpd')
    vhost.run()
    #print vhost.checkUser()
    #vhost.getVirtualHost('httpd')

# ensure root or sudo user
# take arguments
# check if directory of vhosts exists
# create if not
# download vhost file
# find/replace example.com with domain name
# create document root
# add to sites-enabled if nginx/apache2
# restart service.
