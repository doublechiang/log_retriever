# log_retriever
Retriever the logs from all server.

# Setup
rsync all of server logs to local server.
ssh-keygen -t rsa
ssh-copy-id user@target

# Development
$ export FLASK_ENV=development

# run the server
$ export FLASK_APP=hello.py
$ python -m flask run
