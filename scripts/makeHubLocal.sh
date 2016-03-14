#!/bin/bash
mkdir /robotics/git/$@
cd /robotics/git/$@
git init --bare --shared=true
touch git-daemon-export-ok
touch no-github-sync
echo "Creating remote:" $@
echo '{"name":"'$@'"}'
echo 'setting hub'
git remote add hub https://pantherbotics3863:3863nphs@github.com/Pantherbotics/$@
cd ../
chmod -R 777 $@

