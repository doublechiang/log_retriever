#!/usr/bin/env python3
import os
from flask import Flask, request, render_template, url_for
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
        sn=request.form.get('sn')
        found, search_lst = qmfnetop.QMFNetOp().querySn(sn)
    return  render_template('query.html', found=found, search_lst = search_lst)

@app.route('/get_remotef')
def get_remotef():
    ip=request.args['ip']
    fpath=request.args['file']
    qmfnetop.QMFNetOp().scp(ip, fpath)
    fn=os.path.basename(fpath)
    return send_file("/tmp/{}".format(fn), as_attachment=True)

    

if __name__ == '__main__':
    app.run(port=5000)
