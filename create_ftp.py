#!/usr/bin/env python

## TO DO:
## CHECK IF USER IS ALREADY PART OF SFTPONLY GROUP

# create user if not exists
import re
import subprocess
import fileinput

class FTP():
    def __init__(self, name):
        self.name = name
        self.group = None

    def scanFile(self, file, string):
        with open(file, 'r') as lines:
            for line in lines:
                match = re.findall('\\b'+string+'\\b', line)
                if len(match) > 0:
                    return True
        return False

    def addField(self, string):
        add = subprocess.Popen(string.split(),
                               stdout = subprocess.PIPE,
                              )
        output, error = add.communicate()

    def checkUser(self):
        return self.scanFile('/etc/passwd', self.name)

    def checkGroup(self):
        return self.scanFile('/etc/group', 'sftponly')

    def createGroup(self):
        self.addField("groupadd sftponly")

    def createUser(self):
        self.addField("useradd -G sftponly -s /bin/false {0}".format(self.name))

    def addGroupToUser(self):
        self.addField("usermod -G sftponly {0}".format(self.name))

    def disableSubsystem(self):
        """
        """
        find = "Subsystem\tsftp\t/usr/libexec/openssh/sftp-server"
        for line in fileinput.FileInput('/etc/ssh/sshd_config.test', inplace=1):
            line = line.replace(find, "#{0}".format(find))
            print line,

    def appendMatchGroup(self):
        """
        """
        subsystem = """
Subsystem     sftp   internal-sftp
Match Group sftponly
    ChrootDirectory %h
    ForceCommand internal-sftp
    AllowTcpForwarding no
"""
        with open('/etc/ssh/sshd_config.test', 'a') as insert:
            insert.write(subsystem)
            insert.close()


if __name__ == '__main__':
    ftp = FTP('testing')
    if not ftp.checkUser():
        if not ftp.checkGroup():
            ftp.createGroup()
        ftp.createUser()
