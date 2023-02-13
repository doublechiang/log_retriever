#!/usr/bin/env python3
import os
from flask import Flask, request, redirect, render_template, url_for, jsonify
from flask import send_file
import yaml
import json
from datetime import datetime

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
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            with open('locations.txt', 'r') as f:
                data = f.read()
                records = json.loads(data)
                try:
                    if (records[sn]):
                        return jsonify(records[sn])
                except KeyError:
                    return jsonify({'Error': 'Data not found'})
        else:
            if SEARCH_SIBLING:
                record = get_sn_loc(sn)
                if (record):
                    found, error = qmfnetop.QMFNetOp().querySnFromBackupSiblings(sn, record['location'])
                else:
                    found, error = qmfnetop.QMFNetOp().querySnFromBackupSiblings(sn, None)
            else:
                found, error = qmfnetop.QMFNetOp().querySnFromBackup(sn)
            if (found):
                location = found[0]['ip']
                put_sn(sn, location)
                
    error = logErrors(error)
                
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

#--------------------

# @app.route("/queryPut/<sn>/<location>", methods=["GET","PUT"])
def put_sn(sn,location):
    # if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        with open('locations.txt', 'r') as f:
                data = f.read()
        records = json.loads(data)
        if not data:
            records = [record]
        else:    
            records[sn] = json.loads (f'{{"sn": "{sn}","location": "{location}"}}')
        with open('locations.txt', 'w') as f:
                f.write(json.dumps(records, indent=2))
        return records[sn]


def get_sn_loc(sn):
    with open('locations.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        try:
            if (records[sn]):
                return records[sn]
        except KeyError:
            pass
        return None

def logErrors(error):
    if (len(error)>0):
        with open('logs/errors.txt', 'a') as f:
            for entry in error:
                f.write(f"{datetime.now()} : {entry}\n")
        error = []
    return error


if __name__ == '__main__':
    app.run(port=5000)
