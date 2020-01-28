#!/bin/bash

cd /var/www/synth/current
git pull
rm -rf /var/www/synth/current/synth_accounts
rm -rf /var/www/synth/current/synth_logs

sudo systemctl restart cityfibre_synth
sudo systemctl status cityfibre_synth
