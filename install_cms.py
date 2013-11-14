#!/usr/bin/env python

import urllib
import tarfile
import os
import shutil
import glob


class InstallCMS():
    def __init__(self, cms, destination):
        self.cms = cms.lower()
        self.destination = destination
        self.file_name = None
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

    def moveCmsToDestination(self):
        """
        """
        for file in glob.glob('/tmp/{0}/*'.format(self.cms)):
            print file
            shutil.move(file,
                        self.destination)

    def install(self):
        pass

    def createDatabase(self):
        pass

    def createDatabaseUser(self):
        pass

    def shell(self):
        pass

    def run(self):
        self.download()
        self.extractTar()
        self.moveCmsToDestination()

if __name__ == '__main__':
    install = InstallCMS('wordpress', '/var/www/vhosts/testing')
    install.run()
