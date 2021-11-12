#!/bin/bash

# You need to manual login first to establish the trusted host.
# With default hop station set to 'cchiang@192.168.66.28'
if [ $# -ne 1 ]; then
    echo "Usage: $0 [user@remote]"; exit 1;
fi
remote=$1
hop_station='cchiang@192.168.66.28'

cmd="ssh ${hop_station} ssh-copy-id ${remote}"
echo $cmd
eval ${cmd}

cmd="ssh-copy-id -o ProxyCommand=\"ssh -W %h:%p ${hop_station}\" ${remote}"
echo $cmd
eval ${cmd}
