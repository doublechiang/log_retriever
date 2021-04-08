#!/usr/bin/env python3
import subprocess
import os
import threading
import logging


class QMFNetOp:
    Station  = '192.168.0.81 192.168.0.82 192.168.0.83 192.168.0.84'.split()
    hopStation ='cchiang@192.168.66.28'
    """ QMF network operation
    """
    def querySn(self, sn):
        found = []
        threads = []
        cmd = "find /RACKLOG/ -type f -name *{}* -exec ls -lhgG --time-style=long-iso {{}} +".format(sn)
        for ip in QMFNetOp.Station:
            x=threading.Thread(target=self.remoteJob, args=(found, ip, cmd))
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            thread.join()
        
        return found


    def scp(self, ip, path):
        """ Copy file to a temporary file location
            copy without middle file system.
            estable password less login 
            ssh-copy-id -o ProxyCommand="ssh -W %h:%p cchiang@192.168.66.28" root@192.168.0.84
            scp -o ProxyCommand="ssh -W %h:%p cchiang@192.168.66.28" root@192.168.0.83:[file] /tmp
        """
        
        logging.info("Copy file {} form ip {}".format(path, ip))
        path= path.replace('[', '\[').replace(']', '\]').replace('(', '\(').replace(')', '\)')
        # .replace('(', '\(').replace(')', '\)')
        fn = os.path.basename(path)
        # Copy file to hop station 
        cmd = "scp -o ProxyCommand=\"ssh -W %h:%p {}\" root@{}:'{}' /tmp".format(QMFNetOp.hopStation, ip, path)
        logging.debug(cmd)

        # using subprocess run will have problem when copy filename with brace.
        #result = subprocess.run(cmds, universal_newlines=True, stdout=subprocess.PIPE)
        os.system(cmd)

        return 
        

    def remoteJob(self, found, ip, cmd):
        """ Execute the cmd on the remote server
        """
        hopcmd = self.__sshHop(cmd, 'root@{}'.format(ip))
        hopcmd = self.__sshHop(hopcmd, QMFNetOp.hopStation)
        logging.info(subprocess.__file__)
        logging.debug(hopcmd)
        try:
            result = subprocess.run(hopcmd.split(), universal_newlines=True, stdout=subprocess.PIPE)
        except Exception as inst:
            print(inst)

        contents = result.stdout.splitlines()
        for r in contents:
            line=dict()
            line['ip']=ip
            # parsing ls -l output
            # line['file']=r
            line['size'] = r.split()[2]
            line['date'] = r.split()[3] + ' ' + r.split()[4]
            line['file'] = r.split()[5]
            logging.info(line)
            found.append(line)
        logging.debug("{} done!".format(cmd))
        return
                

    def __sshHop(self, cmd, hop):
        return "ssh {} {}".format(hop, cmd)

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        #logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    pass
    # s= QMFNetOp().remote('find /RACKLOG/ -type f -name ZNH02200016.* ' )
    # QMFNetOp().querySn('ZNH02200016')
    # QMFNetOp().scp('192.168.0.81', '/RACKLOG/S2PL_PY/2020/Aug12/ZNH02200016/RUNIN/ZNH02200016.log')
