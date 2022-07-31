import os
import yaml
import subprocess
import qmfnetop

""" Help program to seutp the ssh copy key.
    Read the setting file and setup the RSA public key login
"""


with open(qmfnetop.QMFNetOp.SETTTINGS_FILE, 'r') as cfg:
    log_cfg = yaml.safe_load(cfg)
    ts = log_cfg.get('STATIONS').split()
    hop = log_cfg.get('hopStation')
    # self.pxes = list(map(lambda x: pxe.Pxe(x, hop), ts))

    for p in ts:
        # cmd = f"ssh -o StrictHostKeyChecking=no {p} exit"
        # result= subprocess.run(cmd.split()).stdout
        cmd = f"ssh-copy-id {p}"
        result= subprocess.run(cmd.split()).stdout

