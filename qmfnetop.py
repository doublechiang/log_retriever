#!/usr/bin/env python3
import subprocess
import os
import threading
import logging
import yaml
from datetime import datetime
import queue

import station


class QMFNetOp:
    SETTTINGS_FILE='settings.yml'
    """ QMF network operation
    """
    def querySn(self, sn):
        """ parameter SN to query
            return the list of found and the error
        """
        threads = []
        found = []
        error = []
        # collect thread call request from quque
        out_que = queue.Queue()

        if sn is None:
            return found, error
        # ls -1rt
        # -t     sort by modification time
        cmd = "find /RACKLOG/ -type f -iname *{}* -exec ls -tlhgG --time-style=long-iso {{}} +".format(sn)
        for p in self.pxes:
            x=threading.Thread(target=p.find_file, args=(cmd, out_que))
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            thread.join()

        while not out_que.empty():
            line = out_que.get()
            if type(line) is subprocess.CalledProcessError:
                error.append(line)
            else:
                found.append(line)

        # The search result append into the list by multiple thread.
        found.sort(reverse=True, key=lambda d: datetime.strptime(d['date'], "%Y-%m-%d %H:%M"))
        return found, error

    def querySnFromBackup(self, sn):
        """ Backup all the logs on /data partition 
            root cronjob and have updatedb /var/lib/mlocate/data.db run every 5 minutes
            We can use locate to do a quick search
        """
        cmd = f"ls -tlhgGd --time-style=long-iso `locate -d /data/locate.db -i {sn}` | grep \'^-'"
        error = []
        result = []
        try:
            result = subprocess.check_output(cmd, shell=True).decode('utf-8').splitlines()
        except subprocess.CalledProcessError as e:
            logging.error(e)
            error.append(e)

        found=[]
        error=[]
        for line in result:
            rec=dict()
            rec['ip']='local'
            # parsing ls -l output
            # line['file']=r
            rec['size'] = line.split()[2]
            rec['date'] = line.split()[3] + ' ' + line.split()[4]
            rec['file'] = line.split()[5]
            found.append(rec)
        return found, error

    def querySnFromBackupSiblings(self, sn):
        """ Backup all the logs on /data partition 
            root cronjob and have updatedb /var/lib/mlocate/data.db run every 5 minutes
            We can use locate to do a quick search
            Search through each of the Backup Siblings
        """
        threads = []
        found = []
        error = []
        # collect thread call request from quque
        out_que = queue.Queue()

        if sn is None:
            return found, error
        # ls -1rt
        # -t     sort by modification time
        cmd = f"ls -tlhgGd --time-style=long-iso `locate -d /data/locate.db -i {sn}` | grep \'^-'"
        for r in self.racklogs:
            x=threading.Thread(target=r.find_file, args=(cmd, out_que))
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            thread.join()

        while not out_que.empty():
            line = out_que.get()
            if type(line) is subprocess.CalledProcessError:
                error.append(line)
            else:
                found.append(line)

        # The search result append into the list by multiple thread.
        found.sort(reverse=True, key=lambda d: datetime.strptime(d['date'], "%Y-%m-%d %H:%M"))
        return found, error


    def scp(self, ip, path, dest):
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

        # Locate the PXE instance
        for p in self.pxes:
            if ip in p.__str__():
                p.scp(path, dest)
                break
        return

    def locate_men(self, sn=None):
        if sn is None:
            return None, None

        found, search_lst = self.querySn(sn)
        # Get first file and download the content.
        f = found [0]
        path = f.get('file')
        self.scp(f.get('ip'), path, '/tmp')
        fname = os.path.basename(path)
        cmd = f"grep 'section_type: memory error' /tmp/{fname} -B 1"
        try:
            output = subprocess.check_output(cmd, shell=True, universal_newlines = False).decode('utf-8').splitlines()
        except:
            return ["No trouble found"], []
        return output, []


    def __init__(self): 
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.DEBUG)

        with open(QMFNetOp.SETTTINGS_FILE, 'r') as cfg:
            log_cfg = yaml.safe_load(cfg)
            ts = log_cfg.get('PXE_STATIONS').split()
            rs = log_cfg.get('RACKLOG_STATIONS').split()
            hop = log_cfg.get('hopStation')
            self.pxes = list(map(lambda x: station.Station(x, hop), ts))
            self.racklogs = list(map(lambda x: station.Station(x, hop), rs))

if __name__ == "__main__":
    pass
    # s= QMFNetOp().remote('find /RACKLOG/ -type f -name ZNH02200016.* ' )
    # QMFNetOp().querySn('B98340412317603B')
    # QMFNetOp().scp('192.168.0.81', '/RACKLOG/S2PL_PY/2020/Aug12/ZNH02200016/RUNIN/ZNH02200016.log')
    q = QMFNetOp()
    print(q.hop, q.ts)
