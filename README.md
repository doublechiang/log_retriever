# log_retriever
Search/Retriever the logs from all server.

# Setup
Set up all the remote server with ssh key login
ssh-keygen -t rsa
ssh-copy-id user@target

# Development
$ export FLASK_APP=app.py (app.py is the default app, so it's not required to set this command.)
$ export FLASK_ENV=development

# run the server
$ python -m flask run

# Deployment with Apache wsgi
$ yum install python-flask
