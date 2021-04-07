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
        """

        fn = os.path.basename(path)
        # Copy file to hop station 
        cmd = "scp root@{}:{} /tmp".format(ip, path)
        cmd = self.__sshHop(cmd, QMFNetOp.hopStation)
        result = subprocess.run(cmd.split(), universal_newlines=True, stdout=subprocess.PIPE)

        # copy from hop station to local station
        cmd = "scp {}:/tmp/{} /tmp".format(QMFNetOp.hopStation, fn)
        result = subprocess.run(cmd.split(), universal_newlines=True, stdout=subprocess.PIPE)

        # remove the temp file from hop station
        cmd = "ssh {host} rm /tmp/{fn}".format(host=QMFNetOp.hopStation, fn=fn)
        # TODO, add thread here to speed up process
        result = subprocess.run(cmd.split(), universal_newlines=True, stdout=subprocess.PIPE)
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

if __name__ == "__main__":
    pass
    # s= QMFNetOp().remote('find /RACKLOG/ -type f -name ZNH02200016.* ' )
    # QMFNetOp().querySn('ZNH02200016')
    # QMFNetOp().scp('192.168.0.81', '/RACKLOG/S2PL_PY/2020/Aug12/ZNH02200016/RUNIN/ZNH02200016.log')
