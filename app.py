#!/usr/bin/env python3
import os
from flask import Flask, request, redirect, render_template, url_for
from flask import send_file

# local import
import qmfnetop

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'racklog'

@app.route('/', methods=['get', 'post'])
def log_query():
    found = None
    search_lst=dict()
    if request.method == 'POST':
        sn=request.form.get('sn').strip()
        return redirect(url_for('search', sn=sn))
    return  render_template('query.html', found=found, search_lst = search_lst)


@app.route('/query')
@app.route('/query/')
@app.route('/query/<sn>')
def search(sn=None):
    found, error = qmfnetop.QMFNetOp().querySn(sn)
    return render_template('query.html', found=found, error=error)


@app.route('/get_remotef')
def get_remotef():
    ip=request.args['ip']
    fpath=request.args['file']
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
