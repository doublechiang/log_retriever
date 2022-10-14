from cmath import e
import logging
import subprocess
import queue
import os

class Pxe:
    def cmd(self, cmd):
        """ @brief Execute the cmd and return the output of result
            @return list if the files or the exception
        """
        remote_cmd = f"ssh {self.hostn} {cmd}"
        if self.hop is not None:
            remote_cmd = f"ssh {self.hop} {remote_cmd}"
        logging.debug("Running command {}, hop:".format(remote_cmd, self.hop))
        try:
            result = subprocess.run(remote_cmd.split(), universal_newlines=True, stdout=subprocess.PIPE, check=True)
        except Exception as error:
            # CalledProcesError
            logging.error(error)
            return error

        return result.stdout.splitlines()

    def find_file(self, cmd, out_que:queue.Queue):
        """ This is thread function, use a global queue to transfer the result 
        """
        contents = self.cmd(cmd)

        if type(contents) is subprocess.CalledProcessError:
            out_que.put(contents)
            return

        for r in contents:
            line=dict()
            line['ip']=self.hostn.split('@')[1]
            # parsing ls -l output
            # line['file']=r
            line['size'] = r.split()[2]
            line['date'] = r.split()[3] + ' ' + r.split()[4]
            line['file'] = r.split()[5]
            logging.debug(f"file:{line}")
            out_que.put(line)
        return

    def scp(self, source, dest):
        """ copy the file, support a hop station, need password less login.
            ssh-copy-id -o ProxyCommand="ssh -W %h:%p cchiang@192.168.66.28" root@192.168.0.84
            scp -o ProxyCommand="ssh -W %h:%p cchiang@192.168.66.28" root@192.168.0.83:[file] /tmp
        """
        cmd = "scp {}:'{}' {}".format(self.hostn, source, dest)
        if self.hop is not None:
            cmd = "scp -o ProxyCommand=\"ssh -W %h:%p {}\" {}:'{}' {}".format(self.hop, self.hostn, source, dest)
        logging.debug(cmd)

        # using subprocess run will have problem when copy filename with brace.
        #result = subprocess.run(cmds, universal_newlines=True, stdout=subprocess.PIPE)
        os.system(cmd)

    def __init__(self, hostn, hop=None):
        self.hop = hop
        self.hostn = hostn

    def __str__(self):
        return f"{self.hostn}"
    