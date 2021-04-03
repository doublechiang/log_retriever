import subprocess
import os


class QMFNetOp:
    Station  = [
        {
        'ip': '192.168.0.81'
        },
        {
        'ip': '192.168.0.82'
        },
        {
        'ip': '192.168.0.83'
        },
        {
        'ip': '192.168.0.84'
        }
    ]
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
        cmd = self.__sshHop(cmd, 'cchiang@192.168.66.28')
        result = subprocess.run(cmd.split(), universal_newlines=True, stdout=subprocess.PIPE)

        # copy from hop station to local station
        cmd = "scp cchiang@192.168.66.28:/tmp/{} /tmp".format(fn)
        result = subprocess.run(cmd.split(), universal_newlines=True, stdout=subprocess.PIPE)

        # remove the temp file from hop station
        cmd = "rm cchiang@192.168.66.28:/tmp/{}".format(fn)
        return 
        

    def remote(self, cmd):
        found = []
        for s in QMFNetOp.Station:
            ip = s.get('ip')
            hopcmd = self.__sshHop(cmd, 'root@{}'.format(ip))
            hopcmd = self.__sshHop(hopcmd, 'cchiang@192.168.66.28')
            print(hopcmd)
            result = subprocess.run(hopcmd.split(), universal_newlines=True, stdout=subprocess.PIPE)

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