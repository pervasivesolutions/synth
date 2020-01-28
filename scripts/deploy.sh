#!/bin/bash

ssh pervasive@63.32.112.69 < scripts/run_on_server_deploy.sh

# pervasive ALL= NOPASSWD: /usr/bin/systemctl status cityfibre_synth
# pervasive ALL= NOPASSWD: /usr/bin/systemctl restart cityfibre_synth
# pervasive ALL= NOPASSWD: /usr/bin/systemctl start cityfibre_synth
# pervasive ALL= NOPASSWD: /usr/bin/systemctl stop cityfibre_synth
