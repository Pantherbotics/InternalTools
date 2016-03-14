#!/bin/bash
mkdir /robotics/git/$@
cd /robotics/git/$@
git init --bare --shared=true
touch git-daemon-export-ok
echo "Creating remote:" $@
echo '{"name":"'$@'"}'
curl -u 'pantherbotics3863:3863nphs' https://api.github.com/orgs/Pantherbotics/repos -d '{"name":"'$@'"}'
echo 'setting hub'
git remote add hub https://pantherbotics3863:3863nphs@github.com/Pantherbotics/$@
cd ../
chmod -R 777 $@

