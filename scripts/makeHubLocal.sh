#!/bin/bash
cred=$(</robotics/gitCred.txt)
mkdir /robotics/git/$@
cd /robotics/git/$@
git init --bare --shared=true
touch git-daemon-export-ok
touch no-github-sync
echo "Creating remote:" $@
echo '{"name":"'$@'"}'
echo 'setting hub'
git remote add hub https://$cred@github.com/Pantherbotics/$@
cd ../
chmod -R 777 $@

