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


class VHost():
    def __init__(self, domain, service, document_root):
        self.domain = domain
        self.service = service
        self.file = None
        self.document_root = document_root

        self.vhosts = {'httpd': 'https://raw.github.com/3cko/deploy/master/conf/httpd.conf',
                    'apache2': 'https://raw.github.com/3cko/deploy/master/conf/httpd.conf',}
        self.paths = {'httpd': '/etc/httpd/vhost.d',
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
        user = os.geteuid()
        if user != 0:
            print "You must be logged in as root or use sudo to run me"
            sys.exit(0)
        else:
            return True

    def getVirtualHost(self):
        """
        download appropriate vhost conf from git
        """

        print self.file
        self.file = "{0}/{1}.conf".format(self.paths[self.service], self.domain)
        # get vhost template from github
        vhost_file = urllib.urlretrieve(
                        self.vhosts[self.service],
                        self.file)

    def updateTemplate(self, file, find, replace):
        for line in fileinput.FileInput(file, inplace=1):
            line = line.replace(find, replace)
            print line,

    def updateVhostWithDocRoot(self):
        path = "{0}/{1}".format(self.document_root, self.domain)
        self.validateDir(path)
        self.updateTemplate(self.file, '/path/to/doc/root', self.document_root)

    def updateVhostWithDomain(self):
        self.updateTemplate(self.file, 'example.com', self.domain)

    def updateVhostWithGzip(self):
        self.updateTemplate(self.file, '##GZIP##', '')

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

            if self.service == 'apache2':
                import subprocess
                enable = subprocess.Popen(['a2ensite', 
                                           '{0}.conf'.format(self.domain)
                                           ],
                                          stdout=subprocess.PIPE,
                                          )
                output, err = enable.communicate()
                print output
                print err

            

if __name__ == '__main__':
    from optparse import OptionParser, OptionGroup
    parser = OptionParser()
    group = OptionGroup(parser, "REQUIRED")
    group.add_option('-d', '--domain',
                      help="DOMAIN for the new VirtualHost",
                      metavar="DOMAIN",
                      )
    group.add_option('-s', '--service',
                      help="Web service the virtualhost is for: httpd, apach2",
                      type='choice',
                      choices=['httpd', 'apache2'],
                      metavar='WEB SERVICE',
                      )
    parser.add_option('--docroot',
                      help="Domains Document Root directory",
                      metavar='DOCUMENT ROOT',
                      default='/var/www/vhosts',
                      )
    parser.add_option('--gzip',
                      help="Enable GZIP compression in the virtualhost",
                      action='store_true',
                      )
                      
    parser.add_option_group(group)
    options, args = parser.parse_args()

    if not options.service:
        parser.error("WEB SERVICE not specified")
    if not options.domain:
        parser.error("DOMAIN not specified")
    
    vhost = VHost(options.domain, options.service, options.docroot)
    vhost.run()
    if options.gzip:
        vhost.updateVhostWithGzip()

# ensure root or sudo user
# take arguments
# check if directory of vhosts exists
# create if not
# download vhost file
# find/replace example.com with domain name
# create document root
# add to sites-enabled if nginx/apache2
# restart service.
