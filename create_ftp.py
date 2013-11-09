#!/usr/bin/env python

# create user if not exists
import re
import subprocess
import fileinput


class FTP():
    def __init__(self, name):
        self.name = name
        self.group = None
        self.array = []

    def scanFile(self, file, string, array=None):
        """
        open specific file and find exact matches of $string, returns boolean
        """
        self.array = []
        with open(file, 'r') as lines:
            for line in lines:
                match = re.findall('\\b'+string+'\\b', line)
                if len(match) > 0:
                    if array:
                        self.array.append(match[0])
                    return True
        return False

    def addField(self, string):
        """
        main function for creating for executing shell commands
        accepts string only format, eg: 
        'useradd -G sftponly -s /bin/false username'
        """
        add = subprocess.Popen(string.split(),
                               stdout = subprocess.PIPE,
                              )
        output, error = add.communicate()

    def checkUser(self):
        """
        returns boolean if user exists
        """
        return self.scanFile('/etc/passwd', self.name)

    def checkGroup(self):
        """
        returns boolean if group exists
        """
        return self.scanFile('/etc/group', 'sftponly')

    def checkMatchGroup(self):
        """
        returns boolean if sftponly match group has been created
        """
        self.scanFile('/etc/ssh/sshd_config.test',
                      "Subsystem\s+sftp\s+internal-sftp", array=1)
        if len(self.array) > 0:
            return True
        return False

    def createGroup(self):
        """
        creates sftponly group
        """
        self.addField("groupadd sftponly")

    def createUser(self):
        """
        creates ftp user
        """
        self.addField("useradd -G sftponly -s /bin/false {0}".format(self.name))

    def addGroupToUser(self):
        """
        adds user to group, sftponly
        """
        self.addField("usermod -G sftponly {0}".format(self.name))

    def disableDefaultSubsystem(self):
        """
        disables default Subsystem in /etc/ssh/sshd_config
        """
        self.scanFile('/etc/ssh/sshd_config.test',
                      "Subsystem\s+sftp\s+/usr/libexec/openssh/sftp-server", array=1)
        find = self.array[0]
        for line in fileinput.FileInput('/etc/ssh/sshd_config.test', inplace=1):
            line = line.replace(find, "#{0}".format(find))
            print line,

    def appendMatchGroup(self):
        """
        appends Match Group sftponly fields to /etc/ssh/sshd_config
        """
        subsystem = """
Subsystem   sftp    internal-sftp
Match Group sftponly
    ChrootDirectory %h
    ForceCommand internal-sftp
    AllowTcpForwarding no
"""
        with open('/etc/ssh/sshd_config.test', 'a') as insert:
            insert.write(subsystem)
            insert.close()

    def run(self):
        """
        does all of the magic
        """
        if not self.checkUser():
            if not self.checkGroup():
                self.createGroup()
            self.createUser()
        else:
            self.addGroupToUser()
        if not self.checkMatchGroup():
            self.disableDefaultSubsystem()
            self.appendMatchGroup()


if __name__ == '__main__':
    ftp = FTP('testing')
    ftp.run()
