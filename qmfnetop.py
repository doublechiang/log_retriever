#!/usr/bin/env python3
import subprocess
import os


class QMFNetOp:
    Station  = '192.168.0.81 192.168.0.82 192.168.0.83 192.168.0.84'.split()
    hopStation ='cchiang@192.168.66.28'
    """ QMF network operation
    """
    def querySn(self, sn):
        cmd = "find /RACKLOG/ -type f -name *{}*".format(sn)
        return self.remote(cmd)


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
        cmd = "rm {host}:/tmp/{fn}".format(host=QMFNetOp.hopStation, fn=fn)
        return 
        

    def remote(self, cmd):
        found = []
        for ip in QMFNetOp.Station:
            hopcmd = self.__sshHop(cmd, 'root@{}'.format(ip))
            hopcmd = self.__sshHop(hopcmd, QMFNetOp.hopStation)
            print(subprocess.__file__)
            print(hopcmd)
            try:
                result = subprocess.run(hopcmd.split(), universal_newlines=True, stdout=subprocess.PIPE)
            except Exception as inst:
                print(inst)

            contents = result.stdout.splitlines()
            for r in contents:
                line=dict()
                line['ip']=ip
                line['file']=r
                found.append(line)
                
        return found

    def __sshHop(self, cmd, hop):
        return "ssh {} {}".format(hop, cmd)

if __name__ == "__main__":
    # s= QMFNetOp().remote('find /RACKLOG/ -type f -name ZNH02200016.* ' )
    # QMFNetOp().querySn('ZNH02200016')
    QMFNetOp().scp('192.168.0.81', '/RACKLOG/S2PL_PY/2020/Aug12/ZNH02200016/RUNIN/ZNH02200016.log')
