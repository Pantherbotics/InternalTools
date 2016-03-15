#!/bin/bash
#This will update the internal production branch with the master branch
echo "Switching to production"
cd /robotics/services/internalTools
git checkout production
echo "Fetching from Master"
git pull origin master

