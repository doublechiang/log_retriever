#!/usr/bin/env python3
import os
from flask import Flask, request, redirect, render_template, url_for
from flask import send_file
import yaml

# local import
import qmfnetop

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'racklog'

SETTTINGS_FILE='settings.yml'

with open(SETTTINGS_FILE, 'r') as cfg:
        log_cfg = yaml.safe_load(cfg)
        SEARCH_SIBLING = log_cfg.get('SEARCH_SIBLING')
        RACKLOG_STATIONS = log_cfg.get('RACKLOG_STATIONS').split()
LOCAL = ['local']
for racklog in RACKLOG_STATIONS:
    LOCAL.append(racklog.split('@')[1])


@app.route('/')
def log_query():
    return redirect(url_for('search'))


@app.route('/query')
@app.route('/query/', methods=['get', 'post'])
@app.route('/query/<sn>')
def search(sn=None):
    global SEARCH_SIBLING
    
    found = None
    error = []
    if request.method == 'POST':
        sn=request.form.get('sn').strip()
        return redirect(url_for('search')+sn)

    if sn is not None:
        if SEARCH_SIBLING:
            pass
            found, error = qmfnetop.QMFNetOp().querySnFromBackupSiblings(sn)
        else:
            found, error = qmfnetop.QMFNetOp().querySnFromBackup(sn)
    return render_template('query.html', found=found, error=error)

@app.route('/queryDist')
@app.route('/queryDist/', methods=['get', 'post'])
@app.route('/queryDist/<sn>')
def searchDist(sn=None):
    if request.method == 'POST':
        sn=request.form.get('sn').strip()
        return redirect(url_for('searchDist')+sn)

    found, error = qmfnetop.QMFNetOp().querySn(sn)
    return render_template('query.html', found=found, error=error)



@app.route('/get_remotef')
def get_remotef():
    global LOCAL
    ip=request.args['ip']
    fpath=request.args['file']
    if ip in LOCAL:
        if fpath.startswith('/data'):
            return send_file(fpath, as_attachment=True)
        else:
            return 'Do not try to tamper it.'

    qmfnetop.QMFNetOp().scp(ip, fpath, '/tmp')
    fn=os.path.basename(fpath)
    return send_file("/tmp/{}".format(fn), as_attachment=True)

@app.route('/memloc/', methods=['get', 'post'])
def memloc():
    found = []
    search_lst = []
    if request.method == 'POST':
        sn=request.form.get('sn')
        return redirect(url_for('memloc_sn', sn=sn))
    return render_template('mem_locator.html', found=found, search_lst=search_lst)


@app.route('/memloc/<sn>')
def memloc_sn(sn=None):
    found, search_lst = qmfnetop.QMFNetOp().locate_men(sn)
    return render_template('mem_locator.html', found=found, search_lst=search_lst)


if __name__ == '__main__':
    app.run(port=5000)
