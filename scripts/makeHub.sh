#!/bin/bash
cred=$(</robotics/gitCred.txt)
mkdir /robotics/git/$@
cd /robotics/git/$@
git init --bare --shared=true
touch git-daemon-export-ok
echo "Creating remote:" $@
echo '{"name":"'$@'"}'
curl -u "$cred" https://api.github.com/orgs/Pantherbotics/repos -d '{"name":"'$@'"}'
echo 'setting hub'
git remote add hub https://$cred@github.com/Pantherbotics/$@
cd ../
chmod -R 777 $@

