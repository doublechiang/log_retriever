#!/usr/bin/env python3
import os
from flask import Flask, request, render_template, url_for
from flask import send_file

# local import
import qmfnetop

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = 'racklog'

@app.route('/')
def log_query():
    return  render_template('query.html')

@app.route('/get_remotef')
def get_remotef():
    ip=request.args['ip']
    fpath=request.args['file']
    qmfnetop.QMFNetOp().scp(ip, fpath)
    fn=os.path.basename(fpath)
    return send_file("/tmp/{}".format(fn), as_attachment=True)

@app.route('/qsn', methods=['post'])
def qsn():
    if request.method == 'POST':
        sn=request.form.get('sn')
        found = qmfnetop.QMFNetOp().querySn(sn)
        return render_template('query.html', found=found)
     

if __name__ == '__main__':
    app.run(port=5000)
