import paramiko
import os
import subprocess as sub
import shlex
from io import StringIO

class testeur:
    def __init__(self):
        self.host="localhost"
        self.user=os.getlogin()
        

    def test(self, commande, result="lignes"):
        """
        teste une commande sur le système et renvoie le contenu
        de la sortie standart et la sortiue d'erreur
        """
        process = sub.Popen(shlex.split(commande), stdout=sub.PIPE, stderr=sub.PIPE)
        out, err = process.communicate()
        stdout = StringIO(out.decode())
        stderr = StringIO(err.decode())
        if result == "lignes":
            return stdout.readlines(), stderr.readlines()
        else:
            return stdout, stderr
        

    def close(self):
        self.host = ""
    

class testeur_ssh(testeur):
    def __init__(self, host, user, key=None):
        self.host = host
        self.user = user
        self.key = key
        
        self.cli = cli = paramiko.client.SSHClient()
        self.cli.set_missing_host_key_policy(paramiko.client.WarningPolicy())
        self.cli.load_system_host_keys()
        if not self.key is None:
            self.cli.connect(hostname=self.host,
                             username=self.user,
                             key_filename=self.key)
        else:
            self.cli.connect(hostname=self.host,
                             username=self.user)


    def close(self):
        self.cli.close()

    def test(self, com, result="lignes"):
        stdin, stdout, stderr = self.cli.exec_command(com)
        if result == "lignes":
            return stdout.readlines(), stderr.readlines()
        else:
            return stdout, stderr

    
