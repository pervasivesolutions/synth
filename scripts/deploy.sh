#!/bin/bash

ssh pervasive@63.32.112.69 < scripts/run_on_server_deploy.sh

# visudo

# Cmnd_Alias SYNTH_SERVICES = /usr/bin/systemctl status cityfibre_synth,/usr/bin/systemctl start cityfibre_synth,/usr/bin/systemctl stop cityfibre_synth,/usr/bin/systemctl restart cityfibre_synth, /usr/bin/systemctl status comms_synth,/usr/bin/systemctl start comms_synth,/usr/bin/systemctl stop comms_synth,/usr/bin/systemctl restart comms_synth

# pervasive ALL = NOPASSWD: SYNTH_SERVICES

# pervasive ALL= NOPASSWD: /usr/bin/systemctl status cityfibre_synth
# pervasive ALL= NOPASSWD: /usr/bin/systemctl restart cityfibre_synth
# pervasive ALL= NOPASSWD: /usr/bin/systemctl start cityfibre_synth
# pervasive ALL= NOPASSWD: /usr/bin/systemctl stop cityfibre_synth

# LOG FILE ACLS
# view
# getfacl /var/www/synth/synth_logs/cityfibre_synth.log
# set
# setfacl -m u:pervasive:r /var/www/synth/synth_logs/cityfibre_synth.log
